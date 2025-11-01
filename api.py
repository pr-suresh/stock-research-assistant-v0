"""
FastAPI Backend for RAG Pipeline

Run with:
    uvicorn api:app --reload --port 8000

Then visit:
    http://localhost:8000/docs (Swagger UI)
    http://localhost:8000/redoc (ReDoc)

Endpoints:
    GET  /              - Health check
    POST /parse         - Upload HTML → Clean text
    POST /chunk         - Text → Chunks
    POST /embed         - Chunks → Vectors
    POST /pipeline/full - Complete pipeline
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from pathlib import Path
import tempfile
import os
from dotenv import load_dotenv

# Import our modules
import sys
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from sec_parser import SECFilingParser
from text_chunker import TextChunker
from embeddings import EmbeddingGenerator
from vector_store import QdrantVectorStore
from qa_engine import RAGQuestionAnswering

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="RAG Pipeline API",
    description="Parse, chunk, and embed SEC filings for RAG",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# Enable CORS (for React frontend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize embeddings and QA engine (lazy - only when needed)
_embedder = None
_qa_engine = None

def get_embedder():
    """Get or create embeddings generator."""
    global _embedder
    if _embedder is None:
        try:
            _embedder = EmbeddingGenerator()
        except ValueError as e:
            raise HTTPException(
                status_code=500,
                detail=f"OpenAI API key not configured. {str(e)}"
            )
    return _embedder


def get_qa_engine():
    """Get or create Q&A engine."""
    global _qa_engine
    if _qa_engine is None:
        try:
            embedder = get_embedder()

            # Initialize vector store (auto-detects local or cloud)
            qdrant_path = os.getenv('QDRANT_PATH', 'data/processed/qdrant_storage')
            qdrant_url = os.getenv('QDRANT_URL')

            if qdrant_url:
                # Use Qdrant Cloud
                vector_store = QdrantVectorStore(collection_name="sec_filings")
            else:
                # Use local storage
                vector_store = QdrantVectorStore(
                    collection_name="sec_filings",
                    path=qdrant_path
                )

            _qa_engine = RAGQuestionAnswering(
                vector_store=vector_store,
                embedder=embedder
            )
        except ValueError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Q&A engine initialization error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize Q&A engine: {str(e)}"
            )
    return _qa_engine


# =============================================================================
# Request/Response Models (Pydantic)
# =============================================================================

class ParseResponse(BaseModel):
    """Response from parse endpoint."""
    clean_text: str
    sections: Dict[str, str]
    metadata: Dict
    stats: Dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "clean_text": "Item 1. Business...",
                "sections": {"Business": "...", "Risk Factors": "..."},
                "metadata": {"cik": "0000320193", "ticker_hint": "AAPL"},
                "stats": {"clean_text_length": 203301, "num_sections": 7}
            }
        }


class ChunkRequest(BaseModel):
    """Request to chunk text."""
    text: str = Field(..., description="Text to chunk")
    chunk_size: int = Field(1000, description="Target chunk size in characters")
    chunk_overlap: int = Field(200, description="Overlap between chunks")
    strategy: str = Field("recursive", description="Chunking strategy: recursive or character")
    metadata: Optional[Dict] = Field(None, description="Metadata to attach to chunks")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Apple Inc. designs and manufactures consumer electronics...",
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "strategy": "recursive",
                "metadata": {"source": "apple_10k.htm", "company": "Apple"}
            }
        }


class ChunkResponse(BaseModel):
    """Response from chunk endpoint."""
    chunks: List[Dict]
    stats: Dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "chunks": [
                    {
                        "content": "Apple Inc. designs...",
                        "metadata": {"chunk_index": 0, "total_chunks": 5},
                        "length": 987
                    }
                ],
                "stats": {
                    "num_chunks": 5,
                    "avg_chunk_size": 950,
                    "min_chunk_size": 800,
                    "max_chunk_size": 1100
                }
            }
        }


class EmbedRequest(BaseModel):
    """Request to embed chunks."""
    chunks: List[Dict] = Field(..., description="Chunks to embed (from /chunk endpoint)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chunks": [
                    {
                        "content": "Apple Inc. designs...",
                        "metadata": {"chunk_index": 0}
                    }
                ]
            }
        }


class EmbedResponse(BaseModel):
    """Response from embed endpoint."""
    embeddings: List[Dict]
    cost_info: Dict

    class Config:
        json_schema_extra = {
            "example": {
                "embeddings": [
                    {
                        "content": "Apple Inc. designs...",
                        "metadata": {"chunk_index": 0},
                        "embedding": [0.023, -0.015, 0.042, "..."],
                        "embedding_dim": 1536
                    }
                ],
                "cost_info": {
                    "num_documents": 5,
                    "estimated_tokens": 1250,
                    "estimated_cost_usd": 0.0001
                }
            }
        }


class QARequest(BaseModel):
    """Request for question answering."""
    question: str = Field(..., description="Question to ask about SEC filings")
    ticker: Optional[str] = Field(None, description="Filter by stock ticker (e.g., AAPL)")
    filing_type: Optional[str] = Field(None, description="Filter by filing type (e.g., 10-K, 10-Q)")
    section: Optional[str] = Field(None, description="Filter by section name")
    top_k: int = Field(5, description="Number of chunks to retrieve", ge=1, le=20)

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is Apple's revenue?",
                "ticker": "AAPL",
                "top_k": 5
            }
        }


class Source(BaseModel):
    """Source document citation."""
    id: int = Field(..., description="Citation number")
    content: str = Field(..., description="Chunk content")
    metadata: Dict = Field(..., description="Source metadata (ticker, section, score, etc.)")


class QAResponse(BaseModel):
    """Response from question answering."""
    answer: str = Field(..., description="Generated answer with footnoted citations")
    sources: List[Source] = Field(..., description="Source documents with metadata")
    metadata: Dict = Field(..., description="Processing metadata (tokens, cost, timing)")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Apple Inc. reported total net sales of $391.0 billion for fiscal year 2024 [1].",
                "sources": [
                    {
                        "id": 1,
                        "content": "Total net sales were $391.0 billion...",
                        "metadata": {
                            "ticker": "AAPL",
                            "section": "Financial Highlights",
                            "filing_type": "10-K",
                            "score": 0.89
                        }
                    }
                ],
                "metadata": {
                    "model": "gpt-4-turbo-preview",
                    "total_tokens": 975,
                    "estimated_cost_usd": 0.014,
                    "total_time_ms": 1945
                }
            }
        }


# =============================================================================
# Endpoints
# =============================================================================

@app.get("/", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns API status and available endpoints.
    """
    return {
        "status": "healthy",
        "message": "RAG Pipeline API with Q&A is running",
        "endpoints": {
            "docs": "/docs",
            "parse": "POST /parse",
            "chunk": "POST /chunk",
            "embed": "POST /embed",
            "pipeline": "POST /pipeline/full",
            "qa": "POST /qa - Answer questions about SEC filings"
        }
    }


