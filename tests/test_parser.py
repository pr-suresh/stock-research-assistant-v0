"""
Test SEC Parser with Real Apple Filing

This script parses the uploaded Apple 10-K filing and shows you
what we can extract from it.
"""

from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from sec_parser import SECFilingParser


def test_parse_apple_filing():
    """Parse the real Apple 10-K filing."""
    
    print("=" * 70)
    print("SEC FILING PARSER TEST - Apple Inc. 10-K")
    print("=" * 70)
    print()
    
    # Path to the uploaded filing
    filing_path = Path(__file__).parent / "data/filings/0000320193_0000320193-24-000123_aapl-20240928.htm"
    
    if not filing_path.exists():
        print(f"❌ File not found: {filing_path}")
        return
    
    print(f"📂 Input file: {filing_path.name}")
    print(f"📊 File size: {filing_path.stat().st_size / (1024*1024):.2f} MB")
    print()
    
    # Parse the filing
    print("🔄 Parsing (this may take a few seconds)...")
    parser = SECFilingParser(filing_path)
    result = parser.parse()
    
    # Display results
    print("\n" + "=" * 70)
    print("PARSING RESULTS")
    print("=" * 70)
    
    # Metadata
    print("\n📋 Metadata:")
    for key, value in result['metadata'].items():
        print(f"   {key}: {value}")
    
    # Statistics
    print("\n📊 Statistics:")
    for key, value in result['stats'].items():
        if isinstance(value, float):
            print(f"   {key}: {value:,.2f}")
        else:
            print(f"   {key}: {value:,}")
    
    # Sections found
    print(f"\n📑 Sections Identified ({len(result['sections'])}):")
    for i, section_name in enumerate(result['sections'].keys(), 1):
        section_text = result['sections'][section_name]
        word_count = len(section_text.split())
        print(f"   {i}. {section_name} ({word_count:,} words)")
    
    # Sample text from Business section
    print("\n" + "=" * 70)
    print("SAMPLE: Business Section (first 500 chars)")
    print("=" * 70)
    
    business_section = result['sections'].get('Business')
    if business_section:
        print(business_section[:500] + "...")
    else:
        # If no Business section, show first 500 chars of clean text
        print("(Business section not identified, showing start of document)")
        print(result['clean_text'][:500] + "...")
    
    # Save outputs
    print("\n" + "=" * 70)
    print("SAVING OUTPUTS")
    print("=" * 70)
    
    output_dir = Path("data/parsed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save clean text
    clean_text_path = output_dir / "apple_10k_clean.txt"
    parser.save_clean_text(clean_text_path)
    
    # Save sections
    sections_dir = output_dir / "sections"
    parser.save_sections(sections_dir)
    
    # Save metadata as JSON
    metadata_path = output_dir / "apple_10k_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump({
            'metadata': result['metadata'],
            'stats': result['stats'],
            'section_names': list(result['sections'].keys())
        }, f, indent=2)
    print(f"💾 Saved metadata to: {metadata_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ PARSING COMPLETE")
    print("=" * 70)
    print(f"\n📁 Output directory: {output_dir.absolute()}")
    print(f"\nFiles created:")
    print(f"  1. apple_10k_clean.txt      - Full cleaned text")
    print(f"  2. sections/                - Individual section files")
    print(f"  3. apple_10k_metadata.json  - Metadata and stats")
    print()
    print("🎯 Next steps:")
    print("  - Examine the cleaned text")
    print("  - Check individual sections")
    print("  - Ready for chunking strategy!")
    print()
    
    return result


if __name__ == "__main__":
    test_parse_apple_filing()