"""
Tools for the stock research agent.

Each tool is a function that the agent can call to gather information.
"""

import logging
from typing import Dict, Any, Optional
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


# ============================================================================
# PHASE 1: Echo Tool (for testing infrastructure)
# ============================================================================


@tool
def echo_tool(message: str) -> str:
    """
    Simple echo tool for testing the agent infrastructure.

    Args:
        message: The message to echo back

    Returns:
        The same message, echoed back
    """
    logger.info(f"Echo tool called with message: {message}")
    return f"Echo: {message}"


# ============================================================================
# PHASE 2: Live Data Tools (to be implemented)
# ============================================================================


@tool
def get_stock_price(ticker: str) -> Dict[str, Any]:
    """
    Get current stock price and market data for a ticker symbol.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')

    Returns:
        Dictionary with price, volume, market cap, and other metrics

    Note:
        This is a placeholder. Full implementation coming in Phase 2.
    """
    logger.info(f"get_stock_price called with ticker: {ticker}")
    # TODO: Implement yfinance integration in Phase 2
    return {
        "ticker": ticker.upper(),
        "status": "placeholder",
        "message": "Full implementation coming in Phase 2",
        "note": "Will use yfinance to fetch real-time data",
    }


@tool
def compare_financials(ticker1: str, ticker2: str) -> Dict[str, Any]:
    """
    Compare financial metrics between two companies.

    Args:
        ticker1: First stock ticker symbol
        ticker2: Second stock ticker symbol

    Returns:
        Dictionary with comparative analysis

    Note:
        This is a placeholder. Full implementation coming in Phase 2.
    """
    logger.info(f"compare_financials called: {ticker1} vs {ticker2}")
    # TODO: Implement comparison logic in Phase 2
    return {
        "ticker1": ticker1.upper(),
        "ticker2": ticker2.upper(),
        "status": "placeholder",
        "message": "Full implementation coming in Phase 2",
        "note": "Will combine yfinance data with SEC filing insights",
    }


@tool
def search_sec_filings(query: str, ticker: Optional[str] = None) -> Dict[str, Any]:
    """
    Search SEC filings for specific information.

    Args:
        query: Search query (e.g., "risk factors", "revenue growth")
        ticker: Optional ticker symbol to filter results

    Returns:
        Dictionary with search results and relevant excerpts

    Note:
        This is a placeholder. Full implementation coming in Phase 2.
        Will integrate with existing qa_engine.py from the RAG system.
    """
    logger.info(f"search_sec_filings called: query='{query}', ticker={ticker}")
    # TODO: Integrate with existing qa_engine.py in Phase 2
    return {
        "query": query,
        "ticker": ticker,
        "status": "placeholder",
        "message": "Full implementation coming in Phase 2",
        "note": "Will wrap existing RAG Q&A engine as an agent tool",
    }


# ============================================================================
# Tool Registry
# ============================================================================


def get_all_tools():
    """
    Get list of all available tools for the agent.

    Returns:
        List of tool functions
    """
    return [
        echo_tool,
        get_stock_price,
        compare_financials,
        search_sec_filings,
    ]


def get_phase1_tools():
    """
    Get only Phase 1 tools (for testing infrastructure).

    Returns:
        List of working tool functions
    """
    return [echo_tool]
