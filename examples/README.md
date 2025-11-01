# Examples

This folder contains example scripts and demos for the Stock Research Assistant project.

## 🎯 Available Examples

### Main Pipeline
- **[pipeline_demo.py](pipeline_demo.py)** - Complete end-to-end pipeline
  - Parse SEC filing
  - Generate chunks
  - Create embeddings
  - Upload to Qdrant
  - Usage: `python examples/pipeline_demo.py`

### Query & Search
- **[query_demo.py](query_demo.py)** - Interactive search interface
  - Semantic search examples
  - Filtered search demos
  - Interactive mode
  - Usage: `python examples/query_demo.py` or `python examples/query_demo.py -i`

### Q&A System
- **[qa_api_demo.py](qa_api_demo.py)** - Question answering CLI demo
  - GPT-4 powered Q&A
  - Source citations
  - Interactive mode
  - Usage: `python examples/qa_api_demo.py`

### Cloud Integration
- **[qdrant_cloud_example.py](qdrant_cloud_example.py)** - Qdrant Cloud usage example
  - Cloud connection setup
  - Data upload
  - Search operations
  - Usage: `python examples/qdrant_cloud_example.py`

### Utility Scripts
- **[upload_to_qdrant_cloud.py](upload_to_qdrant_cloud.py)** - Upload local data to Qdrant Cloud
  - Migrate from local to cloud
  - Batch upload with progress
  - Cost estimation
  - Usage: `python examples/upload_to_qdrant_cloud.py`

- **[add_qdrant_indexes.py](add_qdrant_indexes.py)** - Add payload indexes to collection
  - Improve query performance
  - Add filters for metadata fields
  - Usage: `python examples/add_qdrant_indexes.py`

## 🚀 Quick Start

### 1. Run the Full Pipeline

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Or use the convenience script
./run_pipeline.sh
```

### 2. Query the Database

```bash
# Interactive mode
python examples/query_demo.py -i

# Direct query
python examples/query_demo.py "What is Apple's revenue?"
```

### 3. Ask Questions

```bash
# Start the Q&A demo
python examples/qa_api_demo.py
```

### 4. Use the API

```bash
# Start the API server
uvicorn api:app --reload --port 8000

# Visit http://localhost:8000/docs for interactive API documentation
```

## 📝 Notes

- All examples assume you've completed the [setup](../docs/SETUP.md)
- Make sure you have an OpenAI API key configured in `.env`
- For Qdrant Cloud examples, add cloud credentials to `.env`

## 🔗 Related Documentation

- [Main README](../README.md)
- [Setup Guide](../docs/SETUP.md)
- [Requirements](../docs/REQUIREMENTS.md)
- [Q&A Implementation](../docs/QA_IMPLEMENTATION_SUMMARY.md)
