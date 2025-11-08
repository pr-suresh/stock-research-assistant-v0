"""
LangChain tools for the Stock Research Agent.

These tools combine live stock data with RAG-based SEC filing search.
"""

from langchain_core.tools import tool
from typing import Optional
import sys
from pathlib import Path

# Import our existing modules
sys.path.insert(0, str(Path(__file__).parent))

from stock_tools import get_stock_price as _get_stock_price


@tool
def get_stock_price(ticker: str) -> str:
    """
    Get current stock price and key metrics for a ticker symbol.

    Use this tool when you need current/live stock market data.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)

    Returns:
        Formatted string with current price, change, volume, market cap, and price ranges.

    Examples:
        - get_stock_price("AAPL") -> Returns Apple's current stock info
        - get_stock_price("MSFT") -> Returns Microsoft's current stock info
    """
    result = _get_stock_price(ticker)

    if result.get('error'):
        return f"Error fetching stock data for {ticker}: {result['error']}"

    # Format the result as a readable string for the LLM
    formatted = f"""
Stock Information for {result['ticker']}:
- Current Price: ${result['price']:.2f}
- Change: ${result['change']:.2f} ({result['change_percent']:.2f}%)
- Volume: {result['volume']:,}
- Market Cap: ${result['market_cap']:,}
- Day Range: ${result['day_low']:.2f} - ${result['day_high']:.2f}
- 52-Week Range: ${result['week_52_low']:.2f} - ${result['week_52_high']:.2f}
- Data Timestamp: {result['timestamp']}
"""
    return formatted.strip()


@tool
def search_sec_filings(question: str, ticker: Optional[str] = None, section: Optional[str] = None) -> str:
    """
    Search SEC filings (10-K, 10-Q, etc.) to answer questions about companies.

    Use this tool when you need historical financial data, business descriptions,
    risk factors, or other information from official SEC filings.

    Args:
        question: Question about company operations, financials, risks, strategy, etc.
        ticker: Optional stock ticker to filter results (e.g., AAPL, MSFT)
        section: Optional section filter (e.g., "Risk Factors", "Business", "Financial Statements")

    Returns:
        Answer with source citations from SEC filings.

    Examples:
        - search_sec_filings("What is Apple's revenue?", ticker="AAPL")
        - search_sec_filings("What are the main risk factors?", ticker="AAPL", section="Risk Factors")
        - search_sec_filings("How much does the company spend on R&D?", ticker="AAPL")
    """
    # Import here to avoid circular imports and allow lazy loading
    try:
        from qa_engine import RAGQuestionAnswering
        from embeddings import EmbeddingGenerator
        from vector_store import QdrantVectorStore
        import os
        from dotenv import load_dotenv

        load_dotenv()

        # Initialize components
        embedder = EmbeddingGenerator()

        # Use cloud or local Qdrant based on environment
        qdrant_url = os.getenv('QDRANT_URL')
        if qdrant_url:
            vector_store = QdrantVectorStore(collection_name="sec_filings")
        else:
            qdrant_path = os.getenv('QDRANT_PATH', 'data/processed/qdrant_storage')
            vector_store = QdrantVectorStore(collection_name="sec_filings", path=qdrant_path)

        qa_engine = RAGQuestionAnswering(vector_store=vector_store, embedder=embedder)

        # Build filters
        filters = {}
        if ticker:
            filters['ticker'] = ticker.upper()
        if section:
            filters['section'] = section

        # Ask the question
        result = qa_engine.ask(
            question=question,
            filters=filters if filters else None,
            top_k=3  # Get top 3 most relevant chunks
        )

        # Format the response for the agent
        answer = result['answer']
        sources = result.get('sources', [])

        # Add source information
        if sources:
            source_info = "\n\nSources from SEC Filings:"
            for src in sources[:3]:  # Top 3 sources
                metadata = src.get('metadata', {})
                source_info += f"\n- {metadata.get('ticker', 'N/A')} {metadata.get('filing_type', '')} - {metadata.get('section', 'N/A')}"
        else:
            source_info = "\n\nNote: No relevant SEC filing data found for this query."

        return answer + source_info

    except Exception as e:
        return f"Error searching SEC filings: {str(e)}\n\nPlease ensure Qdrant database is accessible and contains SEC filing data."


@tool
def compare_stock_and_filings(ticker: str, question: str) -> str:
    """
    Compare current stock data with historical SEC filing information for a company.

    This is a hybrid tool that combines live market data with historical SEC filing analysis.
    Use this when you need both current market performance and historical context.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT)
        question: Question about the company (e.g., "revenue", "growth", "strategy")

    Returns:
        Comparison of current stock metrics with historical filing data.

    Examples:
        - compare_stock_and_filings("AAPL", "How does current stock price compare to revenue trends?")
        - compare_stock_and_filings("MSFT", "What's the relationship between current market cap and reported assets?")
    """
    # Get current stock price
    stock_info = get_stock_price.invoke({"ticker": ticker})

    # Search SEC filings for the question
    filing_info = search_sec_filings.invoke({
        "question": question,
        "ticker": ticker
    })

    # Combine both
    combined = f"""
CURRENT MARKET DATA:
{stock_info}

HISTORICAL SEC FILING DATA:
{filing_info}

Analysis: The above data combines current live stock market information with historical data from official SEC filings, providing both real-time and historical context for {ticker}.
"""

    return combined.strip()


# Export all tools as a list for easy agent initialization
ALL_TOOLS = [
    get_stock_price,
    search_sec_filings,
    compare_stock_and_filings
]
