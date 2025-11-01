"""
Query Demo: Search SEC Filings with Qdrant

This script demonstrates how to query the vector database
after running pipeline_demo.py.

USAGE:
1. Run pipeline_demo.py first to populate the database
2. Run this script to search:
   python query_demo.py

3. Try different queries and filters
"""

from pathlib import Path
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from embeddings import EmbeddingGenerator
from vector_store import QdrantVectorStore


def search_filings(
    query: str,
    ticker: str = None,
    filing_type: str = None,
    section: str = None,
    limit: int = 5
):
    """
    Search SEC filings with optional filters.

    Args:
        query: Natural language question
        ticker: Filter by stock ticker (e.g., "AAPL")
        filing_type: Filter by filing type (e.g., "10-K")
        section: Filter by section name
        limit: Number of results
    """
    print("=" * 70)
    print("SEARCHING SEC FILINGS")
    print("=" * 70)

    # Load environment variables
    load_dotenv()

    # Initialize
    print("\n📚 Connecting to vector database...")

    # Check if using cloud or local storage
    import os
    use_cloud = os.getenv('QDRANT_URL') is not None

    if use_cloud:
        print("☁️  Using Qdrant Cloud (from .env)")
        store = QdrantVectorStore(
            collection_name="sec_filings"
        )
    else:
        print("💾 Using local Qdrant storage")
        qdrant_path = Path("data/processed/qdrant_storage")

        if not qdrant_path.exists():
            print(f"\n❌ Vector database not found at: {qdrant_path}")
            print("\n💡 Please run pipeline_demo.py first to create the database:")
            print("   python pipeline_demo.py")
            return

        store = QdrantVectorStore(
            collection_name="sec_filings",
            path=str(qdrant_path)
        )

    # Get database info
    info = store.get_collection_info()
    print(f"✅ Connected to database")
    print(f"   Total documents: {info['points_count']}")

    # Initialize embedder
    print("\n🧮 Generating query embedding...")
    embedder = EmbeddingGenerator()
    query_vector = embedder.embed_query(query)

    # Build filter
    filter_dict = {}
    if ticker:
        filter_dict['ticker'] = ticker
    if filing_type:
        filter_dict['filing_type'] = filing_type
    if section:
        filter_dict['section'] = section

    # Search
    print(f"\n🔍 Searching for: '{query}'")
    if filter_dict:
        print(f"   Filters: {filter_dict}")

    results = store.search(
        query_vector=query_vector,
        limit=limit,
        filter=filter_dict if filter_dict else None
    )

    # Display results
    print(f"\n📄 Found {len(results)} results:")
    print("=" * 70)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. SIMILARITY SCORE: {result['score']:.3f}")
        print("-" * 70)

        # Metadata
        metadata = result['metadata']
        print(f"📊 Ticker: {metadata.get('ticker', 'N/A')}")
        print(f"🏢 Company: {metadata.get('company', 'N/A')}")
        print(f"📋 Filing: {metadata.get('filing_type', 'N/A')} ({metadata.get('filing_date', 'N/A')})")
        print(f"📖 Section: {metadata.get('section', 'N/A')}")

        # Content
        content = result['content']
        print(f"\n📝 Content:")
        print(f"{content[:500]}{'...' if len(content) > 500 else ''}")
        print()

    print("=" * 70)


def interactive_search():
    """Interactive search interface."""
    print("=" * 70)
    print("INTERACTIVE SEC FILING SEARCH")
    print("=" * 70)
    print()
    print("Ask questions about SEC filings!")
    print("Type 'quit' to exit")
    print()

    # Load environment variables
    load_dotenv()

    # Initialize once
    import os
    use_cloud = os.getenv('QDRANT_URL') is not None

    print("📚 Loading database...")

    if use_cloud:
        store = QdrantVectorStore(
            collection_name="sec_filings"
        )
    else:
        qdrant_path = Path("data/processed/qdrant_storage")

        if not qdrant_path.exists():
            print(f"\n❌ Vector database not found at: {qdrant_path}")
            print("\n💡 Please run pipeline_demo.py first")
            return

        store = QdrantVectorStore(
            collection_name="sec_filings",
            path=str(qdrant_path)
        )

    embedder = EmbeddingGenerator()

    info = store.get_collection_info()
    print(f"✅ Ready! Database has {info['points_count']} documents")
    print()

    while True:
        # Get query
        print("-" * 70)
        query = input("\n🔍 Your question: ").strip()

        if query.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break

        if not query:
            continue

        # Optional filters
        ticker = input("   Filter by ticker (optional, press Enter to skip): ").strip().upper()
        ticker = ticker if ticker else None

        # Generate embedding
        print("\n⏳ Searching...")
        query_vector = embedder.embed_query(query)

        # Search
        filter_dict = {"ticker": ticker} if ticker else None
        results = store.search(
            query_vector=query_vector,
            limit=3,
            filter=filter_dict
        )

        # Display results
        print(f"\n📄 Top {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n  {i}. [{result['score']:.3f}] {result['metadata'].get('ticker')} - {result['metadata'].get('section')}")
            print(f"     {result['content'][:150]}...")

        print()


def main():
    """Run demo queries."""

    # Example 1: Simple search
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Simple Search")
    print("=" * 70)
    search_filings(
        query="What is Apple's revenue?",
        limit=3
    )

    input("\nPress Enter to continue to Example 2...")

    # Example 2: Filtered search
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Filtered Search (AAPL only)")
    print("=" * 70)
    search_filings(
        query="What are the main products?",
        ticker="AAPL",
        limit=3
    )

    input("\nPress Enter to continue to Example 3...")

    # Example 3: Section-specific search
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Search Specific Section")
    print("=" * 70)
    search_filings(
        query="What are the risk factors?",
        ticker="AAPL",
        limit=3
    )

    print("\n" + "=" * 70)
    print("\n💡 Next: Try interactive mode!")
    print("   Uncomment interactive_search() at the bottom of this file")
    print()


if __name__ == "__main__":
    import sys

    # Check command line args
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive" or sys.argv[1] == "-i":
            interactive_search()
        else:
            # Custom query from command line
            query = " ".join(sys.argv[1:])
            search_filings(query, limit=5)
    else:
        # Run demo examples
        main()

        # Or run interactive mode
        # interactive_search()
