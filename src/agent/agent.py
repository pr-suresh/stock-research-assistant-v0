"""
Stock Research Agent using LangGraph.

This module implements a multi-step reasoning agent that can:
1. Plan which tools to use
2. Execute tools in sequence
3. Synthesize results into coherent answers
"""

import logging
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

from .config import get_config
from .tools import get_phase1_tools, get_all_tools
from .prompts import AGENT_SYSTEM_PROMPT
from .cache import get_cache

logger = logging.getLogger(__name__)


# ============================================================================
# Agent State
# ============================================================================


class AgentState(TypedDict):
    """State that flows through the agent graph."""

    # User input
    query: str

    # Conversation history
    messages: List[Any]

    # Tool execution results
    tool_results: List[Dict[str, Any]]

    # Final answer
    answer: Optional[str]

    # Metadata
    iteration: int
    reasoning_steps: List[str]
    tools_used: List[str]
    start_time: float
    cache_hit: bool


# ============================================================================
# Stock Research Agent
# ============================================================================


class StockResearchAgent:
    """
    Main agent class for stock research with multi-step reasoning.

    Uses LangGraph for state management and tool orchestration.
    """

    def __init__(self, use_all_tools: bool = False):
        """
        Initialize the agent.

        Args:
            use_all_tools: If True, use all tools (including placeholders).
                          If False, use only Phase 1 tools (echo only).
        """
        self.config = get_config()
        self.cache = get_cache()

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.config.openai_model,
            temperature=self.config.openai_temperature,
            max_tokens=self.config.openai_max_tokens,
            openai_api_key=self.config.openai_api_key,
        )

        # Select tools based on phase
        self.tools = get_all_tools() if use_all_tools else get_phase1_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.tool_executor = ToolExecutor(self.tools)

        # Build the agent graph
        self.graph = self._build_graph()

        logger.info(
            f"StockResearchAgent initialized with {len(self.tools)} tools "
            f"(use_all_tools={use_all_tools})"
        )

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine.

        Flow:
            START → should_continue → call_tools → should_continue → END
        """
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("agent", self._call_agent)
        workflow.add_node("tools", self._execute_tools)

        # Set entry point
        workflow.set_entry_point("agent")

        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            },
        )

        # After tools, go back to agent
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    def _call_agent(self, state: AgentState) -> AgentState:
        """
        Agent reasoning step - decides what to do next.

        Args:
            state: Current agent state

        Returns:
            Updated state with agent's decision
        """
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)

        # Log reasoning if enabled
        if self.config.log_reasoning_steps and response.content:
            state["reasoning_steps"].append(f"Agent: {response.content}")
            logger.info(f"Agent reasoning: {response.content}")

        # Update state
        state["messages"].append(response)
        state["iteration"] += 1

        return state

    def _execute_tools(self, state: AgentState) -> AgentState:
        """
        Execute tools requested by the agent.

        Args:
            state: Current agent state

        Returns:
            Updated state with tool results
        """
        last_message = state["messages"][-1]

        # Execute each tool call
        tool_calls = getattr(last_message, "tool_calls", [])
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_input = tool_call["args"]

            logger.info(f"Executing tool: {tool_name} with input: {tool_input}")

            # Execute tool
            result = self.tool_executor.invoke(tool_call)

            # Store result
            state["tool_results"].append(
                {"tool": tool_name, "input": tool_input, "result": result}
            )

            # Track tools used
            if tool_name not in state["tools_used"]:
                state["tools_used"].append(tool_name)

            # Log reasoning
            if self.config.log_reasoning_steps:
                state["reasoning_steps"].append(
                    f"Tool {tool_name}: {str(result)[:100]}..."
                )

        # Add tool results to messages
        from langchain_core.messages import ToolMessage

        for tool_call in tool_calls:
            # Find matching result
            matching_results = [
                r
                for r in state["tool_results"]
                if r["tool"] == tool_call["name"]
                and r["input"] == tool_call["args"]
            ]
            if matching_results:
                result = matching_results[-1]["result"]
                state["messages"].append(
                    ToolMessage(content=str(result), tool_call_id=tool_call["id"])
                )

        return state

    def _should_continue(self, state: AgentState) -> str:
        """
        Determine whether to continue or end.

        Args:
            state: Current agent state

        Returns:
            'continue' to execute tools, 'end' to finish
        """
        last_message = state["messages"][-1]

        # Check for tool calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"

        # Check max iterations
        if state["iteration"] >= self.config.max_iterations:
            logger.warning(f"Max iterations ({self.config.max_iterations}) reached")
            return "end"

        return "end"

    def query(self, query: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Process a user query through the agent.

        Args:
            query: User's question or request
            use_cache: Whether to use cached results

        Returns:
            Dictionary with answer, reasoning steps, and metadata
        """
        import time

        start_time = time.time()

        # Check cache if enabled
        cache_hit = False
        if use_cache and self.config.enable_cache:
            from .cache import generate_cache_key

            cache_key = generate_cache_key("agent_query", query=query)
            cached_result = self.cache.get(cache_key, ttl=self.config.cache_ttl_seconds)
            if cached_result:
                logger.info("Returning cached result")
                cached_result["cache_hit"] = True
                return cached_result

        # Initialize state
        initial_state: AgentState = {
            "query": query,
            "messages": [
                SystemMessage(content=AGENT_SYSTEM_PROMPT),
                HumanMessage(content=query),
            ],
            "tool_results": [],
            "answer": None,
            "iteration": 0,
            "reasoning_steps": [],
            "tools_used": [],
            "start_time": start_time,
            "cache_hit": False,
        }

        # Run the graph
        try:
            final_state = self.graph.invoke(initial_state)

            # Extract final answer
            last_message = final_state["messages"][-1]
            answer = last_message.content if hasattr(last_message, "content") else str(
                last_message
            )

            # Build result
            result = {
                "answer": answer,
                "reasoning_steps": final_state["reasoning_steps"],
                "tools_used": final_state["tools_used"],
                "tool_results": final_state["tool_results"],
                "iterations": final_state["iteration"],
                "execution_time_ms": int((time.time() - start_time) * 1000),
                "cache_hit": cache_hit,
                "timestamp": datetime.now().isoformat(),
            }

            # Cache result
            if use_cache and self.config.enable_cache:
                from .cache import generate_cache_key

                cache_key = generate_cache_key("agent_query", query=query)
                self.cache.set(cache_key, result)

            return result

        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            return {
                "answer": f"Error: {str(e)}",
                "reasoning_steps": [f"Error occurred: {str(e)}"],
                "tools_used": [],
                "tool_results": [],
                "iterations": 0,
                "execution_time_ms": int((time.time() - start_time) * 1000),
                "cache_hit": False,
                "error": str(e),
            }

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.stats()

    def clear_cache(self):
        """Clear the agent's cache."""
        self.cache.clear()
        logger.info("Agent cache cleared")
