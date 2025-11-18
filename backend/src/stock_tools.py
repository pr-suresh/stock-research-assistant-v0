"""
Stock price tools using Yahoo Finance API.

Simple implementation with built-in caching for live market data.
"""

import yfinance as yf
from functools import lru_cache
from typing import Dict, Any, Optional
from datetime import datetime


@lru_cache(maxsize=100)
def get_stock_price(ticker: str) -> Dict[str, Any]:
    """
    Get current stock price and key metrics for a ticker symbol.

    Uses Yahoo Finance API via yfinance library.
    Results are cached using Python's built-in LRU cache.

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT, TSLA)

    Returns:
        Dictionary with stock information:
        - ticker: Stock symbol
        - price: Current/last price
        - change: Price change amount
        - change_percent: Percentage change
        - volume: Trading volume
        - market_cap: Market capitalization
        - day_high: Today's high
        - day_low: Today's low
        - week_52_high: 52-week high
        - week_52_low: 52-week low
        - timestamp: When data was fetched
        - error: Error message if fetch failed

    Example:
        >>> data = get_stock_price("AAPL")
        >>> print(f"Apple price: ${data['price']}")
    """
    ticker = ticker.upper().strip()

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Get current price (try multiple fields as Yahoo Finance API varies)
        current_price = (
            info.get('currentPrice') or
            info.get('regularMarketPrice') or
            info.get('previousClose')
        )

        # Calculate change if we have both current and previous
        previous_close = info.get('previousClose')
        change = None
        change_percent = None

        if current_price and previous_close:
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100
        elif info.get('regularMarketChange'):
            change = info.get('regularMarketChange')
            change_percent = info.get('regularMarketChangePercent')

        result = {
            'ticker': ticker,
            'price': current_price,
            'change': change,
            'change_percent': change_percent,
            'volume': info.get('volume'),
            'market_cap': info.get('marketCap'),
            'day_high': info.get('dayHigh') or info.get('regularMarketDayHigh'),
            'day_low': info.get('dayLow') or info.get('regularMarketDayLow'),
            'week_52_high': info.get('fiftyTwoWeekHigh'),
            'week_52_low': info.get('fiftyTwoWeekLow'),
            'timestamp': datetime.now().isoformat(),
            'error': None
        }

        return result

    except Exception as e:
        return {
            'ticker': ticker,
            'price': None,
            'change': None,
            'change_percent': None,
            'volume': None,
            'market_cap': None,
            'day_high': None,
            'day_low': None,
            'week_52_high': None,
            'week_52_low': None,
            'timestamp': datetime.now().isoformat(),
            'error': f"Failed to fetch stock data: {str(e)}"
        }


def clear_stock_cache():
    """Clear the LRU cache for stock prices (useful for testing or forced refresh)."""
    get_stock_price.cache_clear()


def get_cache_info() -> Dict[str, int]:
    """
    Get cache statistics.

    Returns:
        Dictionary with cache hits, misses, size, and max size.
    """
    cache_info = get_stock_price.cache_info()
    return {
        'hits': cache_info.hits,
        'misses': cache_info.misses,
        'size': cache_info.currsize,
        'max_size': cache_info.maxsize
    }
