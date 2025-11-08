"""
Demo script for testing the Stock Research Agent.

This script demonstrates the agent's ability to:
1. Get live stock prices
2. Search SEC filings
3. Combine both for hybrid analysis
4. Perform multi-step reasoning
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from stock_agent import StockResearchAgent
from dotenv import load_dotenv

load_dotenv()


def print_separator(title=""):
    """Print a nice separator."""
    if title:
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    else:
        print(f"{'='*80}\n")


def print_agent_result(result):
    """Pretty print agent query result."""
    print(f"ANSWER:")
    print(f"{result['answer']}\n")

    if result['tool_calls']:
        print(f"TOOL CALLS ({len(result['tool_calls'])}):")
        for i, tc in enumerate(result['tool_calls'], 1):
            print(f"\n  {i}. {tc['tool']}")
            print(f"     Arguments: {tc['arguments']}")
            result_preview = tc['result'][:150] + "..." if len(tc['result']) > 150 else tc['result']
            print(f"     Result: {result_preview}")

    print(f"\nMETADATA:")
    for key, value in result['metadata'].items():
        print(f"  {key}: {value}")


def main():
    """Run demo queries."""
    print_separator("STOCK RESEARCH AGENT DEMO")

    print("Initializing agent...")
    agent = StockResearchAgent(verbose=True)
    print("✅ Agent initialized\n")

    # Example queries
    examples = [
        {
            "title": "Example 1: Simple Stock Price Query",
            "question": "What is Apple's current stock price?",
            "description": "Tests get_stock_price tool"
        },
        {
            "title": "Example 2: SEC Filing Query",
            "question": "What is Apple's revenue according to their SEC filings?",
            "description": "Tests search_sec_filings tool"
        },
        {
            "title": "Example 3: Hybrid Query (Multi-step)",
            "question": "What is Apple's current stock price and how does it compare to their revenue from the last 10-K?",
            "description": "Tests multi-step reasoning with both tools"
        },
    ]

    for i, example in enumerate(examples, 1):
        print_separator(f"{example['title']}")
        print(f"Description: {example['description']}")
        print(f"Question: {example['question']}\n")

        try:
            result = agent.query(example['question'])
            print_agent_result(result)

        except Exception as e:
            print(f"❌ Error: {str(e)}")

        if i < len(examples):
            input("\nPress Enter to continue to next example...")

    print_separator("DEMO COMPLETE")
    print("✅ All examples completed successfully!")
    print("\nYou can now:")
    print("1. Try your own questions by modifying this script")
    print("2. Start the API: uvicorn api:app --reload --port 8000")
    print("3. Test via Swagger UI: http://localhost:8000/docs")
    print()


def interactive_mode():
    """Interactive Q&A mode."""
    print_separator("INTERACTIVE AGENT MODE")

    print("Ask the agent questions about stocks and companies.")
    print("The agent can:")
    print("  - Get live stock prices")
    print("  - Search SEC filings")
    print("  - Combine both for analysis")
    print("\nType 'quit' or 'exit' to stop.\n")

    agent = StockResearchAgent(verbose=False)

    while True:
        try:
            question = input("Your question: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            if not question:
                continue

            print("\n🤖 Thinking...\n")
            result = agent.query(question)

            print(f"💡 {result['answer']}\n")

            if result['tool_calls']:
                print(f"🔧 Tools used: {', '.join([tc['tool'] for tc in result['tool_calls']])}")
                print(f"📊 Iterations: {result['metadata']['iterations']}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stock Research Agent Demo")
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    else:
        main()
