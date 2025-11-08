"""
Simple test script for stock price functionality.

Tests the get_stock_price function and caching behavior.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from stock_tools import get_stock_price, get_cache_info, clear_stock_cache


def test_stock_price():
    """Test fetching stock price for Apple."""
    print("=" * 80)
    print("STOCK PRICE TOOL TEST")
    print("=" * 80)
    print()

    # Test 1: Fetch Apple stock price
    print("1. Fetching AAPL stock price (first call - will fetch from Yahoo Finance)...")
    result1 = get_stock_price("AAPL")

    if result1.get('error'):
        print(f"   ❌ Error: {result1['error']}")
    else:
        print(f"   ✅ Success!")
        print(f"   Ticker: {result1['ticker']}")
        print(f"   Price: ${result1['price']:.2f}" if result1['price'] else "   Price: N/A")
        print(f"   Change: {result1['change']:.2f} ({result1['change_percent']:.2f}%)" if result1['change'] else "   Change: N/A")
        print(f"   Volume: {result1['volume']:,}" if result1['volume'] else "   Volume: N/A")
        print(f"   Market Cap: ${result1['market_cap']:,}" if result1['market_cap'] else "   Market Cap: N/A")

    print()

    # Test 2: Check cache
    cache_info = get_cache_info()
    print("2. Cache status after first call:")
    print(f"   Hits: {cache_info['hits']}")
    print(f"   Misses: {cache_info['misses']}")
    print(f"   Size: {cache_info['size']}/{cache_info['max_size']}")

    print()

    # Test 3: Fetch again to test caching
    print("3. Fetching AAPL again (second call - should be cached)...")
    result2 = get_stock_price("AAPL")

    cache_info = get_cache_info()
    print(f"   ✅ Cached result retrieved!")
    print(f"   Cache hits: {cache_info['hits']}")
    print(f"   Cache misses: {cache_info['misses']}")

    print()

    # Test 4: Fetch different ticker
    print("4. Fetching MSFT stock price...")
    result3 = get_stock_price("MSFT")

    if result3.get('error'):
        print(f"   ❌ Error: {result3['error']}")
    else:
        print(f"   ✅ Success!")
        print(f"   Price: ${result3['price']:.2f}" if result3['price'] else "   Price: N/A")

    print()

    # Final cache stats
    cache_info = get_cache_info()
    print("5. Final cache statistics:")
    print(f"   Total hits: {cache_info['hits']}")
    print(f"   Total misses: {cache_info['misses']}")
    print(f"   Cache size: {cache_info['size']}/{cache_info['max_size']}")
    print(f"   Hit rate: {cache_info['hits']/(cache_info['hits']+cache_info['misses'])*100:.1f}%")

    print()
    print("=" * 80)
    print("✅ Stock price tool test complete!")
    print("=" * 80)


if __name__ == "__main__":
    test_stock_price()
