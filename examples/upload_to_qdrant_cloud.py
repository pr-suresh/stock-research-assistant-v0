"""
Upload Existing Chunks to Qdrant Cloud

This script takes already-generated chunks from JSON files,
generates embeddings, and uploads them to Qdrant Cloud.

USAGE:
1. Set up Qdrant Cloud credentials in .env:
   QDRANT_URL=https://your-cluster.cloud.qdrant.io
   QDRANT_API_KEY=your-api-key

2. Run this script:
   python upload_to_qdrant_cloud.py

WHY THIS SCRIPT:
- Avoids re-parsing SEC filings
- Uses existing chunks
- Just generates embeddings and uploads to cloud
"""

from pathlib import Path
import sys
import json
from dotenv import load_dotenv
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from embeddings import EmbeddingGenerator
from vector_store import QdrantVectorStore
from langchain_core.documents import Document


def load_chunks_from_json(json_path: Path) -> list[Document]:
    """
    Load chunks from JSON file and convert to LangChain Documents.

    Args:
        json_path: Path to chunks JSON file

    Returns:
        List of Document objects
    """
    print(f"📂 Loading chunks from: {json_path}")

    with open(json_path, 'r') as f:
        chunks_data = json.load(f)

    # Convert to LangChain Documents
    documents = []
    for chunk in chunks_data:
        doc = Document(
            page_content=chunk['content'],  # Field is 'content' in JSON
            metadata=chunk['metadata']
        )
        documents.append(doc)

    print(f"✅ Loaded {len(documents)} chunks")
    return documents


def main():
    """Upload chunks to Qdrant Cloud."""

    print("=" * 70)
    print("UPLOAD TO QDRANT CLOUD")
    print("=" * 70)
    print()

    # Load environment variables
    load_dotenv()

    # Check for Qdrant Cloud credentials
    qdrant_url = os.getenv('QDRANT_URL')
    qdrant_api_key = os.getenv('QDRANT_API_KEY')

    if not qdrant_url or not qdrant_api_key:
        print("❌ Qdrant Cloud credentials not found in .env")
        print()
        print("To use Qdrant Cloud:")
        print("1. Sign up at: https://cloud.qdrant.io")
        print("2. Create a cluster")
        print("3. Add to .env file:")
        print("   QDRANT_URL=https://your-cluster-id.cloud.qdrant.io")
        print("   QDRANT_API_KEY=your-api-key")
        print()
        return

    # Check for chunks file
    chunks_path = Path("data/processed/apple_10k_chunks.json")

    if not chunks_path.exists():
        print(f"❌ Chunks file not found: {chunks_path}")
        print()
        print("Please run pipeline_demo.py first to generate chunks:")
        print("   python pipeline_demo.py")
        return

    # ========================================
    # STEP 1: LOAD CHUNKS
    # ========================================
    print("STEP 1: Loading Chunks")
    print("-" * 70)

    documents = load_chunks_from_json(chunks_path)

    print(f"\n📊 Chunk Statistics:")
    print(f"   Total chunks: {len(documents)}")

    # Show sample metadata
    if documents:
        sample = documents[0]
        print(f"\n   Sample metadata:")
        for key, value in sample.metadata.items():
            print(f"      {key}: {value}")

    # ========================================
    # STEP 2: GENERATE EMBEDDINGS
    # ========================================
    print("\n" + "=" * 70)
    print("STEP 2: Generating Embeddings")
    print("-" * 70)

    try:
        embedder = EmbeddingGenerator()

        # Estimate cost
        cost_info = embedder.estimate_cost(documents)
        print(f"\n💰 Estimated cost:")
        print(f"   Documents: {cost_info['num_documents']}")
        print(f"   Tokens: ~{cost_info['estimated_tokens']:,}")
        print(f"   Cost: ${cost_info['estimated_cost_usd']:.4f}")

        # Ask for confirmation
        print()
        proceed = input("Generate embeddings? (y/N): ").strip().lower()
        if proceed != 'y':
            print("❌ Cancelled")
            return

        # Generate embeddings
        print(f"\n⏳ Generating embeddings for {len(documents)} documents...")
        vectors = embedder.embed_documents(documents)

        print(f"✅ Generated {len(vectors)} embeddings")
        print(f"   Dimension: {len(vectors[0])}")

    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 To fix:")
        print("   1. Get OpenAI API key from: https://platform.openai.com/api-keys")
        print("   2. Add to .env: OPENAI_API_KEY=your-key-here")
        return

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return

    # ========================================
    # STEP 3: UPLOAD TO QDRANT CLOUD
    # ========================================
    print("\n" + "=" * 70)
    print("STEP 3: Uploading to Qdrant Cloud")
    print("-" * 70)

    try:
        # Initialize Qdrant Cloud
        print(f"\n☁️  Connecting to Qdrant Cloud...")
        print(f"   URL: {qdrant_url}")

        store = QdrantVectorStore(
            collection_name="sec_filings"
            # Automatically reads QDRANT_URL and QDRANT_API_KEY from .env
        )

        # Upload documents
        print(f"\n📤 Uploading {len(documents)} documents to Qdrant Cloud...")
        point_ids = store.add_documents(documents, vectors)

        # Get collection info
        info = store.get_collection_info()
        print(f"\n✅ Upload complete!")
        print(f"   Collection: {info['name']}")
        print(f"   Total points: {info['points_count']}")
        print(f"   Status: {info['status']}")

        # Test search
        print(f"\n🔍 Testing similarity search...")
        test_query = "What is Apple's revenue?"
        test_query_vector = embedder.embed_query(test_query)

        search_results = store.search(
            test_query_vector,
            limit=3,
            filter={"ticker": "AAPL"}
        )

        print(f"\n   Query: '{test_query}'")
        print(f"   Found {len(search_results)} results:")
        for i, result in enumerate(search_results, 1):
            print(f"\n   {i}. Score: {result['score']:.3f}")
            print(f"      Section: {result['metadata'].get('section', 'N/A')}")
            print(f"      Preview: {result['content'][:100]}...")

    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "=" * 70)
    print("✅ UPLOAD COMPLETE")
    print("=" * 70)

    print(f"\n📊 Summary:")
    print(f"   Source: {chunks_path}")
    print(f"   Chunks: {len(documents)}")
    print(f"   Embeddings: {len(vectors)}")
    print(f"   Cost: ${cost_info['estimated_cost_usd']:.4f}")
    print(f"   Storage: Qdrant Cloud")
    print(f"   Collection: sec_filings")

    print(f"\n🎯 Next steps:")
    print(f"   1. View your data at: https://cloud.qdrant.io")
    print(f"   2. Query with: python query_demo.py -i")
    print(f"   3. Share collection with team members")
    print(f"   4. Add more SEC filings to expand the database")

    print()


if __name__ == "__main__":
    main()
