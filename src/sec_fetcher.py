"""
SEC EDGAR Fetcher - Compliant Financial Data Retrieval

This module handles fetching financial filings from the SEC's EDGAR system.
We're building this carefully to understand each component and follow SEC rules.
"""

import requests
import time
import json
from typing import Dict, List, Optional
from pathlib import Path


class SECFetcher:
    """
    Fetches financial filings from SEC EDGAR system.
    
    WHY THIS CLASS EXISTS:
    - Centralize SEC API access with proper compliance
    - Handle rate limiting automatically
    - Provide clean interface for getting company filings
    
    SEC RULES WE MUST FOLLOW:
    1. Declare User-Agent with identity (name + email)
    2. Max 10 requests per second
    3. Use official APIs, not web scraping
    """
    
    def __init__(self, user_agent_name: str, user_agent_email: str):
        """
        Initialize the fetcher with required identity information.
        
        Args:
            user_agent_name: Your name or company name
            user_agent_email: Your contact email
            
        WHY WE NEED THIS:
        The SEC requires you to identify yourself. This helps them:
        - Contact you if there's an issue
        - Track usage patterns
        - Block abusive users while allowing legitimate ones
        """
        # Build compliant User-Agent header
        # Format: "YourName/YourEmail"
        self.headers = {
            'User-Agent': f'{user_agent_name} {user_agent_email}',
            'Accept-Encoding': 'gzip, deflate'
        }
        
        # Base URL for SEC EDGAR API
        self.base_url = 'https://data.sec.gov'
        
        # Track last request time for rate limiting
        # WHY: SEC allows max 10 requests/second. We'll be conservative: 1 per 0.2s
        self.last_request_time = 0
        self.min_request_interval = 0.2  # 5 requests per second (being safe)
        
    def _rate_limit(self):
        """
        Enforce rate limiting before making requests.
        
        WHY THIS EXISTS:
        Without rate limiting, we could:
        - Get our IP banned from SEC
        - Overwhelm their servers
        - Violate their terms of service
        
        HOW IT WORKS:
        - Track time of last request
        - If too soon, sleep until enough time has passed
        - This ensures we never exceed rate limit
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, url: str) -> requests.Response:
        """
        Make a rate-limited request to SEC API.
        
        WHY THIS IS A SEPARATE METHOD:
        - Centralize rate limiting logic
        - Handle errors consistently
        - Make code more testable
        
        Args:
            url: Full URL to request
            
        Returns:
            Response object
            
        Raises:
            requests.HTTPError: If request fails
        """
        self._rate_limit()
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()  # Raise exception for 4xx/5xx status codes
        
        return response
    
    def get_company_cik(self, ticker: str) -> Optional[str]:
        """
        Convert stock ticker to CIK (Central Index Key).
        
        WHY WE NEED THIS:
        The SEC doesn't use ticker symbols (AAPL, MSFT, etc).
        Instead, they use CIK - a unique 10-digit identifier for each company.
        
        Example: AAPL = 0000320193
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            CIK string with leading zeros, or None if not found
        """
        # SEC provides a ticker-to-CIK mapping JSON file
        # Note: This specific endpoint uses www.sec.gov, not data.sec.gov
        url = 'https://www.sec.gov/files/company_tickers.json'
        
        try:
            response = self._make_request(url)
            companies = response.json()
            
            # The JSON structure is: {0: {ticker: "AAPL", cik_str: 320193, ...}, ...}
            ticker_upper = ticker.upper()
            
            for company in companies.values():
                if company['ticker'] == ticker_upper:
                    # CIK must be 10 digits with leading zeros
                    cik = str(company['cik_str']).zfill(10)
                    return cik
            
            return None
            
        except requests.RequestException as e:
            print(f"Error fetching CIK for {ticker}: {e}")
            return None
    
    def get_company_filings(
        self, 
        cik: str, 
        filing_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get list of filings for a company.
        
        WHY THIS IS USEFUL:
        Before downloading documents, we need to know what's available.
        This gives us a list of all filings with metadata.
        
        Args:
            cik: Company's CIK (10-digit string with leading zeros)
            filing_type: Filter by type (e.g., '10-K', '10-Q'). None = all types
            limit: Max number of filings to return
            
        Returns:
            List of filing dictionaries with metadata
        """
        # SEC provides JSON endpoint for company submissions
        # Format: /submissions/CIK{cik}.json
        url = f'{self.base_url}/submissions/CIK{cik}.json'
        
        try:
            response = self._make_request(url)
            data = response.json()
            
            # Extract recent filings
            filings = data.get('filings', {}).get('recent', {})
            
            # Convert from columnar format to list of dicts
            filing_list = []
            num_filings = len(filings.get('form', []))
            
            # Search through all filings and collect matches
            for i in range(num_filings):
                filing = {
                    'form': filings['form'][i],
                    'filing_date': filings['filingDate'][i],
                    'accession_number': filings['accessionNumber'][i],
                    'primary_document': filings['primaryDocument'][i],
                }
                
                # Filter by type if specified
                if filing_type is None or filing['form'] == filing_type:
                    filing_list.append(filing)
                    
                    # Stop once we have enough matches
                    if len(filing_list) >= limit:
                        break
            
            return filing_list
            
        except requests.RequestException as e:
            print(f"Error fetching filings for CIK {cik}: {e}")
            return []
    
    def download_filing(
        self, 
        cik: str, 
        accession_number: str, 
        primary_document: str,
        save_dir: Path
    ) -> Optional[Path]:
        """
        Download a specific filing document.
        
        HOW SEC URLS WORK:
        URL format: https://www.sec.gov/Archives/edgar/data/{CIK}/{ACCESSION}/{DOCUMENT}
        
        Example:
        - CIK: 0000320193 (Apple)
        - Accession: 0000320193-23-000077 (but we remove dashes for URL)
        - Document: aapl-20230930.htm
        
        Args:
            cik: Company CIK
            accession_number: Filing accession number (with dashes)
            primary_document: Name of primary document file
            save_dir: Directory to save file
            
        Returns:
            Path to saved file, or None if download failed
        """
        # Remove dashes from accession number for URL
        # '0000320193-23-000077' becomes '000032019323000077'
        accession_no_dashes = accession_number.replace('-', '')
        
        # Build download URL
        # Note: Using www.sec.gov for documents, not data.sec.gov
        url = f'https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no_dashes}/{primary_document}'
        
        try:
            response = self._make_request(url)
            
            # Create save directory if it doesn't exist
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # Save with informative filename
            filename = f'{cik}_{accession_number}_{primary_document}'
            save_path = save_dir / filename
            
            save_path.write_bytes(response.content)
            print(f"Downloaded: {save_path}")
            
            return save_path
            
        except requests.RequestException as e:
            print(f"Error downloading filing: {e}")
            return None


# EXAMPLE USAGE (commented out - we'll test in a separate script)
if __name__ == "__main__":
    # Initialize with your identity
    fetcher = SECFetcher(
        user_agent_name="YourName",  # REPLACE WITH YOUR NAME
        user_agent_email="your.email@example.com"  # REPLACE WITH YOUR EMAIL
    )
    
    # Get Apple's CIK
    cik = fetcher.get_company_cik("AAPL")
    print(f"Apple CIK: {cik}")
    
    # Get recent 10-K filings
    if cik:
        filings = fetcher.get_company_filings(cik, filing_type="10-K", limit=3)
        for filing in filings:
            print(f"Filing: {filing['form']} - {filing['filing_date']}")