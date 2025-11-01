"""
Qdrant Vector Store for SEC Filings

WHAT IS QDRANT:
Qdrant is a vector database optimized for similarity search.
It stores embeddings + metadata and enables fast retrieval.

WHY QDRANT:
1. Fast similarity search (millions of vectors)
2. Rich metadata filtering (filter by ticker, date, section, etc.)
3. Easy to use Python SDK
4. Can run locally (Docker) or cloud
5. Open source

USAGE:
1. Start Qdrant locally:
   docker run -p 6333:6333 qdrant/qdrant

2. Store documents:
   store = QdrantVectorStore("sec_filings")
   store.add_documents(documents, embeddings)

3. Search with filters:
   results = store.search(
       query_vector=query_embedding,
       filter={"ticker": "AAPL"},
       limit=5
   )
"""

from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType
)
import uuid
import os
from pathlib import Path


class QdrantVectorStore:
    """
    Vector store using Qdrant for SEC filing embeddings.

    METADATA SCHEMA:
    - ticker: str (e.g., "AAPL")
    - company: str (e.g., "Apple Inc.")
    - source: str (filename)
    - filing_type: str (e.g., "10-K", "10-Q")
    - filing_date: str (e.g., "2024-09-28")
    - section: str (e.g., "Business", "Risk Factors")
    - page: int (optional)
    """

    def __init__(
        self,
        collection_name: str = "sec_filings",
        host: str = "localhost",
        port: int = 6333,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        vector_size: int = 1536,  # text-embedding-3-small dimension
        distance: Distance = Distance.COSINE,
        path: Optional[str] = None,
        use_env: bool = True
    ):
        """
        Initialize Qdrant vector store.

        Args:
            collection_name: Name for the vector collection
            host: Qdrant server host (for local deployment)
            port: Qdrant server port
            url: Full Qdrant URL (for cloud deployment)
            api_key: API key for Qdrant Cloud
            vector_size: Embedding dimension (1536 for text-embedding-3-small)
            distance: Distance metric (COSINE recommended for embeddings)
            path: Local path for persistent storage (alternative to server)
            use_env: Read credentials from environment variables

        CONNECTION OPTIONS:
        1. Local persistent storage (default, no setup needed):
           QdrantVectorStore(path="./qdrant_data")

        2. Qdrant Cloud (with environment variables):
           Set in .env:
               QDRANT_URL=https://xxx.cloud.qdrant.io
               QDRANT_API_KEY=your-api-key
           Then:
               QdrantVectorStore()  # Auto-detects cloud config

        3. Qdrant Cloud (explicit):
           QdrantVectorStore(
               url="https://xxx.cloud.qdrant.io",
               api_key="your-key"
           )

        4. Local server (Docker):
           QdrantVectorStore(host="localhost", port=6333)

        ENVIRONMENT VARIABLES:
        - QDRANT_URL: Full URL to Qdrant instance
        - QDRANT_API_KEY: API key for authentication
        - QDRANT_USE_CLOUD: Set to "true" to force cloud mode
        """
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.distance = distance

        # Read from environment if enabled
        if use_env:
            env_url = os.getenv('QDRANT_URL')
            env_api_key = os.getenv('QDRANT_API_KEY')
            use_cloud = os.getenv('QDRANT_USE_CLOUD', '').lower() == 'true'

            # Override with env vars if present
            if env_url and not url:
                url = env_url
            if env_api_key and not api_key:
                api_key = env_api_key

        # Initialize client based on priority
        if path:
            # Local persistent storage (no server needed)
            self.client = QdrantClient(path=path)
            self.mode = "local_storage"
            print(f"✅ Connected to local Qdrant storage: {path}")
        elif url:
            # Qdrant Cloud or custom URL
            self.client = QdrantClient(url=url, api_key=api_key)
            self.mode = "cloud"
            # Mask API key in output
            masked_key = f"{api_key[:8]}..." if api_key and len(api_key) > 8 else "***"
            print(f"✅ Connected to Qdrant Cloud: {url}")
            print(f"   API Key: {masked_key}")
        else:
            # Local server (Docker)
            self.client = QdrantClient(host=host, port=port)
            self.mode = "local_server"
            print(f"✅ Connected to Qdrant server: {host}:{port}")

        # Create collection if it doesn't exist
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=self.distance
                )
            )
            print(f"✅ Created collection: {self.collection_name}")

            # Create payload indexes for filtering (required for cloud)
            # This enables fast filtering by these fields
            self._create_payload_indexes()
        else:
            print(f"✅ Using existing collection: {self.collection_name}")

    def _create_payload_indexes(self):
        """Create indexes on commonly-filtered fields."""
        try:
            # Index on ticker for filtering by stock symbol
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="ticker",
                field_schema=PayloadSchemaType.KEYWORD
            )

            # Index on filing_type for filtering by document type
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="filing_type",
                field_schema=PayloadSchemaType.KEYWORD
            )

            # Index on section for filtering by document section
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="section",
                field_schema=PayloadSchemaType.KEYWORD
            )

            print(f"✅ Created payload indexes for filtering")
        except Exception as e:
            # Indexes might already exist, that's okay
            pass

    def add_documents(
        self,
        documents: List[Document],
        embeddings: List[List[float]],
        batch_size: int = 100
    ) -> List[str]:
        """
        Add documents with embeddings to Qdrant.

        Args:
            documents: List of LangChain Document objects
            embeddings: List of embedding vectors (same length as documents)
            batch_size: Number of documents to upload at once

        Returns:
            List of point IDs

        WHAT HAPPENS:
        1. Each document + embedding → Qdrant point
        2. Metadata extracted and stored
        3. UUID generated for each point
        4. Batched upload for efficiency
        """
        if len(documents) != len(embeddings):
            raise ValueError(
                f"Documents ({len(documents)}) and embeddings ({len(embeddings)}) "
                "must have same length"
            )

        print(f"📤 Uploading {len(documents)} documents to Qdrant...")

        # Prepare points
        points = []
        point_ids = []

        for doc, embedding in zip(documents, embeddings):
            point_id = str(uuid.uuid4())
            point_ids.append(point_id)

            # Prepare metadata (Qdrant calls it "payload")
            payload = {
                'content': doc.page_content,
                **doc.metadata  # Include all metadata
            }

            # Create point
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload
            )
            points.append(point)

        # Upload in batches
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
            print(f"   Uploaded {i + len(batch)}/{len(points)}")

        print(f"✅ Successfully uploaded {len(points)} documents")
        return point_ids

    def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query_vector: Query embedding vector
            limit: Number of results to return
            filter: Metadata filters (e.g., {"ticker": "AAPL"})
            score_threshold: Minimum similarity score

        Returns:
            List of search results with content, metadata, and score

        EXAMPLES:

        1. Simple search:
           results = store.search(query_vector, limit=5)

        2. Filter by ticker:
           results = store.search(
               query_vector,
               filter={"ticker": "AAPL"}
           )

        3. Filter by multiple fields:
           results = store.search(
               query_vector,
               filter={
                   "ticker": "AAPL",
                   "filing_type": "10-K"
               }
           )

        4. Only high-confidence results:
           results = store.search(
               query_vector,
               score_threshold=0.7
           )
        """
        # Build Qdrant filter
        qdrant_filter = None
        if filter:
            conditions = [
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                )
                for key, value in filter.items()
            ]
            qdrant_filter = Filter(must=conditions)

        # Search
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=qdrant_filter,
            score_threshold=score_threshold
        )

        # Format results
        results = []
        for hit in search_results:
            result = {
                'id': hit.id,
                'score': hit.score,
                'content': hit.payload.get('content', ''),
                'metadata': {
                    k: v for k, v in hit.payload.items()
                    if k != 'content'
                }
            }
            results.append(result)

        return results

    def delete_by_filter(self, filter: Dict[str, Any]) -> int:
        """
        Delete documents matching filter.

        Args:
            filter: Metadata filters

        Returns:
            Number of documents deleted

        EXAMPLES:

        1. Delete all documents from a ticker:
           count = store.delete_by_filter({"ticker": "AAPL"})

        2. Delete specific filing:
           count = store.delete_by_filter({
               "ticker": "AAPL",
               "filing_date": "2024-09-28"
           })
        """
        conditions = [
            FieldCondition(
                key=key,
                match=MatchValue(value=value)
            )
            for key, value in filter.items()
        ]

        result = self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(must=conditions)
        )

        print(f"🗑️  Deleted documents matching filter: {filter}")
        return result

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        info = self.client.get_collection(self.collection_name)
        return {
            'name': self.collection_name,
            'vectors_count': info.vectors_count,
            'points_count': info.points_count,
            'status': info.status
        }

    def delete_collection(self):
        """Delete the entire collection."""
        self.client.delete_collection(self.collection_name)
        print(f"🗑️  Deleted collection: {self.collection_name}")


def test_vector_store():
    """
    Test Qdrant vector store with sample data.

    PREREQUISITES:
    Run: docker run -p 6333:6333 qdrant/qdrant
    Or use path parameter for local storage
    """
    import sys
    from pathlib import Path

    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent))
    from embeddings import EmbeddingGenerator

    try:
        print("=" * 70)
        print("QDRANT VECTOR STORE TEST")
        print("=" * 70)

        # Initialize (using local storage, no Docker needed)
        store = QdrantVectorStore(
            collection_name="test_sec_filings",
            path="./data/qdrant_test"  # Local storage
        )

        # Create sample documents
        sample_docs = [
            Document(
                page_content="Apple's revenue in fiscal year 2024 was $391 billion, up 7% year-over-year.",
                metadata={
                    'ticker': 'AAPL',
                    'company': 'Apple Inc.',
                    'filing_type': '10-K',
                    'section': 'Financial Highlights'
                }
            ),
            Document(
                page_content="The company's iPhone sales represented 52% of total revenue.",
                metadata={
                    'ticker': 'AAPL',
                    'company': 'Apple Inc.',
                    'filing_type': '10-K',
                    'section': 'Products'
                }
            ),
            Document(
                page_content="Microsoft's cloud revenue grew 22% to $110 billion in fiscal 2024.",
                metadata={
                    'ticker': 'MSFT',
                    'company': 'Microsoft Corporation',
                    'filing_type': '10-K',
                    'section': 'Financial Highlights'
                }
            ),
        ]

        # Generate embeddings
        print("\n1️⃣  Generating embeddings...")
        embedder = EmbeddingGenerator()
        embeddings = embedder.embed_documents(sample_docs)

        # Add to Qdrant
        print("\n2️⃣  Adding documents to Qdrant...")
        point_ids = store.add_documents(sample_docs, embeddings)
        print(f"   Added {len(point_ids)} documents")

        # Get collection info
        info = store.get_collection_info()
        print(f"\n📊 Collection info:")
        print(f"   Points: {info['points_count']}")
        print(f"   Status: {info['status']}")

        # Test search
        print("\n3️⃣  Testing search...")
        query = "What is Apple's revenue?"
        query_vector = embedder.embed_query(query)

        # Search all
        print(f"\n   Query: '{query}'")
        results = store.search(query_vector, limit=3)
        print(f"   Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n   {i}. Score: {result['score']:.3f}")
            print(f"      Ticker: {result['metadata'].get('ticker')}")
            print(f"      Content: {result['content'][:80]}...")

        # Search with filter
        print(f"\n4️⃣  Testing filtered search (AAPL only)...")
        filtered_results = store.search(
            query_vector,
            filter={"ticker": "AAPL"},
            limit=3
        )
        print(f"   Found {len(filtered_results)} AAPL results:")
        for i, result in enumerate(filtered_results, 1):
            print(f"   {i}. {result['metadata'].get('ticker')}: {result['content'][:60]}...")

        print("\n✅ All tests passed!")
        print("\n💡 To clean up: Delete ./data/qdrant_test directory")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_vector_store()
