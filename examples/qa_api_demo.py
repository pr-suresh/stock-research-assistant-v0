"""
Q&A API Demo - CLI Testing Tool

Test the Q&A engine before using the API endpoint.
This connects directly to Qdrant and uses the QA engine.

USAGE:
    python qa_api_demo.py

REQUIREMENTS:
    - Qdrant database with processed filings
    - OPENAI_API_KEY in .env
"""

from pathlib import Path
import sys
from dotenv import load_dotenv
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from vector_store import QdrantVectorStore
from embeddings import EmbeddingGenerator
from qa_engine import RAGQuestionAnswering


def print_answer(result: dict):
    """Pretty print Q&A result."""
    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(result['answer'])

    if result['sources']:
        print("\n" + "=" * 80)
        print(f"SOURCES ({len(result['sources'])} documents)")
        print("=" * 80)

        for source in result['sources']:
            print(f"\n[{source['id']}] {source['metadata'].get('formatted_citation', 'N/A')}")
            print(f"    Score: {source['metadata'].get('score', 0):.3f}")
            print(f"    Preview: {source['content'][:150]}...")

    # Print metadata
    metadata = result.get('metadata', {})
    if metadata:
        print("\n" + "=" * 80)
        print("METADATA")
        print("=" * 80)
        print(f"Model: {metadata.get('model', 'N/A')}")
        print(f"Tokens: {metadata.get('total_tokens', 0)} "
              f"(prompt: {metadata.get('prompt_tokens', 0)}, "
              f"completion: {metadata.get('completion_tokens', 0)})")
        print(f"Cost: ${metadata.get('estimated_cost_usd', 0):.6f}")
        print(f"Time: {metadata.get('total_time_ms', 0):.0f}ms "
              f"(retrieval: {metadata.get('retrieval_time_ms', 0):.0f}ms, "
              f"generation: {metadata.get('generation_time_ms', 0):.0f}ms)")

    print("=" * 80 + "\n")


def run_example_queries(qa_engine: RAGQuestionAnswering):
    """Run predefined example queries."""

    examples = [
        {
            "question": "What is Apple's revenue?",
            "filters": {"ticker": "AAPL"},
            "top_k": 3
        },
        {
            "question": "What are the main risk factors?",
            "filters": {"ticker": "AAPL", "section": "Risk Factors"},
            "top_k": 3
        },
        {
            "question": "Tell me about iPhone sales",
            "filters": {"ticker": "AAPL"},
            "top_k": 3
        },
    ]

    print("\n" + "🎯" * 40)
    print("RUNNING EXAMPLE QUERIES")
    print("🎯" * 40)

    for i, example in enumerate(examples, 1):
        print(f"\n📝 Example {i}")
        print(f"   Question: {example['question']}")
        if example.get('filters'):
            print(f"   Filters: {example['filters']}")
        print(f"   Top K: {example['top_k']}")

        input("\nPress Enter to run this query...")

        result = qa_engine.ask(
            question=example['question'],
            filters=example.get('filters'),
            top_k=example.get('top_k', 5)
        )

        print_answer(result)

        if i < len(examples):
            cont = input("Continue to next example? (Y/n): ").strip().lower()
            if cont == 'n':
                break


def interactive_mode(qa_engine: RAGQuestionAnswering):
    """Interactive Q&A loop."""

    print("\n" + "💬" * 40)
    print("INTERACTIVE Q&A MODE")
    print("💬" * 40)
    print()
    print("Ask questions about SEC filings!")
    print("Commands:")
    print("  - Type your question and press Enter")
    print("  - Type 'quit' or 'exit' to stop")
    print("  - Type 'help' for tips")
    print()

    while True:
        # Get question
        print("-" * 80)
        question = input("\n🔍 Your question: ").strip()

        if question.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break

        if question.lower() == 'help':
            print("\n💡 Tips for good questions:")
            print("  - Be specific: 'What is Apple's revenue?' vs 'Tell me about Apple'")
            print("  - Ask about data in SEC filings: revenue, products, risks, etc.")
            print("  - Use filters (ticker, section) to narrow results")
            print()
            print("Example questions:")
            print("  - What is Apple's revenue?")
            print("  - What are the main risk factors?")
            print("  - How much does the company spend on R&D?")
            print("  - What are the key products?")
            continue

        if not question:
            continue

        # Get optional filters
        print("\n⚙️  Optional filters (press Enter to skip):")
        ticker = input("   Ticker (e.g., AAPL): ").strip().upper()
        section = input("   Section (e.g., Risk Factors): ").strip()

        try:
            top_k_input = input("   Number of sources (default 5): ").strip()
            top_k = int(top_k_input) if top_k_input else 5
        except ValueError:
            top_k = 5

        # Build filters
        filters = {}
        if ticker:
            filters['ticker'] = ticker
        if section:
            filters['section'] = section

        # Ask question
        print("\n⏳ Thinking...")

        try:
            result = qa_engine.ask(
                question=question,
                filters=filters if filters else None,
                top_k=top_k
            )

            print_answer(result)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again with a different question.")


def main():
    """Main demo function."""

    print("=" * 80)
    print("Q&A API DEMO - CLI Testing Tool")
    print("=" * 80)
    print()

    # Load environment
    load_dotenv()

    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in .env file")
        print()
        print("Please add your OpenAI API key:")
        print("1. Get key from: https://platform.openai.com/api-keys")
        print("2. Add to .env file: OPENAI_API_KEY=your-key-here")
        return

    # Initialize components
    print("📚 Initializing components...")

    try:
        # Check for Qdrant database
        qdrant_url = os.getenv('QDRANT_URL')

        if qdrant_url:
            print(f"☁️  Using Qdrant Cloud: {qdrant_url}")
            vector_store = QdrantVectorStore(collection_name="sec_filings")
        else:
            qdrant_path = "data/processed/qdrant_storage"
            if not Path(qdrant_path).exists():
                print(f"\n❌ Qdrant database not found at: {qdrant_path}")
                print()
                print("Please run pipeline_demo.py first to process SEC filings:")
                print("   python pipeline_demo.py")
                return

            print(f"💾 Using local Qdrant: {qdrant_path}")
            vector_store = QdrantVectorStore(
                collection_name="sec_filings",
                path=qdrant_path
            )

        # Initialize embeddings
        embedder = EmbeddingGenerator()

        # Initialize Q&A engine
        qa_engine = RAGQuestionAnswering(
            vector_store=vector_store,
            embedder=embedder
        )

        # Get collection info
        info = vector_store.get_collection_info()
        print(f"\n✅ Connected successfully!")
        print(f"   Collection: {info['name']}")
        print(f"   Documents: {info['points_count']}")
        print(f"   Status: {info['status']}")

        # Show model info
        model_info = qa_engine.get_model_info()
        print(f"\n🤖 Q&A Engine:")
        print(f"   Model: {model_info['model']}")
        print(f"   Temperature: {model_info['temperature']}")
        print(f"   Max tokens: {model_info['max_tokens']}")

    except Exception as e:
        print(f"\n❌ Initialization error: {e}")
        import traceback
        traceback.print_exc()
        return

    # Main menu
    while True:
        print("\n" + "=" * 80)
        print("MAIN MENU")
        print("=" * 80)
        print()
        print("1. Run example queries")
        print("2. Interactive Q&A mode")
        print("3. Exit")
        print()

        choice = input("Choose an option (1-3): ").strip()

        if choice == '1':
            run_example_queries(qa_engine)
        elif choice == '2':
            interactive_mode(qa_engine)
        elif choice == '3':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
