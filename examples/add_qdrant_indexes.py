"""
Add Payload Indexes to Existing Qdrant Collection

This script adds indexes to your Qdrant collection so you can filter by fields
like ticker, filing_type, and section.

WHY: Qdrant Cloud requires indexes for filtering, unlike local storage.

USAGE:
    python add_qdrant_indexes.py
"""

from pathlib import Path
import sys
from dotenv import load_dotenv
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType


def main():
    """Add indexes to existing collection."""

    print("=" * 70)
    print("ADD QDRANT PAYLOAD INDEXES")
    print("=" * 70)
    print()

    # Load environment variables
    load_dotenv()

    # Check for Qdrant credentials
    qdrant_url = os.getenv('QDRANT_URL')
    qdrant_api_key = os.getenv('QDRANT_API_KEY')

    if qdrant_url and qdrant_api_key:
        print(f"☁️  Connecting to Qdrant Cloud: {qdrant_url}")
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    else:
        # Use local storage
        local_path = "data/processed/qdrant_storage"
        print(f"💾 Connecting to local storage: {local_path}")
        client = QdrantClient(path=local_path)

    collection_name = "sec_filings"

    # Check if collection exists
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]

    if collection_name not in collection_names:
        print(f"❌ Collection '{collection_name}' not found")
        print("\nAvailable collections:", collection_names if collection_names else "None")
        return

    print(f"✅ Found collection: {collection_name}")

    # Add indexes
    print("\n📊 Adding payload indexes...")

    indexes = [
        ("ticker", "Filter by stock ticker (e.g., AAPL, MSFT)"),
        ("filing_type", "Filter by document type (e.g., 10-K, 10-Q)"),
        ("section", "Filter by section (e.g., Business, Risk Factors)"),
        ("company", "Filter by company name"),
    ]

    for field_name, description in indexes:
        try:
            client.create_payload_index(
                collection_name=collection_name,
                field_name=field_name,
                field_schema=PayloadSchemaType.KEYWORD
            )
            print(f"   ✅ Created index: {field_name} - {description}")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"   ⏭️  Index already exists: {field_name}")
            else:
                print(f"   ⚠️  Failed to create index {field_name}: {e}")

    print()
    print("=" * 70)
    print("✅ INDEXES ADDED")
    print("=" * 70)
    print()
    print("You can now use filters in your searches:")
    print("   filter={'ticker': 'AAPL'}")
    print("   filter={'filing_type': '10-K'}")
    print("   filter={'section': 'Business'}")
    print()


if __name__ == "__main__":
    main()
