# Stock Research Assistant

AI-powered stock research tool combining live market data, SEC filings analysis, and multi-step reasoning to answer complex financial questions.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**🔗 Live Demo:** https://stock-research-assistant-v0.vercel.app

**📚 API Docs:** [https://stock-research-assistant-v0.onrender.com/docs](https://stock-research-assistant-v0.onrender.com/docs)

---

## ✨ Features

- **🤖 AI Agent:** Multi-step reasoning with GPT-4 for complex queries
- **📈 Live Stock Data:** Real-time prices, volume, and market cap via Yahoo Finance
- **📄 SEC Filings:** RAG-powered analysis of 10-K documents
- **💬 Chat Interface:** Clean Next.js UI with message history and tool visibility
- **🔧 REST API:** FastAPI backend with 8+ endpoints

---

## 🚀 Quick Start

### Option 1: Use the Live Demo (Recommended)

Visit the deployed application at: [Demo URL will appear here after Vercel deployment]

### Option 2: Run Locally

**Backend:**
```bash
# 1. Clone and setup
git clone <repo-url>
cd stock-research-assistant-v0/backend

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp ../.env.example .env
# Edit .env and add your API keys (OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY)

# 5. Start the API server
uvicorn api:app --reload --port 8000
# Visit http://localhost:8000/docs for API documentation
```

**Frontend:**
```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Configure environment
cp .env.example .env.local
# Edit .env.local and set NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# 4. Start development server
npm run dev
# Visit http://localhost:3000
```

---

## 📋 How It Works

1. **AI Agent Reasoning** - Breaks down complex questions into actionable steps
2. **Live Stock Data** - Fetches real-time prices using Yahoo Finance API
3. **SEC Filings Search** - Retrieves relevant context from vector database (Qdrant)
4. **RAG Analysis** - Combines retrieved documents with GPT-4 for accurate answers
5. **Multi-Step Execution** - Orchestrates multiple tool calls to answer complex queries

### Example: "What is Tesla's stock price and summarize their risk factors?"

1. Agent calls `get_stock_price("TSLA")` → $395.23
2. Agent calls `search_sec_filings("Tesla risk factors")` → Retrieves relevant chunks
3. GPT-4 synthesizes both results into comprehensive answer

---

## 🎯 Example Queries

Try asking the AI agent:

```
"What is Apple's current stock price?"
"What is Tesla's revenue from their latest SEC filing?"
"Compare Microsoft and Apple's market cap"
"What are the main risk factors for NVDA?"
"Tell me about Amazon's business segments and current stock price"
```

The agent intelligently decides which tools to use and combines multiple data sources to answer your question.

---

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Next.js   │─────▶│   FastAPI    │─────▶│   OpenAI    │
│   Frontend  │      │   Backend    │      │   GPT-4     │
│  (Vercel)   │      │  (Render)    │      └─────────────┘
└─────────────┘      └──────────────┘              │
                            │                      │
                            ▼                      ▼
                     ┌──────────────┐      ┌─────────────┐
                     │ Yahoo Finance│      │   Qdrant    │
                     │  (Live Data) │      │  (Vectors)  │
                     └──────────────┘      └─────────────┘
```

### Tech Stack

**Frontend:**
- Next.js 16 (React framework)
- TypeScript
- Tailwind CSS
- Vercel AI SDK

**Backend:**
- FastAPI (Python web framework)
- LangChain (AI agent orchestration)
- yfinance (Stock data)
- Qdrant (Vector database)

**AI/ML:**
- OpenAI GPT-4 Turbo (LLM)
- OpenAI text-embedding-3-small (Embeddings)

**Deployment:**
- Frontend: Vercel
- Backend: Render
- Database: Qdrant Cloud

---

## 📊 API Endpoints

The FastAPI backend provides the following endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/stock/{ticker}` | GET | Get live stock price |
| `/search` | POST | Search SEC filings |
| `/qa` | POST | Ask questions about filings |
| `/agent/query` | POST | AI agent with multi-step reasoning |
| `/collections` | GET | List available collections |
| `/collections/{name}` | GET | Get collection details |

**Interactive API Docs:** [https://stock-research-assistant-v0.onrender.com/docs](https://stock-research-assistant-v0.onrender.com/docs)

---

<details>
<summary><h2>📖 Additional Documentation</h2></summary>

### Backend Setup & Development
- **[docs/SETUP.md](docs/SETUP.md)** - Local installation guide
- **[docs/REQUIREMENTS.md](docs/REQUIREMENTS.md)** - Implementation details

### Data Pipeline
- **[docs/QDRANT_QUICKSTART.md](docs/QDRANT_QUICKSTART.md)** - Vector database quickstart
- **[docs/QA_IMPLEMENTATION_SUMMARY.md](docs/QA_IMPLEMENTATION_SUMMARY.md)** - RAG implementation

### Example Scripts
```bash
# Process SEC filings
python backend/examples/pipeline_demo.py

# Test vector search
python backend/examples/query_demo.py -i

# Test Q&A system
python backend/examples/qa_api_demo.py
```

</details>

---

<details>
<summary><h2>📁 Project Structure</h2></summary>

```
stock-research-assistant-v0/
├── frontend/                  # Next.js application
│   ├── app/
│   │   ├── api/chat/         # Chat API proxy
│   │   ├── page.tsx          # Main page
│   │   └── layout.tsx        # App layout
│   ├── components/
│   │   └── ChatInterface.tsx # Chat UI component
│   ├── package.json
│   └── .env.local            # Frontend config
│
├── backend/                   # FastAPI application
│   ├── src/                  # Core modules
│   │   ├── sec_parser.py    # SEC filing parser
│   │   ├── text_chunker.py  # Text chunking
│   │   ├── embeddings.py    # OpenAI embeddings
│   │   ├── vector_store.py  # Qdrant interface
│   │   ├── qa_engine.py     # Q&A RAG engine
│   │   ├── agent.py         # LangChain AI agent
│   │   └── prompts.py       # LLM prompts
│   ├── examples/             # Demo scripts
│   │   ├── pipeline_demo.py
│   │   ├── query_demo.py
│   │   └── qa_api_demo.py
│   ├── tests/                # Test scripts
│   ├── api.py                # FastAPI server
│   ├── requirements.txt      # Python dependencies
│   └── render.yaml           # Render deployment config
│
├── docs/                      # Documentation
├── .env.example              # Environment template
└── README.md                 # This file
```

</details>

---

<summary><h2>🔧 Configuration</h2></summary>

### Environment Variables

**Backend (.env):**
```bash
# Required
OPENAI_API_KEY=sk-...
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-api-key

# Optional
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=1000
```

**Frontend (.env.local):**
```bash
# Backend API URL
NEXT_PUBLIC_BACKEND_URL=https://stock-research-assistant-v0.onrender.com
# For local development: http://localhost:8000
```

### Deployment Configuration

Both frontend and backend are configured for automatic deployment:
- **Frontend**: Vercel auto-deploys on push to `main` branch
- **Backend**: Render auto-deploys on push to `main` branch


---

<details>
<summary><h2>🎯 Use Cases</h2></summary>

Perfect for:
- **Individual Investors:** Quick research before making investment decisions
- **Financial Analysts:** Rapid insights combining live data and historical filings
- **Students:** Learning about companies and financial analysis
- **Researchers:** Exploring SEC filing data with AI assistance
- **Developers:** Reference implementation for AI-powered financial tools

### What You Can Ask

**Live Market Data:**
```
"What is Tesla's current stock price?"
"Show me AAPL's market cap and trading volume"
"What's the 52-week range for Microsoft?"
```

**SEC Filings Analysis:**
```
"What is Apple's revenue from their 10-K?"
"Tell me about Tesla's risk factors"
"What are Amazon's main business segments?"
"Describe NVIDIA's competitive landscape"
```

**Combined Queries:**
```
"What is Tesla's stock price and summarize their key risks?"
"Compare Apple and Microsoft's market cap, then tell me about Apple's revenue"
```

</details>

---

<details>
<summary><h2>🚧 Roadmap</h2></summary>

### ✅ Completed
- [x] SEC parsing & RAG pipeline
- [x] Vector storage (Qdrant Cloud)
- [x] Live stock data integration
- [x] AI agent with multi-step reasoning
- [x] REST API (FastAPI)
- [x] Next.js frontend with chat UI
- [x] Backend deployment (Render)
- [x] Frontend deployment (Vercel)

### 🔮 Future Enhancements
- [ ] Rate limiting for API protection
- [ ] User authentication
- [ ] Multi-turn conversation history
- [ ] Automated SEC filing ingestion
- [ ] Multi-company comparative analysis
- [ ] Financial metrics extraction & visualization
- [ ] Export reports (PDF/CSV)
- [ ] Custom watchlists

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

**Version:** 1.0.0 | **Status:** Production ✅ | **Last Updated:** November 22, 2025
