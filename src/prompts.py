"""
Prompt Templates for Q&A System

This module contains prompt templates for the RAG-based Q&A system.
Templates guide the LLM to provide accurate, cited answers from SEC filings.
"""

# System prompt that defines the assistant's role and guidelines
SYSTEM_PROMPT = """You are a financial analyst assistant that answers questions about SEC filings (10-K, 10-Q, 8-K, etc.).

Your responsibilities:
- Provide accurate, factual answers based ONLY on the provided context
- Use numbered citations [1], [2], [3] for every fact or figure you mention
- Be precise with financial data, dates, and percentages
- If the context doesn't contain sufficient information, clearly state: "I don't have enough information in the available filings to answer this question."

Guidelines:
1. **Accuracy**: Never make up or infer information not explicitly in the context
2. **Citations**: Every fact must have a citation number matching the context sources
3. **Clarity**: Use clear, professional language appropriate for financial analysis
4. **Format**: Present numbers with proper units (e.g., "$391 billion", "52%", "Q4 2024")
5. **Honesty**: If uncertain or context is insufficient, admit it clearly

Example of proper citations:
"Apple's total revenue was $391.0 billion in fiscal year 2024 [1], with iPhone sales accounting for $201.2 billion or approximately 52% of total revenue [2]."
"""

# Template for formatting the user query with context
QA_TEMPLATE = """Context from SEC filings:

{context}

Question: {question}

Instructions:
- Answer the question using ONLY the information provided in the context above
- Cite every fact using the numbered citations [1], [2], [3] that correspond to the context sources
- If the context doesn't contain the answer, say so clearly
- Be concise but complete in your answer

Answer:"""

# Response when no relevant context is found
NO_CONTEXT_RESPONSE = """I don't have enough information in the available SEC filings to answer this question.

This could be because:
- The information hasn't been uploaded to the database yet
- The question relates to data not typically found in SEC filings
- The search didn't find relevant sections

Please try:
- Rephrasing your question
- Being more specific about what you're looking for
- Checking if the relevant SEC filing has been processed"""

# Template for formatting context with citations
def format_context_with_citations(chunks: list) -> str:
    """
    Format retrieved chunks with citation numbers.

    Args:
        chunks: List of (content, metadata) tuples

    Returns:
        Formatted context string with numbered citations

    Example:
        [1] Apple Inc. reported revenue of $391 billion...
        [2] iPhone sales increased by 7% year-over-year...
    """
    if not chunks:
        return ""

    formatted_parts = []
    for i, (content, metadata) in enumerate(chunks, 1):
        # Add citation number and content
        citation = f"[{i}] {content}"
        formatted_parts.append(citation)

    return "\n\n".join(formatted_parts)


# Template for extracting metadata for source attribution
def format_source_metadata(metadata: dict) -> str:
    """
    Format metadata for display in sources list.

    Args:
        metadata: Dictionary with filing metadata

    Returns:
        Formatted source description

    Example:
        "Apple Inc. (AAPL) 10-K Filing, 2024-09-28, Section: Financial Highlights"
    """
    parts = []

    # Company and ticker
    if metadata.get('company') and metadata.get('ticker'):
        parts.append(f"{metadata['company']} ({metadata['ticker']})")
    elif metadata.get('company'):
        parts.append(metadata['company'])
    elif metadata.get('ticker'):
        parts.append(metadata['ticker'])

    # Filing type and date
    filing_info = []
    if metadata.get('filing_type'):
        filing_info.append(metadata['filing_type'])
    if metadata.get('filing_date'):
        filing_info.append(metadata['filing_date'])
    if filing_info:
        parts.append(" ".join(filing_info))

    # Section
    if metadata.get('section'):
        parts.append(f"Section: {metadata['section']}")

    return ", ".join(parts)


# Error messages for common issues
ERROR_MESSAGES = {
    'no_api_key': (
        "OpenAI API key not configured. "
        "Please set OPENAI_API_KEY in your .env file. "
        "Get your API key from: https://platform.openai.com/api-keys"
    ),
    'no_results': (
        "No relevant information found in the database for this query. "
        "Try rephrasing your question or check if the relevant filing has been processed."
    ),
    'rate_limit': (
        "OpenAI API rate limit exceeded. Please try again in a few moments."
    ),
    'timeout': (
        "Request timed out. Please try again."
    ),
    'llm_error': (
        "Error generating answer from the language model. "
        "This might be a temporary issue. Please try again."
    ),
    'invalid_response': (
        "Received an invalid response from the language model. "
        "Please try again or rephrase your question."
    ),
}


def get_error_message(error_type: str, details: str = None) -> str:
    """
    Get a user-friendly error message.

    Args:
        error_type: Type of error (key from ERROR_MESSAGES)
        details: Optional additional details

    Returns:
        Formatted error message
    """
    message = ERROR_MESSAGES.get(error_type, "An unexpected error occurred.")
    if details:
        message = f"{message}\n\nDetails: {details}"
    return message
