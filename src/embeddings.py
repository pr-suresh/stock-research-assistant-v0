"""
Text Embeddings for RAG

WHAT ARE EMBEDDINGS:
Embeddings convert text into vectors (lists of numbers) that capture meaning.
Similar text → similar vectors.

Example:
"Apple's revenue" → [0.2, -0.5, 0.8, ...] (1536 numbers)
"Apple earnings"  → [0.19, -0.48, 0.82, ...] (similar!)
"Pizza recipe"    → [-0.4, 0.1, -0.2, ...] (different!)

WHY EMBEDDINGS FOR RAG:
1. Question: "What was Apple's 2024 revenue?"
2. Embed question → vector
3. Find chunks with similar vectors (vector search)
4. Send those chunks to LLM as context
5. LLM generates answer

COST CONSIDERATIONS:
- OpenAI text-embedding-3-small: $0.02 per 1M tokens
- Apple 10-K (~200K chars) ≈ 50K tokens ≈ $0.001
- Very cheap! But adds up with many documents
"""

from typing import List, Optional, Dict
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import os
from pathlib import Path


class EmbeddingGenerator:
    """
    Generate embeddings using OpenAI.
    
    EMBEDDING MODELS:
    - text-embedding-3-small: Cheap, fast, 1536 dimensions (we'll use this)
    - text-embedding-3-large: Better quality, 3072 dimensions, 5x more expensive
    - text-embedding-ada-002: Legacy model, don't use
    """
    
    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: Optional[str] = None
    ):
        """
        Initialize embedding generator.
        
        Args:
            model: OpenAI embedding model name
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            
        HOW TO GET API KEY:
        1. Go to platform.openai.com
        2. Create account / login
        3. API Keys → Create new key
        4. Set as environment variable or pass here
        """
        # Get API key from env or parameter
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
        elif not os.getenv('OPENAI_API_KEY'):
            raise ValueError(
                "OpenAI API key not found. Either:\n"
                "1. Set OPENAI_API_KEY environment variable\n"
                "2. Pass api_key parameter\n"
                "3. Create .env file with OPENAI_API_KEY=your-key"
            )
        
        self.model = model
        self.embeddings = OpenAIEmbeddings(
            model=model,
            # show_progress_bar=True  # Uncomment to see progress
        )
        
        print(f"✅ Initialized embeddings with model: {model}")
    
    def embed_documents(
        self,
        documents: List[Document]
    ) -> List[List[float]]:
        """
        Embed a list of documents.
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            List of embedding vectors
            
        WHAT HAPPENS:
        1. Extract text from each document
        2. Send batch to OpenAI API
        3. Get back vectors
        4. Each vector has 1536 numbers (for text-embedding-3-small)
        
        TIME & COST:
        - ~100 docs: ~5 seconds, $0.001
        - ~1000 docs: ~30 seconds, $0.01
        - Batched automatically by LangChain
        """
        print(f"🔄 Embedding {len(documents)} documents...")
        
        # Extract text content
        texts = [doc.page_content for doc in documents]
        
        # Embed (batched automatically)
        vectors = self.embeddings.embed_documents(texts)
        
        print(f"✅ Generated {len(vectors)} embeddings")
        print(f"   Dimension: {len(vectors[0])}")
        
        return vectors
    
    def embed_query(self, query: str) -> List[float]:
        """
        Embed a single query.
        
        WHY SEPARATE METHOD:
        Query embedding uses slightly different processing than document embedding.
        Always use embed_query() for questions, embed_documents() for text.
        
        Args:
            query: Question or search query
            
        Returns:
            Single embedding vector
        """
        return self.embeddings.embed_query(query)
    
    def estimate_cost(
        self,
        documents: List[Document],
        cost_per_1m_tokens: float = 0.02
    ) -> Dict:
        """
        Estimate embedding cost.
        
        ROUGH CALCULATION:
        - 1 token ≈ 4 characters
        - text-embedding-3-small: $0.02 per 1M tokens
        
        Args:
            documents: Documents to embed
            cost_per_1m_tokens: Price per million tokens
            
        Returns:
            Cost estimate breakdown
        """
        total_chars = sum(len(doc.page_content) for doc in documents)
        estimated_tokens = total_chars / 4  # Rough estimate
        estimated_cost = (estimated_tokens / 1_000_000) * cost_per_1m_tokens
        
        return {
            'num_documents': len(documents),
            'total_characters': total_chars,
            'estimated_tokens': int(estimated_tokens),
            'estimated_cost_usd': round(estimated_cost, 4),
            'cost_per_doc_usd': round(estimated_cost / len(documents), 6) if documents else 0
        }


def test_embeddings():
    """
    Test embedding generation with sample text.
    
    RUN THIS FIRST to make sure your API key works!
    """
    try:
        embedder = EmbeddingGenerator()
        
        # Test with sample documents
        sample_docs = [
            Document(
                page_content="Apple's revenue in 2024 was $391 billion.",
                metadata={'source': 'test', 'section': 'financials'}
            ),
            Document(
                page_content="The company manufactures iPhones and Macs.",
                metadata={'source': 'test', 'section': 'products'}
            ),
        ]
        
        # Embed documents
        print("\n" + "=" * 60)
        print("EMBEDDING TEST")
        print("=" * 60)
        
        vectors = embedder.embed_documents(sample_docs)
        
        # Test query embedding
        query = "What is Apple's revenue?"
        query_vector = embedder.embed_query(query)
        
        print(f"\n✅ Test successful!")
        print(f"   Document embeddings: {len(vectors)}")
        print(f"   Query embedding dimension: {len(query_vector)}")
        
        # Show similarity (dot product)
        from numpy import dot
        from numpy.linalg import norm
        
        # Cosine similarity between query and first doc
        similarity = dot(query_vector, vectors[0]) / (norm(query_vector) * norm(vectors[0]))
        print(f"   Similarity (query vs doc 1): {similarity:.3f}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nMake sure you have:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Or created .env file with OPENAI_API_KEY=your-key")
        return False


if __name__ == "__main__":
    test_embeddings()