@app.post("/parse", response_model=ParseResponse, tags=["Parse"])
async def parse_html(
    file: UploadFile = File(..., description="HTML file to parse (e.g., SEC 10-K filing)")
):
    """
    Parse SEC filing HTML to extract clean text.
    
    **What it does:**
    - Removes XBRL metadata
    - Extracts visible text content
    - Identifies document sections (Item 1, Item 1A, etc.)
    - Cleans formatting
    
    **Input:** HTML file upload
    
    **Output:** Clean text, sections, metadata, and stats
    
    **Example:** Upload an SEC 10-K HTML file
    """
    # Validate file type
    if not file.filename.endswith(('.htm', '.html')):
        raise HTTPException(
            status_code=400,
            detail="File must be HTML (.htm or .html)"
        )
    
    # Save uploaded file temporarily
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.htm') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)
        
        # Parse the file
        parser = SECFilingParser(tmp_path)
        result = parser.parse()
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return ParseResponse(**result)
        
    except Exception as e:
        if tmp_path.exists():
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")


@app.post("/chunk", response_model=ChunkResponse, tags=["Chunk"])
async def chunk_text(request: ChunkRequest):
    """
    Chunk text into smaller pieces for RAG.
    
    **What it does:**
    - Breaks long text into manageable chunks
    - Preserves context with overlap
    - Smart splitting (tries paragraphs, then sentences, then words)
    
    **Why chunking:**
    - LLMs have context limits
    - Enables semantic search
    - Better retrieval accuracy
    
    **Strategies:**
    - `recursive`: Smart splitting (recommended)
    - `character`: Simple character-based splitting
    
    **Input:** Text and chunking parameters
    
    **Output:** List of chunks with metadata
    """
    try:
        chunker = TextChunker(
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            strategy=request.strategy
        )
        
        # Chunk the text
        documents = chunker.chunk_text(
            text=request.text,
            metadata=request.metadata or {}
        )
        
        # Convert to dict format
        chunks = []
        for doc in documents:
            chunks.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "length": len(doc.page_content)
            })
        
        # Get statistics
        stats = chunker.analyze_chunks(documents)
        
        return ChunkResponse(chunks=chunks, stats=stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chunking error: {str(e)}")


@app.post("/embed", response_model=EmbedResponse, tags=["Embed"])
async def embed_chunks(request: EmbedRequest):
    """
    Generate embeddings for chunks using OpenAI.
    
    **What it does:**
    - Converts text chunks to 1536-dimensional vectors
    - Uses OpenAI text-embedding-3-small model
    - Batches requests automatically
    
    **Why embeddings:**
    - Enable semantic search (search by meaning)
    - Required for vector database storage
    - Similar text → similar vectors
    
    **Cost:** ~$0.02 per 1M tokens (~$0.001 per 200KB document)
    
    **Input:** Chunks from /chunk endpoint
    
    **Output:** Embeddings + cost estimate
    
    **Requirements:** OPENAI_API_KEY environment variable
    """
    try:
        embedder = get_embedder()
        
        # Convert dicts back to Document objects
        from langchain_core.documents import Document
        documents = []
        for chunk in request.chunks:
            documents.append(Document(
                page_content=chunk["content"],
                metadata=chunk.get("metadata", {})
            ))
        
        # Generate embeddings
        vectors = embedder.embed_documents(documents)
        
        # Prepare response
        embeddings = []
        for i, (doc, vector) in enumerate(zip(documents, vectors)):
            embeddings.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "embedding": vector,
                "embedding_dim": len(vector)
            })
        
        # Calculate cost
        cost_info = embedder.estimate_cost(documents)
        
        return EmbedResponse(embeddings=embeddings, cost_info=cost_info)
        
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI API key error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")


