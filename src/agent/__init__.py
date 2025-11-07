"""
Agent module for stock research assistant.

This module provides agent capabilities with live data tools:
- Stock price lookup (Yahoo Finance)
- Financial comparison
- Multi-step reasoning with LangGraph
- Caching for performance
"""

from .agent import StockResearchAgent
from .tools import get_stock_price, compare_financials, search_sec_filings

__all__ = [
    "StockResearchAgent",
    "get_stock_price",
    "compare_financials",
    "search_sec_filings",
]
