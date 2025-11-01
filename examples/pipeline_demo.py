"""
Complete RAG Pipeline: Parse → Chunk → Embed

This script demonstrates the full pipeline from SEC filing to embedded chunks
ready for vector database storage.

PIPELINE STEPS:
1. Parse HTML → Clean text
2. Chunk text → Small pieces
3. Embed chunks → Vectors
4. (Next: Store in vector DB)
"""

from pathlib import Path
import sys
import json
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from sec_parser import SECFilingParser
from text_chunker import TextChunker
from embeddings import EmbeddingGenerator
from vector_store import QdrantVectorStore


def main():
    """Run the complete pipeline."""
    
    print("=" * 70)
    print("RAG PIPELINE: Parse → Chunk → Embed")
    print("=" * 70)
    print()
    
    # Load environment variables
    load_dotenv()
    
    # ========================================
    # STEP 1: PARSE
    # ========================================
    print("📄 STEP 1: Parsing SEC Filing")
    print("-" * 70)
    
    # Use relative path from project root
    filing_path = Path(__file__).parent / "data/filings/0000320193_0000320193-24-000123_aapl-20240928.htm"

    if not filing_path.exists():
        print(f"❌ File not found: {filing_path}")
        print(f"\n💡 Please place your SEC filing HTML file at:")
        print(f"   {filing_path}")
        return
    
    parser = SECFilingParser(filing_path)
    result = parser.parse()
    
    print(f"✅ Parsed {result['stats']['clean_text_length']:,} characters")
    print(f"✅ Found {result['stats']['num_sections']} sections")
    
    # ========================================
    # STEP 2: CHUNK
    # ========================================
    print("\n📦 STEP 2: Chunking Text")
    print("-" * 70)
    
    # Let's compare different chunking strategies
    print("\nTrying different strategies...")
    
    # Strategy 1: Recursive (recommended)
    chunker_recursive = TextChunker(
        chunk_size=1000,      # ~250 words
        chunk_overlap=200,    # 20% overlap
        strategy="recursive"
    )
    
    # Strategy 2: Section-based (preserves document structure)
    chunker_sections = TextChunker(
        chunk_size=2000,      # Larger for sections
        chunk_overlap=200,
        strategy="recursive"  # Used for large sections
    )
    
    # Chunk using recursive strategy
    print("\n1. Recursive chunking (whole document):")
    docs_recursive = chunker_recursive.chunk_text(
        result['clean_text'],
        metadata={
            'source': filing_path.name,
            'company': 'Apple Inc.',
            'ticker': 'AAPL',
            'filing_date': '2024-09-28',
            'filing_type': '10-K'
        }
    )
    stats_recursive = chunker_recursive.analyze_chunks(docs_recursive)
    print(f"   Chunks: {stats_recursive['num_chunks']}")
    print(f"   Avg size: {stats_recursive['avg_chunk_size']:.0f} chars")
    
    # Chunk using sections
    print("\n2. Section-based chunking (preserves structure):")
    docs_sections = chunker_sections.chunk_sections(
        result['sections'],
        base_metadata={
            'source': filing_path.name,
            'company': 'Apple Inc.',
            'ticker': 'AAPL',
            'filing_date': '2024-09-28',
            'filing_type': '10-K'
        }
    )
    stats_sections = chunker_sections.analyze_chunks(docs_sections)
    print(f"   Chunks: {stats_sections['num_chunks']}")
    print(f"   Sections: {stats_sections['num_sections']}")
    print(f"   Avg size: {stats_sections['avg_chunk_size']:.0f} chars")
    
    # Let's use section-based for better structure
    print("\n✅ Using section-based chunking (better for SEC filings)")
    chosen_docs = docs_sections
    
    # Save chunks for inspection
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    chunker_sections.save_chunks(
        chosen_docs,
        output_dir / "apple_10k_chunks.json"
    )
    
    # ========================================
    # STEP 3: EMBED
    # ========================================
    print("\n🧮 STEP 3: Generating Embeddings")
    print("-" * 70)
    
    try:
        embedder = EmbeddingGenerator()
        
        # Estimate cost
        cost_info = embedder.estimate_cost(chosen_docs)
        print(f"\nEstimated cost:")
        print(f"   Documents: {cost_info['num_documents']}")
        print(f"   Tokens: ~{cost_info['estimated_tokens']:,}")
        print(f"   Cost: ${cost_info['estimated_cost_usd']:.4f}")
        
        # Generate embeddings
        print(f"\nGenerating embeddings...")
        vectors = embedder.embed_documents(chosen_docs)
        
        print(f"✅ Generated {len(vectors)} embeddings")
        print(f"   Dimension: {len(vectors[0])}")
        
        # Save embeddings and documents together
        print(f"\nSaving embeddings...")
        embeddings_data = []
        for doc, vector in zip(chosen_docs, vectors):
            embeddings_data.append({
                'content': doc.page_content,
                'metadata': doc.metadata,
                'embedding': vector
            })
        
        embeddings_path = output_dir / "apple_10k_embeddings.json"
        with open(embeddings_path, 'w') as f:
            json.dump(embeddings_data, f)

        print(f"💾 Saved to: {embeddings_path}")

        # ========================================
        # STEP 4: STORE IN QDRANT
        # ========================================
        print("\n📦 STEP 4: Storing in Qdrant Vector Database")
        print("-" * 70)

        try:
            # Initialize Qdrant
            # AUTO-DETECTS: Cloud (from .env) or local storage
            import os
            use_cloud = os.getenv('QDRANT_URL') is not None

            if use_cloud:
                print("☁️  Using Qdrant Cloud (from .env)")
                store = QdrantVectorStore(
                    collection_name="sec_filings"
                    # Reads QDRANT_URL and QDRANT_API_KEY from .env
                )
            else:
                print("💾 Using local Qdrant storage")
                qdrant_path = output_dir / "qdrant_storage"
                store = QdrantVectorStore(
                    collection_name="sec_filings",
                    path=str(qdrant_path)
                )

            # Add documents to Qdrant
            print(f"\nUploading {len(chosen_docs)} documents to Qdrant...")
            point_ids = store.add_documents(chosen_docs, vectors)

            # Get collection info
            info = store.get_collection_info()
            print(f"\n✅ Stored in Qdrant:")
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
            print(f"\n⚠️  Qdrant storage failed: {e}")
            print("   Embeddings are still saved to JSON for backup")

    # ========================================
    # SUMMARY
    # ========================================
    print("\n" + "=" * 70)
    print("✅ PIPELINE COMPLETE")
    print("=" * 70)

    print(f"\n📊 Summary:")
    print(f"   Input: {filing_path.name}")
    print(f"   Parsed: {result.get('stats', {}).get('clean_text_length', 0):,} characters")
    print(f"   Chunks: {len(chosen_docs)}")
    print(f"   Embeddings: {len(vectors)} vectors")
    print(f"   Cost: ${cost_info['estimated_cost_usd']:.4f}")
    print(f"   Stored in: Qdrant vector database")

    print(f"\n📁 Output files:")
    print(f"   1. {output_dir / 'apple_10k_chunks.json'}")
    print(f"   2. {output_dir / 'apple_10k_embeddings.json'}")
    if use_cloud:
        print(f"   3. Qdrant Cloud (https://cloud.qdrant.io)")
    else:
        print(f"   3. {qdrant_path}/ (Local Qdrant storage)")

    print(f"\n🎯 Next steps:")
    print(f"   1. Run query_demo.py to search the vector database")
    print(f"   2. Build RAG system with LLM for answer generation")
    print(f"   3. Add more SEC filings to the database")

    # Show sample chunk
    print(f"\n" + "=" * 70)
    print("SAMPLE CHUNK")
    print("=" * 70)
    sample = chosen_docs[0]
    print(f"Section: {sample.metadata.get('section', 'N/A')}")
    print(f"Length: {len(sample.page_content)} chars")
    print(f"\nContent preview:")
    print(sample.page_content[:500] + "...")
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 To fix:")
        print("   1. Get OpenAI API key from: https://platform.openai.com/api-keys")
        print("   2. Create .env file (see .env.example)")
        print("   3. Add: OPENAI_API_KEY=your-key-here")
        return
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    main()