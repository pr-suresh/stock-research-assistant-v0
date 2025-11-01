"""
Test script for SEC Fetcher

This demonstrates how to use the SECFetcher class.
Run this to verify everything works correctly.
"""

from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from sec_fetcher import SECFetcher


def test_fetcher():
    """
    Test the SEC fetcher with a real example.
    
    WHAT THIS DOES:
    1. Looks up Apple's CIK from ticker symbol
    2. Gets their recent 10-K filings (annual reports)
    3. Downloads the most recent one
    """
    
    print("=" * 60)
    print("SEC EDGAR Fetcher Test")
    print("=" * 60)
    
    # TODO: REPLACE THESE WITH YOUR INFORMATION
    # The SEC requires you to identify yourself
    fetcher = SECFetcher(
        user_agent_name="Praveena S",  # <-- CHANGE THIS
        user_agent_email="praveena.suresh@outlook.com"  # <-- CHANGE THIS
    )
    
    # Test with Apple
    ticker = "AAPL"
    print(f"\n1. Looking up CIK for {ticker}...")
    
    cik = fetcher.get_company_cik(ticker)
    if not cik:
        print(f"❌ Could not find CIK for {ticker}")
        return
    
    print(f"✅ Found CIK: {cik}")
    
    # Get recent 10-K filings
    print(f"\n2. Fetching recent 10-K filings...")
    filings = fetcher.get_company_filings(cik, filing_type="10-K", limit=3)
    
    if not filings:
        print("❌ No filings found")
        return
    
    print(f"✅ Found {len(filings)} filings:")
    for i, filing in enumerate(filings, 1):
        print(f"   {i}. {filing['form']} - {filing['filing_date']}")
    
    # Download the most recent one
    print(f"\n3. Downloading most recent filing...")
    latest = filings[0]
    
    save_dir = Path(__file__).parent / 'data' / 'filings'
    
    file_path = fetcher.download_filing(
        cik=cik,
        accession_number=latest['accession_number'],
        primary_document=latest['primary_document'],
        save_dir=save_dir
    )
    
    if file_path:
        print(f"✅ Downloaded successfully!")
        print(f"   Location: {file_path}")
        print(f"   Size: {file_path.stat().st_size / 1024:.1f} KB")
    else:
        print("❌ Download failed")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_fetcher()