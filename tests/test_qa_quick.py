"""
Quick Q&A Test Script

Tests the Q&A system with a simple question to verify everything works.
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


def main():
    print("=" * 80)
    print("QUICK Q&A TEST")
    print("=" * 80)
    print()

    # Load environment
    load_dotenv()

    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found")
        print("Please add to .env file")
        return

    print("1. Initializing components...")

    try:
        # Initialize components
        qdrant_url = os.getenv('QDRANT_URL')

        if qdrant_url:
            vector_store = QdrantVectorStore(collection_name="sec_filings")
        else:
            qdrant_path = "data/processed/qdrant_storage"
            if not Path(qdrant_path).exists():
                print(f"❌ Database not found: {qdrant_path}")
                return
            vector_store = QdrantVectorStore(
                collection_name="sec_filings",
                path=qdrant_path
            )

        embedder = EmbeddingGenerator()
        qa_engine = RAGQuestionAnswering(
            vector_store=vector_store,
            embedder=embedder
        )

        print("✅ Components initialized")
        print()

        # Test question
        print("2. Testing Q&A with sample question...")
        print()
        print("   Question: 'What is Apple's revenue?'")
        print("   Filters: ticker=AAPL")
        print("   Top K: 3")
        print()
        print("   Generating answer...")

        result = qa_engine.ask(
            question="What is Apple's revenue?",
            filters={"ticker": "AAPL"},
            top_k=3
        )

        print()
        print("=" * 80)
        print("✅ SUCCESS - Q&A SYSTEM WORKS!")
        print("=" * 80)
        print()
        print("ANSWER:")
        print(result['answer'])
        print()
        print(f"SOURCES: {len(result['sources'])} documents")
        for source in result['sources']:
            print(f"  [{source['id']}] {source['metadata'].get('section', 'N/A')} (score: {source['metadata'].get('score', 0):.3f})")
        print()
        print("METADATA:")
        metadata = result['metadata']
        print(f"  Model: {metadata.get('model')}")
        print(f"  Tokens: {metadata.get('total_tokens')} (cost: ${metadata.get('estimated_cost_usd', 0):.4f})")
        print(f"  Time: {metadata.get('total_time_ms', 0):.0f}ms")
        print()
        print("=" * 80)
        print()
        print("🎉 Q&A system is ready to use!")
        print()
        print("Next steps:")
        print("  1. Try more questions: python qa_api_demo.py")
        print("  2. Start API: uvicorn api:app --reload --port 8000")
        print("  3. Visit: http://localhost:8000/docs")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
