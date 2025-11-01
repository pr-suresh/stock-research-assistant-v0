# Setup Guide

## ✅ Installation Complete!

Your environment has been successfully set up with Python 3.13 and all dependencies.

---

## 🚀 Quick Start

### 1. Activate Virtual Environment

**Every time you open a new terminal**, activate the virtual environment:

```bash
source .venv/bin/activate
```

You should see `(.venv)` prefix in your terminal.

### 2. Run the Pipeline

```bash
# Option 1: Use the convenience script
./run_pipeline.sh

# Option 2: Manual
source .venv/bin/activate
python pipeline_demo.py
```

### 3. Query the Database

```bash
source .venv/bin/activate

# Demo examples
python query_demo.py

# Interactive mode
python query_demo.py -i

# Direct query
python query_demo.py "What is Apple's revenue?"
```

---

## 📝 What's Installed

All dependencies from [pyproject.toml](pyproject.toml) are now installed:

✅ **Core Libraries:**
- `beautifulsoup4` + `lxml` - HTML/XML parsing
- `langchain` + `langchain-openai` - RAG framework
- `openai` + `tiktoken` - Embeddings & token counting
- `qdrant-client` - Vector database
- `pandas` + `numpy` - Data processing
- `fastapi` + `uvicorn` - Web framework (for future API)

✅ **Python Version:** 3.13.2

✅ **Total packages:** 80+ (including all dependencies)

---

## 🔧 Configuration

### Environment Variables

Create/edit `.env` file:

```bash
# Required: OpenAI API key
OPENAI_API_KEY=your-openai-key-here

# Optional: Qdrant Cloud (leave blank for local storage)
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-key-here
```

See [.env.example](.env.example) for template.

---

## 🐛 Troubleshooting

### "Command not found" errors

Make sure virtual environment is activated:
```bash
source .venv/bin/activate
```

### "Module not found" errors

Reinstall dependencies:
```bash
source .venv/bin/activate
pip install -e .
```

### "File not found" error when running pipeline

The pipeline looks for the SEC filing at:
```
data/filings/0000320193_0000320193-24-000123_aapl-20240928.htm
```

✅ This file already exists! If you add more SEC filings:
1. Place them in `data/filings/`
2. Update the `filing_path` in `pipeline_demo.py` (line 46)

### Python version issues

This project requires Python 3.9+. You're using Python 3.13.2 ✅

Check version:
```bash
python --version
```

### Import errors from src/

The `-e` flag in `pip install -e .` makes the `src/` directory importable. If you still have issues, try:

```bash
pip uninstall stock-research-assistant
pip install -e .
```

### "OpenAI API key not found" error

Add your API key to `.env`:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

---

## 📁 Project Structure

```
stock-research-assistant-v0/
├── .venv/                    # Virtual environment (Python 3.13)
├── src/
│   ├── vector_store.py       # Qdrant integration ⭐
│   ├── embeddings.py         # OpenAI embeddings
│   ├── sec_parser.py         # SEC filing parser
│   └── text_chunker.py       # Text chunking
├── pipeline_demo.py          # Full pipeline ⭐
├── query_demo.py             # Query interface ⭐
├── run_pipeline.sh           # Convenience script ⭐
├── pyproject.toml            # Dependencies
├── .env                      # Your secrets (not in git)
└── .env.example              # Template
```

---

## 🎯 Next Steps

1. **Set up OpenAI API key** (required):
   - Get key from https://platform.openai.com/api-keys
   - Add to `.env` file:
     ```bash
     OPENAI_API_KEY=your-key-here
     ```

2. **Verify SEC filing is present**:
   - ✅ File already exists at: `data/filings/0000320193_0000320193-24-000123_aapl-20240928.htm`
   - This is Apple's 2024 10-K filing (1.4MB)

3. **Run the pipeline**:
   ```bash
   source .venv/bin/activate
   ./run_pipeline.sh
   ```

   This will:
   - Parse the SEC filing
   - Create text chunks
   - Generate embeddings (costs ~$0.001)
   - Store in Qdrant vector database

4. **Try querying**:
   ```bash
   source .venv/bin/activate
   python query_demo.py -i
   ```

5. **Optional: Set up Qdrant Cloud**:
   - Sign up at https://cloud.qdrant.io (free tier)
   - Add credentials to `.env`:
     ```bash
     QDRANT_URL=https://your-cluster.cloud.qdrant.io
     QDRANT_API_KEY=your-key
     ```
   - Pipeline will auto-detect and use cloud

---

## 📚 Documentation

- **[QDRANT_QUICKSTART.md](QDRANT_QUICKSTART.md)** - Quick Qdrant reference
- **[QDRANT_SETUP.md](QDRANT_SETUP.md)** - Detailed Qdrant guide
- **[DEPENDENCY_MANAGEMENT.md](DEPENDENCY_MANAGEMENT.md)** - pyproject.toml guide

---

## 💡 Tips

### Use the convenience script

```bash
./run_pipeline.sh
```

### Check what's installed

```bash
source .venv/bin/activate
pip list | grep -E "langchain|qdrant|openai"
```

### Update dependencies

```bash
source .venv/bin/activate
pip install -e . --upgrade
```

### Deactivate virtual environment

```bash
deactivate
```

---

## ✅ Verification

To verify everything is working:

```bash
source .venv/bin/activate
python -c "from src.vector_store import QdrantVectorStore; print('✅ Imports working!')"
```

Should print: `✅ Imports working!`

---

## 🆘 Getting Help

If you encounter issues:

1. Make sure virtual environment is activated
2. Check `.env` file has OpenAI API key
3. Try reinstalling: `pip install -e . --force-reinstall`
4. Check Python version: `python --version` (should be 3.9+)

Happy coding! 🚀
