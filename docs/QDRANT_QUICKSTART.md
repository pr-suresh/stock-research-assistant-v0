# Qdrant Integration - Quick Start

Your SEC filing RAG pipeline now supports **Qdrant** vector database with both local and cloud options!

## ⚡ Quick Setup

### 1. Install Dependencies

```bash
# Install everything from pyproject.toml
pip install -e .

# Or with uv (faster)
uv pip install -e .
```

This installs `qdrant-client>=1.7.0` and all other dependencies.

### 2. Choose Your Setup

#### Option A: Local Storage (Easiest - Default)

No configuration needed! Just run:

```bash
python pipeline_demo.py
```

Data is stored in `./data/processed/qdrant_storage/`

#### Option B: Qdrant Cloud (Production)

1. **Sign up**: [https://cloud.qdrant.io](https://cloud.qdrant.io) (free tier)
2. **Create cluster** and get credentials
3. **Add to `.env`**:
   ```bash
   QDRANT_URL=https://your-cluster-id.cloud.qdrant.io
   QDRANT_API_KEY=your-api-key-here
   ```
4. **Run pipeline**:
   ```bash
   python pipeline_demo.py
   ```

The pipeline **auto-detects** cloud credentials and uses them automatically!

---

## 🚀 Usage

### Store Data (Pipeline)

```bash
# Run the full pipeline: Parse → Chunk → Embed → Store
python pipeline_demo.py
```

**Output:**
- ✅ Parses SEC filing
- ✅ Creates chunks with metadata
- ✅ Generates embeddings
- ✅ Stores in Qdrant (cloud or local)

### Query Data

```bash
# Run demo examples
python query_demo.py

# Interactive mode
python query_demo.py -i

# Direct query
python query_demo.py "What is Apple's revenue?"
```

### Try Cloud Example

```bash
python examples/qdrant_cloud_example.py
```

---

## 🔧 Configuration

### Environment Variables

Create/edit `.env` file:

```bash
# Required: OpenAI API key for embeddings
OPENAI_API_KEY=your-openai-key

# Optional: Qdrant Cloud (if not set, uses local storage)
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-key
```

### In Code

```python
from src.vector_store import QdrantVectorStore

# Auto-detect from environment (recommended)
store = QdrantVectorStore(collection_name="sec_filings")

# Explicit local storage
store = QdrantVectorStore(
    collection_name="sec_filings",
    path="./data/qdrant"
)

# Explicit cloud
store = QdrantVectorStore(
    collection_name="sec_filings",
    url="https://xxx.cloud.qdrant.io",
    api_key="your-key"
)
```

---

## 📊 Features

### Metadata Filtering

Every chunk is stored with rich metadata:

```python
{
    'ticker': 'AAPL',
    'company': 'Apple Inc.',
    'filing_type': '10-K',
    'filing_date': '2024-09-28',
    'section': 'Business',
    'source': 'filename.htm'
}
```

### Search with Filters

```python
# Search only AAPL filings
results = store.search(
    query_vector,
    filter={"ticker": "AAPL"},
    limit=5
)

# Multiple filters
results = store.search(
    query_vector,
    filter={
        "ticker": "AAPL",
        "filing_type": "10-K"
    }
)

# Minimum similarity threshold
results = store.search(
    query_vector,
    score_threshold=0.7
)
```

---

## 📁 File Structure

```
stock-research-assistant-v0/
├── src/
│   ├── vector_store.py          # Qdrant integration
│   ├── embeddings.py             # OpenAI embeddings
│   ├── sec_parser.py             # SEC filing parser
│   └── text_chunker.py           # Text chunking
├── examples/
│   └── qdrant_cloud_example.py  # Cloud usage demo
├── pipeline_demo.py              # Full pipeline
├── query_demo.py                 # Query interface
├── pyproject.toml                # Dependencies (includes qdrant-client)
├── .env.example                  # Environment template
├── QDRANT_SETUP.md              # Detailed setup guide
└── DEPENDENCY_MANAGEMENT.md     # pyproject.toml guide
```

---

## 🆚 Local vs Cloud Comparison

| Feature | Local Storage | Qdrant Cloud |
|---------|---------------|--------------|
| **Setup** | Zero config | Sign up + credentials |
| **Cost** | Free | Free tier (1GB) |
| **Speed** | Fast (local disk) | Fast (global CDN) |
| **Scalability** | Single machine | Unlimited |
| **Collaboration** | Local only | Team access |
| **Backups** | Manual | Automatic |
| **Best for** | Development | Production |

---

## 🎯 Common Workflows

### Development Workflow

```bash
# 1. Use local storage for development
python pipeline_demo.py

# 2. Test queries locally
python query_demo.py -i

# 3. When ready, switch to cloud
# Add QDRANT_URL and QDRANT_API_KEY to .env
# Run pipeline again - data goes to cloud!
```

### Production Workflow

```bash
# 1. Set up Qdrant Cloud in .env
# 2. Run pipeline for all SEC filings
# 3. Deploy query API
# 4. Scale as needed
```

---

## 📚 Documentation

- **[QDRANT_SETUP.md](QDRANT_SETUP.md)** - Detailed Qdrant setup guide
- **[DEPENDENCY_MANAGEMENT.md](DEPENDENCY_MANAGEMENT.md)** - pyproject.toml guide
- **[Qdrant Docs](https://qdrant.tech/documentation/)** - Official Qdrant docs
- **[Qdrant Cloud](https://cloud.qdrant.io)** - Cloud dashboard

---

## ❓ FAQ

**Q: Do I need Docker?**
A: No! Use local storage (default) or Qdrant Cloud. Docker is optional.

**Q: What's the free tier for Qdrant Cloud?**
A: 1GB storage, 100 ops/sec - plenty for thousands of SEC filings.

**Q: Can I switch from local to cloud later?**
A: Yes! Just add credentials to `.env` and re-run the pipeline.

**Q: How do I know if I'm using cloud or local?**
A: The pipeline prints: `☁️ Using Qdrant Cloud` or `💾 Using local storage`

**Q: Is my data safe in Qdrant Cloud?**
A: Yes - encrypted at rest and in transit, automatic backups, SOC2 compliant.

---

## 🆘 Troubleshooting

**Can't connect to Qdrant:**
- Check `.env` file has correct credentials
- Try local storage: remove `QDRANT_URL` from `.env`

**"Collection not found":**
- Run `pipeline_demo.py` first to create collection

**Import errors:**
- Run `pip install -e .` to install dependencies

**Need help?**
- Check [QDRANT_SETUP.md](QDRANT_SETUP.md) for detailed guide
- Open GitHub issue
- Check Qdrant docs

---

## 🚀 Next Steps

1. ✅ Run `pipeline_demo.py` to test integration
2. ✅ Try `query_demo.py -i` for interactive search
3. ✅ Consider Qdrant Cloud for production
4. 🔜 Add LLM for answer generation (RAG)
5. 🔜 Build web interface
6. 🔜 Process multiple SEC filings

Happy building! 🎉
