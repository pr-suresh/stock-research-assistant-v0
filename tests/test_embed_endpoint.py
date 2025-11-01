"""
Test the /embed endpoint with sample data.

This script demonstrates how to:
1. Prepare chunks for embedding
2. Call the /embed endpoint
3. Inspect the embeddings returned

Requirements:
- API server running: python api.py or uvicorn api:app
- OPENAI_API_KEY set in environment or .env file
"""

import requests
import json
from pprint import pprint

# API endpoint
BASE_URL = "http://localhost:8000"

# Test data: Sample chunks from a financial document
test_chunks = {
    "chunks": [
        {
            "content": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables and accessories, and sells a variety of related services.",
            "metadata": {
                "chunk_index": 0,
                "source": "Apple 10-K 2024",
                "section": "Business",
                "word_count": 23
            }
        },
        {
            "content": "The iPhone is the Company's line of smartphones based on its iOS operating system. The iPhone line includes iPhone 16 Pro, iPhone 16, iPhone 15, iPhone 14 and iPhone SE.",
            "metadata": {
                "chunk_index": 1,
                "source": "Apple 10-K 2024",
                "section": "Products",
                "word_count": 30
            }
        },
        {
            "content": "The Company believes the duration of its intellectual property rights is adequate relative to the expected lives of its products and services.",
            "metadata": {
                "chunk_index": 2,
                "source": "Apple 10-K 2024",
                "section": "Intellectual Property",
                "word_count": 21
            }
        },
        {
            "content": "As of September 28, 2024, the Company had approximately 164,000 full-time equivalent employees worldwide.",
            "metadata": {
                "chunk_index": 3,
                "source": "Apple 10-K 2024",
                "section": "Human Capital",
                "word_count": 15
            }
        }
    ]
}


def test_embed_endpoint():
    """Test the /embed endpoint."""
    print("=" * 70)
    print("TESTING /embed ENDPOINT")
    print("=" * 70)
    print()
    
    print(f"📤 Sending {len(test_chunks['chunks'])} chunks to {BASE_URL}/embed")
    print()
    
    # Show what we're sending
    print("Sample chunk:")
    pprint(test_chunks['chunks'][0])
    print()
    
    try:
        # Make request
        response = requests.post(
            f"{BASE_URL}/embed",
            json=test_chunks,
            headers={"Content-Type": "application/json"}
        )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            
            print("✅ SUCCESS!")
            print()
            print("=" * 70)
            print("RESPONSE")
            print("=" * 70)
            print()
            
            # Show embeddings info
            embeddings = result["embeddings"]
            print(f"📊 Generated {len(embeddings)} embeddings")
            print()
            
            # Show first embedding details
            first_embedding = embeddings[0]
            print("First embedding details:")
            print(f"  Content: {first_embedding['content'][:100]}...")
            print(f"  Metadata: {first_embedding['metadata']}")
            print(f"  Embedding dimension: {first_embedding['embedding_dim']}")
            print(f"  First 5 values: {first_embedding['embedding'][:5]}")
            print()
            
            # Show cost info
            cost_info = result["cost_info"]
            print("💰 Cost Information:")
            print(f"  Documents: {cost_info['num_documents']}")
            print(f"  Total characters: {cost_info['total_characters']:,}")
            print(f"  Estimated tokens: {cost_info['estimated_tokens']:,}")
            print(f"  Estimated cost: ${cost_info['estimated_cost_usd']:.6f}")
            print(f"  Cost per document: ${cost_info['cost_per_doc_usd']:.8f}")
            print()
            
            # Save full response for inspection
            output_file = "data/test_embeddings.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"💾 Full response saved to: {output_file}")
            print()
            
            # Show example use case
            print("=" * 70)
            print("EXAMPLE: Semantic Similarity Check")
            print("=" * 70)
            print()
            print("You can now compare embeddings to find similar content:")
            print()
            print("from numpy import dot")
            print("from numpy.linalg import norm")
            print()
            print("def cosine_similarity(vec1, vec2):")
            print("    return dot(vec1, vec2) / (norm(vec1) * norm(vec2))")
            print()
            print("# Compare first two chunks")
            print("similarity = cosine_similarity(")
            print("    embeddings[0]['embedding'],")
            print("    embeddings[1]['embedding']")
            print(")")
            print(f"# Chunks about similar topics should have high similarity (>0.7)")
            print()
            
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to API")
        print()
        print("Make sure the API server is running:")
        print("  python api.py")
        print("  or")
        print("  uvicorn api:app --reload")
        print()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")


def test_minimal_embed():
    """Test with minimal data - just required fields."""
    print()
    print("=" * 70)
    print("TESTING WITH MINIMAL DATA")
    print("=" * 70)
    print()
    
    minimal_data = {
        "chunks": [
            {
                "content": "This is a simple test chunk."
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/embed",
            json=minimal_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Minimal request works!")
            print(f"   Embedding dimension: {result['embeddings'][0]['embedding_dim']}")
            print()
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    print()
    print("🧪 Testing Embedding Endpoint")
    print()
    
    # Test with full data
    test_embed_endpoint()
    
    # Test with minimal data
    test_minimal_embed()
    
    print("=" * 70)
    print("✅ TESTING COMPLETE")
    print("=" * 70)
    print()

