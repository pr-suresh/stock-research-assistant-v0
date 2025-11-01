# Stock Research Assistant

AI-powered Retrieval-Augmented Generation (RAG) system for analyzing SEC filings and answering questions about public company financial data.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd stock-research-assistant-v0

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -e .

# 4. Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 5. Run the pipeline
python examples/pipeline_demo.py

# 6. Query the database
python examples/query_demo.py -i
```

---

## 📋 What It Does

1. **Parse SEC Filings** - Extract clean text from HTML/XBRL documents
2. **Intelligent Chunking** - Break documents into semantic chunks with metadata
3. **Generate Embeddings** - Convert text to vectors using OpenAI
4. **Vector Storage** - Store in Qdrant (local or cloud)
5. **Semantic Search** - Ask questions in natural language, get relevant answers

---

## 💡 Features

### ✅ Implemented (MVP)
- SEC HTML/XBRL parsing
- Intelligent text chunking with metadata
- OpenAI embedding generation
- Qdrant vector storage (local & cloud)
- Semantic search with filtering
- Interactive query CLI
- GPT-4 Q&A with source citations
- REST API with FastAPI
- Cloud upload utilities
- Comprehensive documentation

### 🔮 Planned
- Web UI (React/Streamlit)
- Multi-turn conversations
- Automated SEC filing ingestion
- Financial metrics extraction
- Multi-filing comparative analysis

---

## 📖 Documentation

- **[SETUP.md](docs/SETUP.md)** - Installation and setup guide
- **[REQUIREMENTS.md](docs/REQUIREMENTS.md)** - Comprehensive requirements & implementation details
- **[QDRANT_QUICKSTART.md](docs/QDRANT_QUICKSTART.md)** - Quick Qdrant reference
- **[QDRANT_SETUP.md](docs/QDRANT_SETUP.md)** - Detailed Qdrant configuration
- **[DEPENDENCY_MANAGEMENT.md](docs/DEPENDENCY_MANAGEMENT.md)** - Guide to pyproject.toml
- **[QA_IMPLEMENTATION_SUMMARY.md](docs/QA_IMPLEMENTATION_SUMMARY.md)** - Q&A system implementation guide

---

<details>
<summary><h2>🏗️ Architecture</h2></summary>

```
SEC Filing (HTML) → Parser → Chunker → Embeddings → Qdrant → Query Interface
```

### Core Components

| Module | Purpose |
|--------|---------|
| `sec_parser.py` | Parse and clean SEC HTML/XBRL filings |
| `text_chunker.py` | Split text into chunks with metadata |
| `embeddings.py` | Generate OpenAI embeddings |
| `vector_store.py` | Qdrant database interface |
| `qa_engine.py` | RAG question answering |

</details>

---

<details>
<summary><h2>📊 Example Usage</h2></summary>

### Process a Filing

```bash
python examples/pipeline_demo.py
```

**Output:**
- Parsed: 500,000 characters
- Chunks: 117 documents
- Embeddings: 117 vectors (1536-dim)
- Cost: ~$0.001
- Time: ~30-60 seconds

### Query the Database

```bash
# Interactive mode
python examples/query_demo.py -i

# Direct query
python examples/query_demo.py "What is Apple's revenue?"

# Example output:
# 1. [Score: 0.85] Apple Inc. reported total revenue of $391.0 billion...
# 2. [Score: 0.82] iPhone revenue was $201.2 billion, representing 52%...
```

### Search with Filters

```python
from src.vector_store import QdrantVectorStore
from src.embeddings import EmbeddingGenerator

# Initialize
store = QdrantVectorStore()
embedder = EmbeddingGenerator()

# Search
query = "What are the risk factors?"
query_vector = embedder.embed_query(query)

results = store.search(
    query_vector,
    filter={"ticker": "AAPL", "section": "Risk Factors"},
    limit=5
)
```

### Q&A with GPT-4

```bash
# Run Q&A demo
python examples/qa_api_demo.py

