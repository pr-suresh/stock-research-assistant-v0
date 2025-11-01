"""
Qdrant Cloud Example

This script demonstrates using Qdrant Cloud for production deployments.

PREREQUISITES:
1. Sign up at https://cloud.qdrant.io (free tier available)
2. Create a cluster
3. Get your cluster URL and API key
4. Add to .env file:
   QDRANT_URL=https://your-cluster-id.cloud.qdrant.io
   QDRANT_API_KEY=your-api-key
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from vector_store import QdrantVectorStore
from embeddings import EmbeddingGenerator
from langchain_core.documents import Document


def main():
    """Demo Qdrant Cloud usage."""

    print("=" * 70)
    print("QDRANT CLOUD EXAMPLE")
    print("=" * 70)
    print()

    # Load environment
    load_dotenv()

    # Check if cloud credentials are set
    qdrant_url = os.getenv('QDRANT_URL')
    qdrant_api_key = os.getenv('QDRANT_API_KEY')

    if not qdrant_url or not qdrant_api_key:
        print("⚠️  Qdrant Cloud credentials not found in .env")
        print()
        print("To use Qdrant Cloud:")
        print("1. Sign up at: https://cloud.qdrant.io")
        print("2. Create a cluster")
        print("3. Add to .env file:")
        print("   QDRANT_URL=https://your-cluster-id.cloud.qdrant.io")
        print("   QDRANT_API_KEY=your-api-key")
        print()
        print("💡 Falling back to local storage for this demo...")

        # Use local storage as fallback
        store = QdrantVectorStore(
            collection_name="sec_filings_demo",
            path="./data/qdrant_demo"
        )
    else:
        # Use Qdrant Cloud
        print("✅ Found Qdrant Cloud credentials")
        print()

        # METHOD 1: Auto-detect from environment (recommended)
        print("METHOD 1: Auto-detect from .env")
        print("-" * 70)
        store = QdrantVectorStore(
            collection_name="sec_filings_demo"
            # Automatically reads QDRANT_URL and QDRANT_API_KEY from .env
        )

        # METHOD 2: Explicit credentials (alternative)
        # print("METHOD 2: Explicit credentials")
        # print("-" * 70)
        # store = QdrantVectorStore(
        #     collection_name="sec_filings_demo",
        #     url=qdrant_url,
        #     api_key=qdrant_api_key
        # )

    print()

    # Get collection info
    info = store.get_collection_info()
    print(f"📊 Collection Info:")
    print(f"   Name: {info['name']}")
    print(f"   Points: {info['points_count']}")
    print(f"   Status: {info['status']}")
    print(f"   Mode: {store.mode}")

    # Create sample documents
    print()
    print("=" * 70)
    print("ADDING SAMPLE DATA")
    print("=" * 70)

    sample_docs = [
        Document(
            page_content="Apple Inc. reported revenue of $391.0 billion for fiscal year 2024, an increase of 7% year-over-year.",
            metadata={
                'ticker': 'AAPL',
                'company': 'Apple Inc.',
                'filing_type': '10-K',
                'filing_date': '2024-09-28',
                'section': 'Financial Highlights'
            }
        ),
        Document(
            page_content="iPhone revenue was $201.2 billion, representing 52% of total company revenue.",
            metadata={
                'ticker': 'AAPL',
                'company': 'Apple Inc.',
                'filing_type': '10-K',
                'filing_date': '2024-09-28',
                'section': 'Products'
            }
        ),
        Document(
            page_content="Services revenue grew 13% to $96.2 billion, driven by App Store and iCloud.",
            metadata={
                'ticker': 'AAPL',
                'company': 'Apple Inc.',
                'filing_type': '10-K',
                'filing_date': '2024-09-28',
                'section': 'Services'
            }
        ),
        Document(
            page_content="Microsoft Corporation's revenue increased 16% to $245.1 billion in fiscal 2024.",
            metadata={
                'ticker': 'MSFT',
                'company': 'Microsoft Corporation',
                'filing_type': '10-K',
                'filing_date': '2024-06-30',
                'section': 'Financial Highlights'
            }
        ),
    ]

    # Generate embeddings
    print("\n🧮 Generating embeddings...")
    embedder = EmbeddingGenerator()
    embeddings = embedder.embed_documents(sample_docs)

    # Add to Qdrant
    print("\n📤 Uploading to Qdrant...")
    point_ids = store.add_documents(sample_docs, embeddings)
    print(f"✅ Uploaded {len(point_ids)} documents")

    # Search examples
    print()
    print("=" * 70)
    print("SEARCH EXAMPLES")
    print("=" * 70)

    # Example 1: General search
    print("\n1️⃣  EXAMPLE 1: General Search")
    print("-" * 70)
    query1 = "What is Apple's revenue?"
    print(f"Query: '{query1}'")

    query_vector1 = embedder.embed_query(query1)
    results1 = store.search(query_vector1, limit=2)

    for i, result in enumerate(results1, 1):
        print(f"\n   Result {i}: [Score: {result['score']:.3f}]")
        print(f"   {result['metadata']['ticker']}: {result['content'][:80]}...")

    # Example 2: Filtered search
    print("\n2️⃣  EXAMPLE 2: Filtered Search (AAPL only)")
    print("-" * 70)
    query2 = "Tell me about iPhone"
    print(f"Query: '{query2}'")
    print(f"Filter: ticker = AAPL")

    query_vector2 = embedder.embed_query(query2)
    results2 = store.search(
        query_vector2,
        limit=2,
        filter={"ticker": "AAPL"}
    )

    for i, result in enumerate(results2, 1):
        print(f"\n   Result {i}: [Score: {result['score']:.3f}]")
        print(f"   Section: {result['metadata']['section']}")
        print(f"   {result['content'][:80]}...")

    # Example 3: Multi-filter search
    print("\n3️⃣  EXAMPLE 3: Multi-Filter Search")
    print("-" * 70)
    query3 = "revenue growth"
    print(f"Query: '{query3}'")
    print(f"Filter: ticker = MSFT AND filing_type = 10-K")

    query_vector3 = embedder.embed_query(query3)
    results3 = store.search(
        query_vector3,
        limit=2,
        filter={
            "ticker": "MSFT",
            "filing_type": "10-K"
        }
    )

    for i, result in enumerate(results3, 1):
        print(f"\n   Result {i}: [Score: {result['score']:.3f}]")
        print(f"   {result['metadata']['company']}")
        print(f"   {result['content']}")

    # Final info
    print()
    print("=" * 70)
    print("✅ DEMO COMPLETE")
    print("=" * 70)

    info = store.get_collection_info()
    print(f"\n📊 Final Collection Stats:")
    print(f"   Total documents: {info['points_count']}")
    print(f"   Collection: {info['name']}")
    print(f"   Storage mode: {store.mode}")

    if store.mode == "cloud":
        print(f"\n☁️  Data is stored in Qdrant Cloud")
        print(f"   View in dashboard: https://cloud.qdrant.io")
    else:
        print(f"\n💾 Data is stored locally")

    print()
    print("🎯 Next steps:")
    print("   1. Add more SEC filings with pipeline_demo.py")
    print("   2. Build a web interface for querying")
    print("   3. Add LLM for answer generation")
    print("   4. Scale to thousands of filings")

    # Cleanup option
    print()
    cleanup = input("\n🗑️  Delete demo collection? (y/N): ").strip().lower()
    if cleanup == 'y':
        store.delete_collection()
        print("✅ Collection deleted")
    else:
        print("💾 Collection kept for further testing")


if __name__ == "__main__":
    main()
