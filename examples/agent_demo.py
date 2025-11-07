#!/usr/bin/env python3
"""
Demo script for the Stock Research Agent (Phase 1 - Infrastructure Test).

This script demonstrates:
1. Basic agent initialization
2. Echo tool functionality
3. Multi-step reasoning
4. Caching behavior
5. Performance metrics

Usage:
    python examples/agent_demo.py
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import StockResearchAgent
from src.agent.cache import get_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_result(result: dict):
    """Print agent result in a readable format."""
    print(f"Answer: {result['answer']}\n")
    print(f"Iterations: {result['iterations']}")
    print(f"Execution time: {result['execution_time_ms']}ms")
    print(f"Cache hit: {result['cache_hit']}")
    print(f"Tools used: {', '.join(result['tools_used']) if result['tools_used'] else 'None'}")

    if result.get("reasoning_steps"):
        print("\nReasoning steps:")
        for i, step in enumerate(result["reasoning_steps"], 1):
            print(f"  {i}. {step}")

    if result.get("tool_results"):
        print("\nTool results:")
        for tr in result["tool_results"]:
            print(f"  - {tr['tool']}: {tr['result']}")


def demo_basic_query():
    """Demo 1: Basic agent query with echo tool."""
    print_section("Demo 1: Basic Query with Echo Tool")

    agent = StockResearchAgent(use_all_tools=False)  # Phase 1: echo only
    result = agent.query("Echo back: Hello, Agent!")

    print_result(result)


def demo_caching():
    """Demo 2: Cache behavior."""
    print_section("Demo 2: Caching Behavior")

    agent = StockResearchAgent(use_all_tools=False)

    # First query - should be a cache miss
    print("First query (cache miss expected):")
    result1 = agent.query("Echo: Testing cache", use_cache=True)
    print(f"Cache hit: {result1['cache_hit']}")
    print(f"Execution time: {result1['execution_time_ms']}ms\n")

    # Second query - should be a cache hit
    print("Second query (cache hit expected):")
    result2 = agent.query("Echo: Testing cache", use_cache=True)
    print(f"Cache hit: {result2['cache_hit']}")
    print(f"Execution time: {result2['execution_time_ms']}ms\n")

    # Show cache stats
    stats = agent.get_cache_stats()
    print(f"Cache statistics:")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Hit rate: {stats['hit_rate_percent']}%")
    print(f"  Cached entries: {stats['cached_entries']}")


def demo_placeholder_tools():
    """Demo 3: Test placeholder tools (coming in Phase 2)."""
    print_section("Demo 3: Placeholder Tools (Phase 2 Preview)")

    agent = StockResearchAgent(use_all_tools=True)  # Include placeholder tools

    queries = [
        "What's the stock price of AAPL?",
        "Compare AAPL and MSFT financials",
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        result = agent.query(query, use_cache=False)
        print(f"Answer: {result['answer']}")
        print(f"Tools used: {result['tools_used']}")


def demo_interactive():
    """Demo 4: Interactive mode."""
    print_section("Demo 4: Interactive Mode")

    agent = StockResearchAgent(use_all_tools=True)

    print("Enter queries (type 'quit' to exit, 'stats' for cache stats, 'clear' to clear cache):")
    print("Examples:")
    print("  - Echo: Hello")
    print("  - What's the price of AAPL?")
    print("  - Compare TSLA and NVDA\n")

    while True:
        try:
            query = input("\n> ").strip()

            if not query:
                continue

            if query.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            if query.lower() == "stats":
                stats = agent.get_cache_stats()
                print(f"\nCache Statistics:")
                print(f"  Hits: {stats['hits']}")
                print(f"  Misses: {stats['misses']}")
                print(f"  Hit rate: {stats['hit_rate_percent']}%")
                print(f"  Cached entries: {stats['cached_entries']}")
                continue

            if query.lower() == "clear":
                agent.clear_cache()
                print("Cache cleared!")
                continue

            # Process query
            result = agent.query(query)
            print(f"\n{result['answer']}")
            print(
                f"\n[{result['execution_time_ms']}ms | "
                f"Cache: {'HIT' if result['cache_hit'] else 'MISS'} | "
                f"Tools: {', '.join(result['tools_used']) or 'None'}]"
            )

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            logger.error(f"Error processing query: {e}", exc_info=True)


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("  STOCK RESEARCH AGENT - PHASE 1 DEMO")
    print("  Testing Agent Infrastructure with Echo Tool")
    print("=" * 80)

    try:
        # Check if .env exists
        if not os.path.exists(".env"):
            print("\n⚠️  WARNING: .env file not found!")
            print("   Please copy .env.example to .env and add your OPENAI_API_KEY")
            print("   Command: cp .env.example .env\n")
            return

        # Run demos
        demo_basic_query()
        demo_caching()
        demo_placeholder_tools()

        # Ask if user wants interactive mode
        print("\n" + "=" * 80)
        response = input("\nWould you like to try interactive mode? (y/n): ").strip().lower()
        if response in ["y", "yes"]:
            demo_interactive()

        print("\n" + "=" * 80)
        print("  ✅ Phase 1 Demo Complete!")
        print("  Next Steps:")
        print("    - Phase 2: Implement live data tools (yfinance)")
        print("    - Phase 3: Add multi-step reasoning")
        print("    - Phase 4: Optimize caching")
        print("=" * 80 + "\n")

    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("   Check that your OPENAI_API_KEY is set in .env")
        sys.exit(1)


if __name__ == "__main__":
    main()
