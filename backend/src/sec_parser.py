"""
SEC Filing HTML Parser

Extracts clean, structured text from SEC HTML/iXBRL filings.

WHY THIS MODULE EXISTS:
SEC filings are complex HTML/iXBRL documents with:
- XBRL metadata tags (financial data structure)
- Hidden sections
- Inline styling and formatting
- Tables and financial statements
- Nested structure

We need to extract just the meaningful text content for RAG.
"""

from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from pathlib import Path
import re


class SECFilingParser:
    """
    Parse SEC HTML/iXBRL filings and extract clean text.
    
    PARSING STRATEGY:
    1. Remove hidden XBRL metadata sections
    2. Extract visible text content
    3. Identify major sections (Business, Risk Factors, etc.)
    4. Clean formatting (extra whitespace, special chars)
    5. Structure output for downstream use
    """
    
    # Common section headers in 10-K/10-Q filings
    # WHY: These help us identify and separate major sections
    SECTION_PATTERNS = [
        r'item\s+1\s*[.\-:]\s*business',
        r'item\s+1a\s*[.\-:]\s*risk\s+factors',
        r'item\s+2\s*[.\-:]\s*properties',
        r'item\s+3\s*[.\-:]\s*legal\s+proceedings',
        r'item\s+7\s*[.\-:]\s*management.*discussion',
        r'item\s+8\s*[.\-:]\s*financial\s+statements',
        r'item\s+9a\s*[.\-:]\s*controls\s+and\s+procedures',
    ]
    
    def __init__(self, html_path: Path):
        """
        Initialize parser with HTML file.
        
        Args:
            html_path: Path to SEC HTML filing
        """
        self.html_path = html_path
        self.soup = None
        self.raw_text = None
        self.clean_text = None
        self.sections = None
        
    def parse(self) -> Dict:
        """
        Main parsing pipeline.
        
        Returns:
            Dictionary with parsed content:
            {
                'raw_text': str,        # All text extracted
                'clean_text': str,      # Cleaned and formatted
                'sections': dict,       # Major sections identified
                'metadata': dict,       # File info
            }
        """
        print(f"📄 Parsing: {self.html_path.name}")
        
        # Step 1: Load and parse HTML
        self._load_html()
        
        # Step 2: Remove hidden/metadata sections
        self._remove_hidden_sections()
        
        # Step 3: Extract all text
        self._extract_text()
        
        # Step 4: Clean text
        self._clean_text()
        
        # Step 5: Identify sections
        self._identify_sections()
        
        # Step 6: Build result
        result = {
            'raw_text': self.raw_text,
            'clean_text': self.clean_text,
            'sections': self.sections,
            'metadata': self._extract_metadata(),
            'stats': {
                'file_size_kb': self.html_path.stat().st_size / 1024,
                'raw_text_length': len(self.raw_text) if self.raw_text else 0,
                'clean_text_length': len(self.clean_text) if self.clean_text else 0,
                'num_sections': len(self.sections) if self.sections else 0,
            }
        }
        
        print(f"✅ Parsed {result['stats']['clean_text_length']:,} characters")
        print(f"✅ Found {result['stats']['num_sections']} sections")
        
        return result
    
    def _load_html(self):
        """
        Load HTML file and create BeautifulSoup object.
        
        WHY BEAUTIFULSOUP:
        - Handles malformed HTML gracefully
        - Provides easy DOM navigation
        - Built-in text extraction
        """
        with open(self.html_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        # Use 'html.parser' - faster and no external dependencies
        # Alternative: 'lxml' (faster but requires installation)
        self.soup = BeautifulSoup(html_content, 'html.parser')
    
    def _remove_hidden_sections(self):
        """
        Remove hidden XBRL metadata and invisible content.
        
        WHY: iXBRL files have hidden sections with structured data
        that's not meant for human reading. This includes:
        - <ix:hidden> tags (XBRL metadata)
        - <script> tags (JavaScript)
        - <style> tags (CSS)
        - Elements with display:none
        """
        # Remove common non-content tags
        tags_to_remove = ['script', 'style', 'ix:header', 'ix:hidden']
        
        for tag_name in tags_to_remove:
            for tag in self.soup.find_all(tag_name):
                tag.decompose()  # Completely remove from tree
        
        # Remove elements with display:none
        for element in self.soup.find_all(style=re.compile(r'display:\s*none', re.I)):
            element.decompose()
    
    def _extract_text(self):
        """
        Extract all visible text from HTML.
        
        HOW THIS WORKS:
        - get_text() walks the DOM tree
        - separator=' ' adds space between elements
        - strip=True removes leading/trailing whitespace
        """
        self.raw_text = self.soup.get_text(separator=' ', strip=True)
    
    def _clean_text(self):
        """
        Clean and normalize extracted text.
        
        CLEANING STEPS:
        1. Remove excessive whitespace
        2. Remove special characters that break parsing
        3. Normalize line breaks
        4. Remove XBRL namespace URLs (if any remain)
        """
        text = self.raw_text
        
        # Remove XBRL namespace URLs (like http://fasb.org/us-gaap/2024#...)
        text = re.sub(r'http://[^\s]+#\w+', '', text)
        
        # Remove other URLs that snuck through
        text = re.sub(r'https?://[^\s]+', '', text)
        
        # Collapse multiple spaces into one
        text = re.sub(r'\s+', ' ', text)
        
        # Remove strange characters but keep basic punctuation
        # Keep: letters, numbers, common punctuation, spaces
        text = re.sub(r'[^\w\s.,;:!?()\-\'\"$%/&]', '', text)
        
        self.clean_text = text.strip()
    
    def _identify_sections(self):
        """
        Identify major sections in the filing.
        
        HOW IT WORKS:
        - Search for section headers (Item 1, Item 1A, etc.)
        - Extract text between headers
        - Store as structured dictionary
        
        WHY THIS MATTERS FOR RAG:
        - Allows targeted retrieval (e.g., "show me risk factors")
        - Better context for LLM
        - More precise embeddings
        """
        self.sections = {}
        
        text = self.clean_text.lower()
        
        # Find all section positions
        section_positions = []
        
        for pattern in self.SECTION_PATTERNS:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                section_name = match.group(0).strip()
                section_positions.append((match.start(), section_name))
        
        # Sort by position
        section_positions.sort()
        
        # Extract text for each section
        for i, (start_pos, section_name) in enumerate(section_positions):
            # Get end position (start of next section or end of text)
            if i < len(section_positions) - 1:
                end_pos = section_positions[i + 1][0]
            else:
                end_pos = len(text)
            
            # Extract section text
            section_text = self.clean_text[start_pos:end_pos].strip()
            
            # Clean up section name
            clean_name = re.sub(r'item\s+\w+\s*[.\-:]\s*', '', section_name, flags=re.IGNORECASE)
            clean_name = clean_name.strip().title()
            
            self.sections[clean_name] = section_text
    
    def _extract_metadata(self) -> Dict:
        """
        Extract metadata from filing.
        
        WHAT WE EXTRACT:
        - Company name (from title or meta tags)
        - Filing date
        - Form type (10-K, 10-Q, etc.)
        - CIK (if available)
        """
        metadata = {}
        
        # Try to extract from filename
        filename = self.html_path.name
        parts = filename.replace('.htm', '').split('_')
        
        if len(parts) >= 2:
            metadata['cik'] = parts[0]
            if len(parts) >= 3:
                # Last part is often company-date (e.g., aapl-20240928)
                doc_name = parts[-1]
                if '-' in doc_name:
                    company, date = doc_name.split('-', 1)
                    metadata['ticker_hint'] = company.upper()
                    metadata['date_hint'] = date
        
        # Try to find title
        title_tag = self.soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)
        
        return metadata
    
    def save_clean_text(self, output_path: Path):
        """
        Save cleaned text to file.
        
        Args:
            output_path: Where to save cleaned text
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.clean_text, encoding='utf-8')
        print(f"💾 Saved clean text to: {output_path}")
    
    def save_sections(self, output_dir: Path):
        """
        Save each section as a separate file.
        
        WHY SEPARATE FILES:
        - Easier to work with individual sections
        - Can embed sections separately
        - Better for targeted retrieval
        
        Args:
            output_dir: Directory to save section files
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for section_name, section_text in self.sections.items():
            # Create safe filename
            safe_name = re.sub(r'[^\w\s-]', '', section_name)
            safe_name = safe_name.replace(' ', '_').lower()
            
            # Truncate if too long (filesystem limit is ~255 chars)
            # Keep first 100 chars to preserve meaningful name
            if len(safe_name) > 100:
                safe_name = safe_name[:100] + '_truncated'
            
            output_path = output_dir / f'{safe_name}.txt'
            output_path.write_text(section_text, encoding='utf-8')
        
        print(f"💾 Saved {len(self.sections)} sections to: {output_dir}")


# Example usage
if __name__ == "__main__":
    # Parse a filing
    filing_path = Path("data/filings/example.htm")
    
    if filing_path.exists():
        parser = SECFilingParser(filing_path)
        result = parser.parse()
        
        print("\n" + "=" * 60)
        print("PARSING RESULTS")
        print("=" * 60)
        print(f"File: {filing_path.name}")
        print(f"Raw text: {result['stats']['raw_text_length']:,} chars")
        print(f"Clean text: {result['stats']['clean_text_length']:,} chars")
        print(f"Sections found: {result['stats']['num_sections']}")
        print("\nSections:")
        for section_name in result['sections'].keys():
            print(f"  - {section_name}")