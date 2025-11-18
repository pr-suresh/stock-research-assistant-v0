"""
RAG Question-Answering Engine

This module implements a Retrieval-Augmented Generation (RAG) system for answering
questions about SEC filings using GPT-4 and Qdrant vector database.

Pipeline:
1. Embed user question
2. Retrieve relevant chunks from Qdrant
3. Format context with citations
4. Generate answer with GPT-4
5. Return answer with source attributions
"""

from typing import List, Dict, Any, Optional, Tuple
import time
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

try:
    # Try relative imports (when used as a module)
    from .vector_store import QdrantVectorStore
    from .embeddings import EmbeddingGenerator
    from .prompts import (
        SYSTEM_PROMPT,
        QA_TEMPLATE,
        NO_CONTEXT_RESPONSE,
        format_context_with_citations,
        format_source_metadata,
        get_error_message,
    )
except ImportError:
    # Fall back to absolute imports (when run directly or from parent directory)
    from vector_store import QdrantVectorStore
    from embeddings import EmbeddingGenerator
    from prompts import (
        SYSTEM_PROMPT,
        QA_TEMPLATE,
        NO_CONTEXT_RESPONSE,
        format_context_with_citations,
        format_source_metadata,
        get_error_message,
    )


class RAGQuestionAnswering:
    """
    RAG-based Question Answering system for SEC filings.

    Combines vector search (retrieval) with LLM generation to answer
    questions with proper source citations.

    Example:
        qa = RAGQuestionAnswering(vector_store, embedder)
        result = qa.ask("What is Apple's revenue?", filters={"ticker": "AAPL"})
        print(result['answer'])
        print(result['sources'])
    """

    def __init__(
        self,
        vector_store: QdrantVectorStore,
        embedder: EmbeddingGenerator,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
    ):
        """
        Initialize the Q&A engine.

        Args:
            vector_store: QdrantVectorStore instance for retrieval
            embedder: EmbeddingGenerator instance for query embedding
            model: OpenAI model name (defaults to env var or gpt-4-turbo-preview)
            temperature: LLM temperature (defaults to env var or 0.1)
            max_tokens: Maximum tokens in response (defaults to env var or 1000)
        """
        self.vector_store = vector_store
        self.embedder = embedder

        # Get configuration from environment or use defaults
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        self.temperature = (
            temperature
            if temperature is not None
            else float(os.getenv('OPENAI_TEMPERATURE', '0.1'))
        )
        self.max_tokens = (
            max_tokens
            if max_tokens is not None
            else int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
        )

        # Initialize ChatOpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(get_error_message('no_api_key'))

        self.llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=api_key,
        )

        print(f"✅ Initialized Q&A engine with {self.model}")

    def ask(
        self,
        question: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
        min_score: float = None,
    ) -> Dict[str, Any]:
        """
        Answer a question about SEC filings.

        Args:
            question: User's question
            filters: Optional metadata filters (ticker, filing_type, section)
            top_k: Number of chunks to retrieve
            min_score: Minimum similarity score threshold

        Returns:
            Dictionary with:
                - answer: Generated answer with citations
                - sources: List of source documents with metadata
                - metadata: Processing metadata (tokens, cost, timing)

        Example:
            result = qa.ask(
                "What is Apple's revenue?",
                filters={"ticker": "AAPL"},
                top_k=3
            )
        """
        start_time = time.time()

        try:
            # Step 1: Retrieve relevant context
            retrieval_start = time.time()
            chunks = self._retrieve_context(question, filters, top_k, min_score)
            retrieval_time = (time.time() - retrieval_start) * 1000  # ms

            # Handle no results
            if not chunks:
                return self._format_no_results_response(retrieval_time)

            # Step 2: Format context with citations
            context_str = self._format_context_with_citations(chunks)

            # Step 3: Generate answer
            generation_start = time.time()
            answer, tokens_used = self._generate_answer(question, context_str)
            generation_time = (time.time() - generation_start) * 1000  # ms

            # Step 4: Format response with sources
            response = self._format_response(
                answer=answer,
                chunks=chunks,
                tokens_used=tokens_used,
                retrieval_time=retrieval_time,
                generation_time=generation_time,
            )

            return response

        except Exception as e:
            return self._format_error_response(str(e))

    def _retrieve_context(
        self,
        question: str,
        filters: Optional[Dict[str, Any]],
        top_k: int,
        min_score: Optional[float],
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Retrieve relevant chunks from vector store.

        Args:
            question: User question
            filters: Metadata filters
            top_k: Number of results
            min_score: Minimum similarity threshold

        Returns:
            List of (content, metadata) tuples
        """
        # Get minimum score from env if not provided
        if min_score is None:
            min_score = float(os.getenv('QA_MIN_SIMILARITY_SCORE', '0.0'))

        # Generate query embedding
        query_vector = self.embedder.embed_query(question)

        # Search vector store
        search_results = self.vector_store.search(
            query_vector=query_vector,
            limit=top_k,
            filter=filters,
            score_threshold=min_score if min_score > 0 else None,
        )

        # Extract content and metadata
        chunks = [(result['content'], result['metadata']) for result in search_results]

        return chunks

    def _format_context_with_citations(
        self, chunks: List[Tuple[str, Dict[str, Any]]]
    ) -> str:
        """
        Format retrieved chunks with citation numbers.

        Args:
            chunks: List of (content, metadata) tuples

        Returns:
            Formatted context string
        """
        return format_context_with_citations(chunks)

    def _generate_answer(
        self, question: str, context: str
    ) -> Tuple[str, Dict[str, int]]:
        """
        Generate answer using LLM.

        Args:
            question: User question
            context: Formatted context with citations

        Returns:
            Tuple of (answer, token_usage)
        """
        # Build messages
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=QA_TEMPLATE.format(context=context, question=question)),
        ]

        # Call LLM
        try:
            response = self.llm.invoke(messages)
            answer = response.content

            # Extract token usage
            tokens_used = {
                'prompt_tokens': response.response_metadata.get('token_usage', {}).get(
                    'prompt_tokens', 0
                ),
                'completion_tokens': response.response_metadata.get(
                    'token_usage', {}
                ).get('completion_tokens', 0),
                'total_tokens': response.response_metadata.get('token_usage', {}).get(
                    'total_tokens', 0
                ),
            }

            return answer, tokens_used

        except Exception as e:
            error_msg = str(e)
            if 'rate_limit' in error_msg.lower():
                raise ValueError(get_error_message('rate_limit'))
            elif 'timeout' in error_msg.lower():
                raise ValueError(get_error_message('timeout'))
            else:
                raise ValueError(get_error_message('llm_error', error_msg))

    def _format_response(
        self,
        answer: str,
        chunks: List[Tuple[str, Dict[str, Any]]],
        tokens_used: Dict[str, int],
        retrieval_time: float,
        generation_time: float,
    ) -> Dict[str, Any]:
        """
        Format the final response with answer, sources, and metadata.

        Args:
            answer: Generated answer
            chunks: Retrieved chunks with metadata
            tokens_used: Token usage stats
            retrieval_time: Time for retrieval (ms)
            generation_time: Time for generation (ms)

        Returns:
            Formatted response dictionary
        """
        # Format sources
        sources = []
        for i, (content, metadata) in enumerate(chunks, 1):
            source = {
                'id': i,
                'content': content,
                'metadata': {
                    **metadata,
                    'formatted_citation': format_source_metadata(metadata),
                },
            }
            sources.append(source)

        # Calculate cost estimate
        # GPT-4 Turbo pricing: $0.01/1K input, $0.03/1K output
        input_cost = (tokens_used['prompt_tokens'] / 1000) * 0.01
        output_cost = (tokens_used['completion_tokens'] / 1000) * 0.03
        total_cost = input_cost + output_cost

        # Build metadata
        metadata = {
            'model': self.model,
            'prompt_tokens': tokens_used['prompt_tokens'],
            'completion_tokens': tokens_used['completion_tokens'],
            'total_tokens': tokens_used['total_tokens'],
            'retrieval_time_ms': round(retrieval_time, 2),
            'generation_time_ms': round(generation_time, 2),
            'total_time_ms': round(retrieval_time + generation_time, 2),
            'estimated_cost_usd': round(total_cost, 6),
            'sources_count': len(sources),
        }

        return {
            'answer': answer,
            'sources': sources,
            'metadata': metadata,
        }

    def _format_no_results_response(self, retrieval_time: float) -> Dict[str, Any]:
        """
        Format response when no relevant documents are found.

        Args:
            retrieval_time: Time spent on retrieval (ms)

        Returns:
            Response with no results message
        """
        return {
            'answer': NO_CONTEXT_RESPONSE,
            'sources': [],
            'metadata': {
                'model': self.model,
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0,
                'retrieval_time_ms': round(retrieval_time, 2),
                'generation_time_ms': 0,
                'total_time_ms': round(retrieval_time, 2),
                'estimated_cost_usd': 0,
                'sources_count': 0,
                'no_results': True,
            },
        }

    def _format_error_response(self, error: str) -> Dict[str, Any]:
        """
        Format response for errors.

        Args:
            error: Error message

        Returns:
            Error response
        """
        return {
            'answer': f"I encountered an error while processing your question: {error}",
            'sources': [],
            'metadata': {
                'error': True,
                'error_message': error,
            },
        }

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model configuration.

        Returns:
            Model configuration details
        """
        return {
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'vector_store_mode': self.vector_store.mode,
        }


def estimate_cost(num_queries: int, avg_tokens_per_query: int = 1000) -> Dict[str, float]:
    """
    Estimate costs for a given number of queries.

    Args:
        num_queries: Number of expected queries
        avg_tokens_per_query: Average tokens (input + output) per query

    Returns:
        Cost breakdown
    """
    # Rough breakdown: 70% input, 30% output
    avg_input_tokens = int(avg_tokens_per_query * 0.7)
    avg_output_tokens = int(avg_tokens_per_query * 0.3)

    # GPT-4 Turbo pricing
    input_cost_per_query = (avg_input_tokens / 1000) * 0.01
    output_cost_per_query = (avg_output_tokens / 1000) * 0.03
    cost_per_query = input_cost_per_query + output_cost_per_query

    return {
        'num_queries': num_queries,
        'avg_tokens_per_query': avg_tokens_per_query,
        'cost_per_query': round(cost_per_query, 6),
        'total_cost': round(cost_per_query * num_queries, 2),
        'monthly_cost_1000_queries': round(cost_per_query * 1000, 2),
    }