# Or use the API
uvicorn api:app --reload --port 8000
# Visit http://localhost:8000/docs
```

</details>

---

<details>
<summary><h2>🛠️ Tech Stack</h2></summary>

- **Language:** Python 3.9+
- **Parsing:** BeautifulSoup4, lxml
- **RAG Framework:** LangChain
- **Embeddings:** OpenAI API (text-embedding-3-small)
- **LLM:** OpenAI GPT-4 Turbo
- **Vector DB:** Qdrant
- **Web Framework:** FastAPI

</details>

---

<details>
<summary><h2>📁 Project Structure</h2></summary>

```
stock-research-assistant-v0/
├── src/                       # Core modules
│   ├── sec_parser.py         # SEC filing parser
│   ├── text_chunker.py       # Text chunking
│   ├── embeddings.py         # OpenAI embeddings
│   ├── vector_store.py       # Qdrant interface
│   ├── qa_engine.py          # Q&A RAG engine
│   └── prompts.py            # LLM prompts
├── examples/                  # Demo scripts & utilities
│   ├── pipeline_demo.py      # End-to-end pipeline
│   ├── query_demo.py         # Query interface
│   ├── qa_api_demo.py        # Q&A CLI demo
│   ├── upload_to_qdrant_cloud.py  # Cloud upload
│   └── add_qdrant_indexes.py      # Index management
├── tests/                     # Test scripts
│   ├── test_parser.py
│   ├── test_api.py
│   └── test_qa_quick.py
├── docs/                      # Documentation
│   ├── SETUP.md
│   ├── REQUIREMENTS.md
│   ├── QDRANT_QUICKSTART.md
│   └── QA_IMPLEMENTATION_SUMMARY.md
├── data/
│   ├── filings/              # Raw SEC HTML files
│   └── processed/            # Processed chunks & embeddings
├── api.py                     # FastAPI server
├── pyproject.toml            # Dependencies
├── .env.example              # Environment template
└── LICENSE                    # MIT License
```

</details>

---

<details>
<summary><h2>🔧 Configuration</h2></summary>

### Environment Variables

```bash
# Required: OpenAI API key
OPENAI_API_KEY=sk-...

# Optional: Qdrant Cloud
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-api-key

# Optional: Q&A Configuration
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=1000
```

### Deployment Options

| Mode | Setup | Use Case |
|------|-------|----------|
| **Local Storage** | None | Development, testing |
| **Qdrant Cloud** | Sign up at cloud.qdrant.io | Production, collaboration |
| **Local Server** | Docker | Development with API |

</details>

---

<details>
<summary><h2>💰 Cost Breakdown</h2></summary>

### OpenAI Embeddings
- Model: `text-embedding-3-small`
- Cost: $0.02 per 1M tokens
- **~$0.001 per 10-K filing**

### GPT-4 Q&A
- Model: `gpt-4-turbo-preview`
- Cost: ~$0.01-0.03 per query
- **~$0.015 average per query**

### Qdrant Cloud
- **Free tier:** 1GB storage (≈10,000 filings)
- Paid plans from $25/month

### Example Costs

| Scale | Filings | Embedding Cost | Monthly Queries | Q&A Cost | Total |
|-------|---------|----------------|-----------------|----------|-------|
| Small | 100 | $0.10 | 100 | $1.50 | ~$2 |
| Medium | 1,000 | $1.00 | 500 | $7.50 | ~$9 |
| Large | 10,000 | $10.00 | 5,000 | $75.00 | ~$85 |

</details>

---

<details>
<summary><h2>🎯 Use Cases</h2></summary>

- **Financial Analysts:** Quick insights from SEC filings
- **Investors:** Research multiple companies efficiently
- **Compliance Teams:** Track regulatory changes
- **Researchers:** Analyze filing trends over time
- **Developers:** Build financial data applications

### Example Queries

```
"What is Apple's revenue?"
"Tell me about iPhone sales"
"What are the main risk factors?"
"How much does the company spend on R&D?"
"What are the key products and services?"
"Describe the competitive landscape"
"What segments does the company operate in?"
```

</details>

---

<details>
<summary><h2>🚧 Roadmap</h2></summary>

### Phase 1: MVP (✅ Complete)
- [x] SEC parsing & chunking
- [x] Embedding generation
- [x] Vector storage
- [x] Basic search interface

### Phase 2: Enhanced Query (✅ Complete)
- [x] LLM answer generation
- [x] Source citations
- [x] REST API
- [ ] Multi-turn conversations
- [ ] Query refinement

### Phase 3: Web Interface
- [ ] React/Streamlit UI
- [ ] User authentication
- [ ] Visualization

### Phase 4: Scale
- [ ] Automated filing ingestion
- [ ] Multi-filing support
- [ ] Financial metrics extraction
- [ ] Trend analysis

</details>

---

<details>
<summary><h2>🤝 Contributing</h2></summary>

Contributions welcome! Areas of interest:
- Additional filing types (8-K, proxy statements)
- Performance optimizations
- UI/UX improvements
- Documentation
- Testing

### How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

</details>

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- **OpenAI** - Embedding API and GPT-4
- **Qdrant** - Vector database
- **LangChain** - RAG framework
- **BeautifulSoup** - HTML parsing

---

## 📞 Support

For issues, questions, or suggestions:
1. Check the [SETUP.md](docs/SETUP.md) guide
2. Review [troubleshooting](docs/SETUP.md#troubleshooting) section
3. See [REQUIREMENTS.md](docs/REQUIREMENTS.md) for detailed implementation info

---

**Version:** 0.1.0 | **Status:** MVP Complete ✅ | **Last Updated:** November 1, 2025
