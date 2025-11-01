# Dependency Management with pyproject.toml

This project uses `pyproject.toml` for modern Python dependency management. No more `requirements.txt`!

## 🎯 Quick Start

### Install Dependencies

```bash
# Standard pip
pip install -e .

# Or with uv (much faster!)
uv pip install -e .
```

The `-e` flag installs in "editable" mode - your code changes take effect immediately without reinstalling.

---

## 📦 What's Installed

### Core Dependencies (Always Installed)

All dependencies in `[project.dependencies]`:

```toml
dependencies = [
    "beautifulsoup4>=4.12.0",      # HTML parsing
    "lxml>=5.0.0",                  # Fast XML parser
    "langchain>=0.1.0",             # RAG framework
    "langchain-openai>=0.0.5",      # OpenAI integration
    "langchain-core>=0.1.0",        # LangChain core
    "openai>=1.12.0",               # OpenAI API
    "tiktoken>=0.5.0",              # Token counting
    "qdrant-client>=1.7.0",         # Vector database
    "python-dotenv>=1.0.0",         # Environment variables
    # ... and more
]
```

### Optional Dependencies

Install only what you need:

```bash
# Development tools (pytest, black, ruff, jupyter)
pip install -e ".[dev]"

# RAG alternatives (sentence-transformers, chromadb, anthropic)
pip install -e ".[rag]"

# Everything
pip install -e ".[dev,rag]"
```

---

## 🔧 Common Tasks

### Adding a New Dependency

**For a core dependency everyone needs:**

Edit `pyproject.toml`:

```toml
[project]
dependencies = [
    # ... existing deps
    "new-package>=1.0.0",  # Add here
]
```

Then reinstall:

```bash
pip install -e .
```

**For an optional dependency:**

```toml
[project.optional-dependencies]
dev = [
    "new-dev-tool>=1.0.0",
]
```

### Updating Dependencies

```bash
# Update all to latest compatible versions
pip install -e . --upgrade

# Update specific package
pip install --upgrade langchain
```

### Viewing Installed Packages

```bash
pip list
```

### Freezing Exact Versions

For reproducible builds, create a lock file:

```bash
pip freeze > requirements-lock.txt
```

Then others can install exact versions:

```bash
pip install -r requirements-lock.txt
```

---

## 🆚 pyproject.toml vs requirements.txt

| Feature | pyproject.toml | requirements.txt |
|---------|----------------|------------------|
| **Standard** | PEP 518 (modern) | Legacy |
| **Metadata** | ✅ Project name, version, author | ❌ Only dependencies |
| **Optional deps** | ✅ `[project.optional-dependencies]` | ❌ Need multiple files |
| **Version ranges** | ✅ `>=1.0.0,<2.0.0` | ✅ Same |
| **Editable install** | ✅ `pip install -e .` | ❌ Manual setup |
| **Tool configs** | ✅ black, ruff, pytest in one file | ❌ Separate files |

---

## 📝 Project Metadata in pyproject.toml

Our `pyproject.toml` includes:

```toml
[project]
name = "stock-research-assistant"
version = "0.1.0"
description = "AI-powered stock research assistant using RAG"
readme = "README.md"
requires-python = ">=3.9"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
```

This metadata is used when:
- Publishing to PyPI
- Generating documentation
- Showing project info (`pip show stock-research-assistant`)

---

## 🛠️ Tool Configuration

`pyproject.toml` also configures dev tools:

### Black (Code Formatter)

```toml
[tool.black]
line-length = 88
target-version = ['py39']
```

Usage:
```bash
black .
```

### Ruff (Linter)

```toml
[tool.ruff]
line-length = 88
select = ["E", "W", "F", "I"]
```

Usage:
```bash
ruff check .
ruff check . --fix  # Auto-fix issues
```

### Pytest (Testing)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

Usage:
```bash
pytest
```

---

## 🚀 Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a blazing-fast Python package installer (10-100x faster than pip).

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### Use uv Instead of pip

```bash
# Install dependencies
uv pip install -e .

# Install with optional dependencies
uv pip install -e ".[dev]"

# Add a package
uv pip install new-package

# Create virtual environment
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

**Why uv?**
- 10-100x faster than pip
- Better dependency resolution
- Caches packages globally
- Drop-in replacement for pip

---

## 📋 Migration from requirements.txt

If you have an old `requirements.txt`:

### Option 1: Keep Both (Transition Period)

Generate `requirements.txt` from `pyproject.toml`:

```bash
pip-compile pyproject.toml  # Requires pip-tools
```

Or manually:

```bash
pip freeze > requirements.txt
```

### Option 2: Full Migration

1. Move all dependencies to `pyproject.toml`
2. Delete `requirements.txt`
3. Update CI/CD to use `pip install -e .`
4. Update documentation

We've chosen **Option 2** - `requirements.txt` is deprecated in this project.

---

## 🔐 Security & Best Practices

### Version Pinning Strategies

**Development (our approach):**
```toml
"package>=1.0.0"  # Latest compatible version
```

**Production:**
```toml
"package==1.2.3"  # Exact version
```

Or use a lock file:
```bash
pip freeze > requirements-lock.txt
```

### Checking for Vulnerabilities

```bash
pip install safety
safety check
```

### Dependency Updates

Regularly update dependencies:

```bash
# Check outdated packages
pip list --outdated

# Update all (test thoroughly after!)
pip install -e . --upgrade
```

---

## 📚 Resources

- [PEP 518 - pyproject.toml](https://peps.python.org/pep-0518/)
- [Python Packaging Guide](https://packaging.python.org/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [pip Documentation](https://pip.pypa.io/)