@app.post("/pipeline/full", tags=["Pipeline"])
async def full_pipeline(
    file: UploadFile = File(..., description="HTML file to process"),
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    chunk_strategy: str = "recursive"
):
    """
    Complete pipeline: Parse → Chunk → Embed

    **What it does:**
    1. Parse HTML to clean text
    2. Chunk text into pieces
    3. Generate embeddings for each chunk

    **Input:** HTML file + chunking parameters

    **Output:** Embeddings ready for vector database

    **Use case:** One-shot processing of entire document
    """
    # Step 1: Parse
    parse_result = await parse_html(file)

    # Step 2: Chunk
    chunk_request = ChunkRequest(
        text=parse_result.clean_text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        strategy=chunk_strategy,
        metadata=parse_result.metadata
    )
    chunk_result = await chunk_text(chunk_request)

    # Step 3: Embed
    embed_request = EmbedRequest(chunks=chunk_result.chunks)
    embed_result = await embed_chunks(embed_request)

    return {
        "parse_stats": parse_result.stats,
        "chunk_stats": chunk_result.stats,
        "embeddings": embed_result.embeddings,
        "cost_info": embed_result.cost_info,
        "message": "Pipeline complete! Ready for vector database storage."
    }


@app.post("/qa", response_model=QAResponse, tags=["Q&A"])
async def question_answering(request: QARequest):
    """
    Answer questions about SEC filings using RAG + GPT-4.

    **How it works:**
    1. Embed the user's question
    2. Search Qdrant for relevant chunks (semantic search)
    3. Optionally filter by ticker, filing type, or section
    4. Pass top_k relevant chunks to GPT-4 as context
    5. Generate answer with footnoted source citations [1], [2], etc.

    **Features:**
    - Semantic search (searches by meaning, not keywords)
    - Metadata filtering (specific ticker, filing type, section)
    - Source citations for fact-checking
    - Cost tracking (tokens and estimated USD)

    **Example Questions:**
    - "What is Apple's revenue?"
    - "What are the main risk factors for AAPL?"
    - "How much does the company spend on R&D?"
    - "What are the key products and services?"

    **Filters:**
    - `ticker`: e.g., "AAPL", "MSFT"
    - `filing_type`: e.g., "10-K", "10-Q"
    - `section`: e.g., "Business", "Risk Factors"

    **Cost:** ~$0.01-0.03 per query (GPT-4 Turbo)

    **Requirements:**
    - OPENAI_API_KEY environment variable
    - Qdrant database with processed filings
    """
    try:
        qa_engine = get_qa_engine()

        # Build filters
        filters = {}
        if request.ticker:
            filters['ticker'] = request.ticker.upper()
        if request.filing_type:
            filters['filing_type'] = request.filing_type
        if request.section:
            filters['section'] = request.section

        # Ask question
        result = qa_engine.ask(
            question=request.question,
            filters=filters if filters else None,
            top_k=request.top_k
        )

        # Check for errors
        if result.get('metadata', {}).get('error'):
            raise HTTPException(
                status_code=500,
                detail=result['metadata']['error_message']
            )

        return QAResponse(**result)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Q&A error: {str(e)}"
        )


# =============================================================================
# Startup/Shutdown Events
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on API startup."""
    print("\n" + "=" * 70)
    print("🚀 RAG Pipeline API Starting...")
    print("=" * 70)
    print(f"📚 Swagger UI: http://localhost:8000/docs")
    print(f"📖 ReDoc:      http://localhost:8000/redoc")
    print("=" * 70 + "\n")
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  WARNING: OPENAI_API_KEY not set!")
        print("   Embeddings endpoint will not work.")
        print("   Set in .env file or environment variable.\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on API shutdown."""
    print("\n👋 API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )