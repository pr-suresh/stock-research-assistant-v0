# Tests

This folder contains test scripts for the Stock Research Assistant project.

## 🧪 Available Tests

### Parser Tests
- **[test_parser.py](test_parser.py)** - Test SEC filing parser
  - Parse real Apple 10-K filing
  - Extract sections and metadata
  - Verify parsing statistics
  - Usage: `python tests/test_parser.py`

### Fetcher Tests
- **[test_sec_fetcher.py](test_sec_fetcher.py)** - Test SEC EDGAR fetcher
  - Look up CIK from ticker
  - Fetch recent filings
  - Download filing documents
  - Usage: `python tests/test_sec_fetcher.py`

### API Tests
- **[test_api.py](test_api.py)** - Test FastAPI endpoints
  - Test API endpoints
  - Verify responses
  - Usage: `python tests/test_api.py`

- **[test_embed_endpoint.py](test_embed_endpoint.py)** - Test embedding endpoint
  - Test embedding generation via API
  - Usage: `python tests/test_embed_endpoint.py`

### Q&A Tests
- **[test_qa_quick.py](test_qa_quick.py)** - Quick Q&A system test
  - Test question answering
  - Verify citations
  - Usage: `python tests/test_qa_quick.py`

## 🚀 Running Tests

### Run Individual Tests

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Run a specific test
python tests/test_parser.py
```

### Run All Tests (Future)

```bash
# When pytest is set up
pytest tests/
```

## 📝 Notes

- Tests use real data from the `data/filings/` directory
- Some tests require an OpenAI API key in `.env`
- Some tests may require running the pipeline first to have data in Qdrant

## 🔧 Test Data

Tests typically use the Apple 10-K filing located at:
```
data/filings/0000320193_0000320193-24-000123_aapl-20240928.htm
```

## 🔗 Related Documentation

- [Main README](../README.md)
- [Setup Guide](../docs/SETUP.md)
- [Requirements](../docs/REQUIREMENTS.md)
