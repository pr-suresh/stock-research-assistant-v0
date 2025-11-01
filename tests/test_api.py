"""
Test API Client

Simple script to test all API endpoints programmatically.

Usage:
    # Start API first:
    .venv/bin/uvicorn api:app --reload --port 8000
    
    # Then run this:
    .venv/bin/python test_api.py
"""

import requests
from pathlib import Path
import json


BASE_URL = "http://localhost:8000"


def test_health():
    """Test health check endpoint."""
    print("\n" + "=" * 60)
    print("TEST: Health Check")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200


def test_parse():
    """Test parse endpoint."""
    print("\n" + "=" * 60)
    print("TEST: Parse HTML")
    print("=" * 60)
    
    # Use the Apple 10-K file
    file_path = Path("/mnt/user-data/uploads/0000320193_0000320193-24-000123_aapl-20240928.htm")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return None
    
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f, 'text/html')}
        response = requests.post(f"{BASE_URL}/parse", files=files)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success!")
        print(f"   Clean text: {len(data['clean_text']):,} chars")
        print(f"   Sections: {data['stats']['num_sections']}")
        print(f"   Sections found: {list(data['sections'].keys())}")
        return data
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_chunk(text):
    """Test chunk endpoint."""
    print("\n" + "=" * 60)
    print("TEST: Chunk Text")
    print("=" * 60)
    
    # Use just the first 10,000 characters for testing
    sample_text = text[:10000]
    
    payload = {
        "text": sample_text,
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "strategy": "recursive",
        "metadata": {
            "source": "test",
            "company": "Apple"
        }
    }
    
    response = requests.post(f"{BASE_URL}/chunk", json=payload)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success!")
        print(f"   Chunks created: {len(data['chunks'])}")
        print(f"   Avg chunk size: {data['stats']['avg_chunk_size']:.0f} chars")
        print(f"   Total chunks: {data['stats']['num_chunks']}")
        
        # Show first chunk
        if data['chunks']:
            first_chunk = data['chunks'][0]
            print(f"\n   First chunk preview:")
            print(f"   {first_chunk['content'][:200]}...")
        
        return data
    else:
        print(f"❌ Error: {response.text}")
        return None


def test_embed(chunks):
    """Test embed endpoint."""
    print("\n" + "=" * 60)
    print("TEST: Generate Embeddings")
    print("=" * 60)
    
    # Use just first 3 chunks for testing (save API costs)
    sample_chunks = chunks[:3]
    
    payload = {
        "chunks": sample_chunks
    }
    
    response = requests.post(f"{BASE_URL}/embed", json=payload)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success!")
        print(f"   Embeddings created: {len(data['embeddings'])}")
        if data['embeddings']:
            print(f"   Embedding dimension: {data['embeddings'][0]['embedding_dim']}")
        print(f"\n   Cost estimate:")
        for key, value in data['cost_info'].items():
            print(f"   {key}: {value}")
        return data
    else:
        print(f"❌ Error: {response.text}")
        print(f"\n💡 Tip: Make sure OPENAI_API_KEY is set in .env file")
        return None


def test_full_pipeline():
    """Test full pipeline endpoint."""
    print("\n" + "=" * 60)
    print("TEST: Full Pipeline")
    print("=" * 60)
    
    file_path = Path("/mnt/user-data/uploads/0000320193_0000320193-24-000123_aapl-20240928.htm")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return None
    
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f, 'text/html')}
        params = {
            'chunk_size': 1000,
            'chunk_overlap': 200,
            'chunk_strategy': 'recursive'
        }
        response = requests.post(
            f"{BASE_URL}/pipeline/full",
            files=files,
            params=params
        )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Success!")
        print(f"\n   Parse stats:")
        for key, value in data['parse_stats'].items():
            print(f"   {key}: {value}")
        print(f"\n   Chunk stats:")
        for key, value in data['chunk_stats'].items():
            if key != 'sections':  # Skip long lists
                print(f"   {key}: {value}")
        print(f"\n   Cost info:")
        for key, value in data['cost_info'].items():
            print(f"   {key}: {value}")
        print(f"\n   {data['message']}")
        return data
    else:
        print(f"❌ Error: {response.text}")
        return None


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("API CLIENT TEST SUITE")
    print("=" * 70)
    print(f"\nBase URL: {BASE_URL}")
    print("\nMake sure API is running:")
    print("  .venv/bin/uvicorn api:app --reload --port 8000")
    print("\n" + "=" * 70)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ API is not running!")
        print("Start it with: .venv/bin/uvicorn api:app --reload --port 8000")
        return
    
    # Test 2: Parse
    parse_result = test_parse()
    if not parse_result:
        print("\n❌ Parse test failed")
        return
    
    # Test 3: Chunk
    chunk_result = test_chunk(parse_result['clean_text'])
    if not chunk_result:
        print("\n❌ Chunk test failed")
        return
    
    # Test 4: Embed (may fail if no API key)
    embed_result = test_embed(chunk_result['chunks'])
    if embed_result:
        print("\n✅ All tests passed!")
    else:
        print("\n⚠️  Embedding test failed (check OPENAI_API_KEY)")
        print("   But other endpoints work!")
    
    # Optional: Test full pipeline
    # Uncomment if you want to test the complete flow
    # print("\n\nBonus: Testing full pipeline...")
    # test_full_pipeline()
    
    print("\n" + "=" * 70)
    print("TESTS COMPLETE")
    print("=" * 70)
    print("\n🎯 Next: Open http://localhost:8000/docs to test in Swagger UI!")


if __name__ == "__main__":
    main()