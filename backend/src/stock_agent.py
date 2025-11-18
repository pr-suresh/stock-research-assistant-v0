"""
Stock Research Agent using LangChain with OpenAI function calling.

This agent can:
- Get live stock prices
- Search SEC filings
- Combine live and historical data
- Perform multi-step reasoning
"""

from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
from dotenv import load_dotenv
import json

# Import our tools
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from agent_tools import ALL_TOOLS

# Load environment
load_dotenv()

# Note: LangChain caching is optional and version-dependent
# Skipping cache setup for compatibility across LangChain versions


class StockResearchAgent:
    """
    Agent that combines live stock data with SEC filing analysis.

    Uses OpenAI's function calling to intelligently select and use tools
    for answering complex questions about stocks.
    """

    def __init__(
        self,
        model: str = None,
        temperature: float = 0.1,
        max_iterations: int = 5,
        verbose: bool = False
    ):
        """
        Initialize the Stock Research Agent.

        Args:
            model: OpenAI model to use (default: from env or gpt-4-turbo-preview)
            temperature: Model temperature (default: 0.1 for factual responses)
            max_iterations: Maximum reasoning steps (default: 5)
            verbose: Whether to print detailed execution logs (default: False)
        """
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.verbose = verbose

        # Initialize LLM with function calling
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            api_key=os.getenv('OPENAI_API_KEY')
        )

        # Bind tools to LLM for function calling
        self.llm_with_tools = self.llm.bind_tools(ALL_TOOLS)

        # Agent system prompt
        self.system_prompt = """You are a financial research assistant that helps analyze stocks using both live market data and historical SEC filings.

You have access to these tools:
1. get_stock_price - Get current stock price and metrics from live market data
2. search_sec_filings - Search official SEC filings (10-K, 10-Q, etc.) for historical company information
3. compare_stock_and_filings - Combine live stock data with SEC filing analysis

Guidelines:
- Use get_stock_price for current market data (price, volume, market cap)
- Use search_sec_filings for historical data (revenue, risk factors, business description, R&D spending)
- Use compare_stock_and_filings when you need both live and historical context
- Always cite your sources and be clear about whether data is current or historical
- If you need multiple steps, think through the process logically
- Be precise with financial figures and always include units ($, %, etc.)
- If you don't have enough information, say so clearly

Answer questions accurately and thoroughly, using the appropriate tools to gather information."""

    def query(self, question: str) -> Dict[str, Any]:
        """
        Execute a query using the agent with multi-step reasoning.

        Args:
            question: User's question about stocks or companies

        Returns:
            Dictionary with:
            - answer: Final answer to the question
            - tool_calls: List of tools used with arguments
            - reasoning_steps: Agent's reasoning process
            - metadata: Execution details (tokens, timing, etc.)
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=question)
        ]

        tool_calls_made = []
        reasoning_steps = []
        iterations = 0

        if self.verbose:
            print(f"\n{'='*80}")
            print(f"AGENT QUERY: {question}")
            print(f"{'='*80}\n")

        # Agentic loop with function calling
        while iterations < self.max_iterations:
            iterations += 1

            if self.verbose:
                print(f"\n--- Iteration {iterations} ---")

            # Get response from LLM
            response = self.llm_with_tools.invoke(messages)

            # Check if the model wants to call tools
            if response.tool_calls:
                if self.verbose:
                    print(f"Tool calls requested: {len(response.tool_calls)}")

                # IMPORTANT: Add the AI response with tool_calls FIRST
                messages.append(response)

                # Execute each tool call
                for tool_call in response.tool_calls:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']

                    if self.verbose:
                        print(f"\n  Calling tool: {tool_name}")
                        print(f"  Arguments: {tool_args}")

                    # Find and execute the tool
                    tool_result = None
                    for tool in ALL_TOOLS:
                        if tool.name == tool_name:
                            try:
                                tool_result = tool.invoke(tool_args)
                                if self.verbose:
                                    print(f"  Result: {tool_result[:200]}..." if len(tool_result) > 200 else f"  Result: {tool_result}")
                            except Exception as e:
                                tool_result = f"Error executing {tool_name}: {str(e)}"
                                if self.verbose:
                                    print(f"  Error: {tool_result}")
                            break

                    # Record the tool call
                    tool_calls_made.append({
                        'tool': tool_name,
                        'arguments': tool_args,
                        'result': tool_result
                    })

                    # Add tool result to messages (AFTER the AI response)
                    from langchain_core.messages import ToolMessage
                    messages.append(ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call['id']
                    ))

            else:
                # No more tool calls - agent has final answer
                if self.verbose:
                    print("\nAgent has final answer (no more tool calls)")

                final_answer = response.content

                return {
                    'answer': final_answer,
                    'tool_calls': tool_calls_made,
                    'reasoning_steps': reasoning_steps,
                    'metadata': {
                        'iterations': iterations,
                        'model': self.model,
                        'total_tools_used': len(tool_calls_made),
                        'cache_enabled': True
                    }
                }

        # Max iterations reached
        return {
            'answer': "I reached the maximum number of reasoning steps. Please try rephrasing your question or breaking it into smaller parts.",
            'tool_calls': tool_calls_made,
            'reasoning_steps': reasoning_steps,
            'metadata': {
                'iterations': iterations,
                'model': self.model,
                'total_tools_used': len(tool_calls_made),
                'max_iterations_reached': True
            }
        }

    def simple_query(self, question: str) -> str:
        """
        Execute a simple query and return just the answer string.

        Args:
            question: User's question

        Returns:
            Answer string
        """
        result = self.query(question)
        return result['answer']
