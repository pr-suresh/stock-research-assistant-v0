# Qdrant Setup Guide

This guide shows you how to set up Qdrant for your SEC filing RAG system, with three options: local storage, local server, or cloud.

## 📦 Installation

All dependencies are managed in `pyproject.toml`. Install with:

```bash
# Install all dependencies
pip install -e .

# Or with uv (faster)
uv pip install -e .
```

This installs `qdrant-client` and all other required packages.

---

## 🚀 Option 1: Local Storage (Recommended for Development)

**Best for:** Local development, testing, no setup needed

**Pros:**
- No Docker or cloud account needed
- Persistent storage on disk
- Perfect for development and testing

**Setup:**

```python
from src.vector_store import QdrantVectorStore

# Just specify a local path
store = QdrantVectorStore(
    collection_name="sec_filings",
    path="./data/qdrant_storage"  # Data saved here
)
```

That's it! The pipeline already uses this by default.

---

## ☁️ Option 2: Qdrant Cloud (Recommended for Production)

**Best for:** Production, sharing data across team, scalability

**Pros:**
- Managed service (no infrastructure)
- Fast global CDN
- Automatic backups
- Free tier: 1GB storage, 100 ops/sec

### Step 1: Sign Up

1. Go to [https://cloud.qdrant.io](https://cloud.qdrant.io)
2. Sign up (free account)
3. Create a new cluster

### Step 2: Get Credentials

From your Qdrant Cloud dashboard:
- **Cluster URL**: `https://your-cluster-id.cloud.qdrant.io`
- **API Key**: Click "API Keys" → "Create New Key"

### Step 3: Configure Environment

Add to your `.env` file:

```bash
# Qdrant Cloud Configuration
QDRANT_URL=https://your-cluster-id.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key-here
```

### Step 4: Use in Code

```python
from src.vector_store import QdrantVectorStore

# Auto-detects cloud config from environment
store = QdrantVectorStore(
    collection_name="sec_filings"
)
# ✅ Connected to Qdrant Cloud: https://xxx.cloud.qdrant.io
```

Or specify explicitly:

```python
store = QdrantVectorStore(
    collection_name="sec_filings",
    url="https://your-cluster-id.cloud.qdrant.io",
    api_key="your-api-key"
)
```

---

## 🐳 Option 3: Local Docker Server

**Best for:** Local development with server experience

**Pros:**
- Full Qdrant server features
- REST API available
- Web dashboard UI

### Step 1: Start Qdrant Server

```bash
# Pull and run Qdrant
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

### Step 2: Use in Code

```python
from src.vector_store import QdrantVectorStore

# Connects to localhost:6333 by default
store = QdrantVectorStore(
    collection_name="sec_filings",
    host="localhost",
    port=6333
)
```

### Step 3: Access Web Dashboard

Open [http://localhost:6333/dashboard](http://localhost:6333/dashboard) to view collections and data.

---

## 🔄 Switching Between Options

The vector store auto-detects configuration in this priority:

1. **Path parameter** → Local storage
2. **QDRANT_URL env var** or **url parameter** → Cloud/Server
3. **host/port parameters** → Local server
4. **Default** → Local server at localhost:6333

### Examples

```python
# Local storage (highest priority)
store = QdrantVectorStore(path="./data/qdrant")

# Cloud (reads from .env)
store = QdrantVectorStore()  # QDRANT_URL must be set

# Cloud (explicit)
store = QdrantVectorStore(
    url="https://xxx.cloud.qdrant.io",
    api_key="your-key"
)

# Local server
store = QdrantVectorStore(host="localhost", port=6333)
```

---

## 📊 Verifying Connection

Test your setup:

```bash
# Test vector store
cd /Users/psuresh/Projects2025/stock-research-assistant-v0
python -c "from src.vector_store import test_vector_store; test_vector_store()"
```

Or run the full pipeline:

```bash
python pipeline_demo.py
```

---

## 💡 Recommendations

| Use Case | Recommendation |
|----------|---------------|
| **Local development** | Local storage (`path="./data/qdrant"`) |
| **Testing** | Local storage or Docker |
| **Production** | Qdrant Cloud |
| **Team collaboration** | Qdrant Cloud |
| **Large datasets (>10GB)** | Qdrant Cloud or self-hosted server |

---

## 🆘 Troubleshooting

### "Connection refused" error

**Problem:** Can't connect to Qdrant server

**Solutions:**
1. If using Docker: Make sure it's running (`docker ps`)
2. Switch to local storage: `QdrantVectorStore(path="./data/qdrant")`
3. Check firewall settings

### "Authentication failed" error

**Problem:** Invalid Qdrant Cloud API key

**Solutions:**
1. Check your `.env` file has correct credentials
2. Regenerate API key in Qdrant Cloud dashboard
3. Make sure you're using the right cluster URL

### "Collection already exists" error

**Problem:** Collection created with different vector size

**Solutions:**
```python
# Delete and recreate collection
store.delete_collection()
store = QdrantVectorStore()  # Recreates with correct size
```

---

## 📚 Additional Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client)
- [Qdrant Cloud](https://cloud.qdrant.io)
