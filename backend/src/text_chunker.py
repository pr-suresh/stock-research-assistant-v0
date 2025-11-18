"""
Text Chunking for RAG

WHY CHUNKING MATTERS:
When you ask an LLM a question, you can only send a limited amount of text
(the context window). For a 200KB document like Apple's 10-K, you need to:

1. Break it into smaller pieces (chunks)
2. Find the most relevant chunks for the question
3. Send only those chunks to the LLM

CHUNKING STRATEGY IS CRITICAL:
- Too small: Loses context, misses connections
- Too large: Wastes tokens, dilutes relevance
- Wrong boundaries: Breaks mid-sentence or mid-thought

DIFFERENT STRATEGIES:
1. RecursiveCharacterTextSplitter: Smart splitting (tries paragraphs first, then sentences)
2. CharacterTextSplitter: Simple splitting by character count
3. SemanticChunker: Groups text by meaning (requires embeddings)
4. Section-based: Use document structure (Item 1, Item 1A, etc.)
"""

from pathlib import Path
from typing import List, Dict, Optional
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
)
from langchain_core.documents import Document
import json


class TextChunker:
    """
    Chunk text using different strategies for RAG.
    
    WHAT ARE CHUNKS:
    Chunks are the pieces of text that get embedded and stored.
    When you ask a question, we:
    1. Embed your question
    2. Find similar chunks (by vector similarity)
    3. Send those chunks to the LLM as context
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        strategy: str = "recursive"
    ):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: How much chunks overlap (preserves context at boundaries)
            strategy: 'recursive', 'character', or 'section'
            
        WHY OVERLAP:
        Overlap ensures important info near chunk boundaries isn't lost.
        Example:
            Chunk 1: "...Apple's revenue was $394B..."
            Chunk 2: "...394B in 2024, up from $365B..."
        
        Both chunks can answer "What was Apple's 2024 revenue?"
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
        
        # Initialize splitter based on strategy
        if strategy == "recursive":
            # Tries to split on paragraphs first, then sentences, then words
            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", ". ", " ", ""],  # Priority order
                length_function=len,
            )
        elif strategy == "character":
            # Simple character-based splitting
            self.splitter = CharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separator=" ",
                length_function=len,
            )
        else:
            # Section-based handled separately
            self.splitter = None
    
    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict] = None
    ) -> List[Document]:
        """
        Chunk text into Documents.
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of LangChain Document objects
            
        WHY DOCUMENT OBJECTS:
        LangChain's Document has:
        - page_content: The actual text
        - metadata: Info about the chunk (source, section, page, etc.)
        
        This metadata helps with:
        - Filtering results
        - Citing sources
        - Debugging
        """
        if self.strategy == "section":
            raise ValueError("Use chunk_sections() for section-based chunking")
        
        if metadata is None:
            metadata = {}
        
        # Create documents
        documents = self.splitter.create_documents(
            texts=[text],
            metadatas=[metadata]
        )
        
        # Add chunk index to metadata
        for i, doc in enumerate(documents):
            doc.metadata['chunk_index'] = i
            doc.metadata['total_chunks'] = len(documents)
            doc.metadata['chunk_size'] = len(doc.page_content)
        
        return documents
    
    def chunk_sections(
        self,
        sections: Dict[str, str],
        base_metadata: Optional[Dict] = None
    ) -> List[Document]:
        """
        Chunk by document sections (Item 1, Item 1A, etc.).
        
        WHY SECTION-BASED CHUNKING:
        SEC filings have natural boundaries:
        - Item 1: Business
        - Item 1A: Risk Factors
        - Item 7: MD&A
        
        Keeping sections together:
        1. Preserves context
        2. Enables section-specific queries
        3. Better citations
        
        Args:
            sections: Dict of {section_name: section_text}
            base_metadata: Common metadata for all chunks
            
        Returns:
            List of Documents, one per section (or chunked if section too large)
        """
        if base_metadata is None:
            base_metadata = {}
        
        all_documents = []
        
        for section_name, section_text in sections.items():
            # Check if section fits in one chunk
            if len(section_text) <= self.chunk_size:
                # Keep entire section as one chunk
                doc = Document(
                    page_content=section_text,
                    metadata={
                        **base_metadata,
                        'section': section_name,
                        'chunk_index': 0,
                        'total_chunks': 1,
                        'chunk_size': len(section_text)
                    }
                )
                all_documents.append(doc)
            else:
                # Section too large, chunk it
                section_chunks = self.splitter.create_documents(
                    texts=[section_text],
                    metadatas=[{**base_metadata, 'section': section_name}]
                )
                
                # Add chunk indices
                for i, doc in enumerate(section_chunks):
                    doc.metadata['chunk_index'] = i
                    doc.metadata['total_chunks'] = len(section_chunks)
                    doc.metadata['chunk_size'] = len(doc.page_content)
                
                all_documents.extend(section_chunks)
        
        return all_documents
    
    def analyze_chunks(self, documents: List[Document]) -> Dict:
        """
        Analyze chunking results.
        
        Returns statistics to help you tune chunk_size and chunk_overlap.
        """
        if not documents:
            return {}
        
        chunk_sizes = [len(doc.page_content) for doc in documents]
        
        stats = {
            'num_chunks': len(documents),
            'avg_chunk_size': sum(chunk_sizes) / len(chunk_sizes),
            'min_chunk_size': min(chunk_sizes),
            'max_chunk_size': max(chunk_sizes),
            'total_characters': sum(chunk_sizes),
        }
        
        # Count sections if available
        sections = set()
        for doc in documents:
            if 'section' in doc.metadata:
                sections.add(doc.metadata['section'])
        
        if sections:
            stats['num_sections'] = len(sections)
            stats['sections'] = sorted(list(sections))
        
        return stats
    
    def save_chunks(
        self,
        documents: List[Document],
        output_path: Path
    ):
        """
        Save chunks as JSON for inspection.
        
        Useful for debugging and understanding what your chunks look like.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to JSON-serializable format
        chunks_data = []
        for doc in documents:
            chunks_data.append({
                'content': doc.page_content,
                'metadata': doc.metadata,
                'length': len(doc.page_content)
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(chunks_data)} chunks to: {output_path}")


def compare_strategies(text: str, chunk_size: int = 1000) -> Dict:
    """
    Compare different chunking strategies.
    
    WHY THIS IS USEFUL:
    Different strategies work better for different content.
    Run this to see which produces the best chunks for your use case.
    
    Args:
        text: Sample text to chunk
        chunk_size: Target chunk size
        
    Returns:
        Dict with results from each strategy
    """
    results = {}
    
    strategies = ['recursive', 'character']
    
    for strategy in strategies:
        chunker = TextChunker(
            chunk_size=chunk_size,
            chunk_overlap=200,
            strategy=strategy
        )
        
        documents = chunker.chunk_text(text)
        stats = chunker.analyze_chunks(documents)
        
        results[strategy] = {
            'stats': stats,
            'sample_chunk': documents[0].page_content[:200] + "..." if documents else ""
        }
    
    return results


# Example usage
if __name__ == "__main__":
    # Test with sample text
    sample_text = """
    Item 1. Business
    
    Company Background
    The Company designs, manufactures and markets smartphones, personal computers,
    tablets, wearables and accessories, and sells a variety of related services.
    
    Products
    iPhone is the Company's line of smartphones based on its iOS operating system.
    Mac is the Company's line of personal computers based on its macOS operating system.
    
    Item 1A. Risk Factors
    
    The Company's business can be affected by various factors including competition,
    supply chain issues, and regulatory changes.
    """
    
    # Test recursive chunking
    chunker = TextChunker(chunk_size=200, chunk_overlap=50, strategy="recursive")
    docs = chunker.chunk_text(sample_text, metadata={'source': 'test'})
    
    print("=" * 60)
    print("CHUNKING TEST")
    print("=" * 60)
    print(f"\nCreated {len(docs)} chunks")
    
    for i, doc in enumerate(docs):
        print(f"\n--- Chunk {i+1} ---")
        print(f"Length: {len(doc.page_content)} chars")
        print(f"Preview: {doc.page_content[:100]}...")
        print(f"Metadata: {doc.metadata}")