# Agent Module

**Status: Phase 1 Complete ✅**

Multi-step reasoning agent for stock research with live data integration.

## Overview

This module implements an intelligent agent using LangGraph that can:
- Execute tools to gather information
- Reason through multi-step queries
- Cache results for performance
- Provide explainable reasoning paths

## Architecture

```
User Query
    ↓
┌───────────────┐
│  Agent Node   │  ← Decides what to do
└───────┬───────┘
        ↓
    [Should Continue?]
        ↓
┌───────────────┐
│  Tools Node   │  ← Executes tools
└───────┬───────┘
        ↓
    [Loop back to Agent]
        ↓
    Final Answer
```

## Files

- **`__init__.py`** - Module exports
- **`agent.py`** - Main LangGraph agent implementation
- **`tools.py`** - Tool definitions (echo + placeholders)
- **`config.py`** - Configuration and environment variables
- **`cache.py`** - Caching utilities
- **`prompts.py`** - System prompts for the agent

## Phase 1: Infrastructure (Current)

### Completed ✅
- [x] LangGraph state machine
- [x] Tool execution framework
- [x] Echo tool (for testing)
- [x] In-memory caching
- [x] Configuration management
- [x] Demo script

### Available Tools
- **`echo_tool`** - Simple echo for testing

## Phase 2: Live Data Tools (Next)

### Planned
- [ ] `get_stock_price(ticker)` - Yahoo Finance integration
- [ ] `compare_financials(ticker1, ticker2)` - Compare companies
- [ ] `search_sec_filings(query, ticker)` - Wrap existing RAG system

## Usage

### Basic Example

```python
from src.agent import StockResearchAgent

# Initialize agent
agent = StockResearchAgent(use_all_tools=False)  # Phase 1: echo only

# Query
result = agent.query("Echo: Hello, Agent!")

print(result["answer"])
print(f"Execution time: {result['execution_time_ms']}ms")
print(f"Tools used: {result['tools_used']}")
```

### Run Demo

```bash
python examples/agent_demo.py
```

### Configuration

Environment variables (see `.env.example`):

```bash
# Agent behavior
AGENT_MAX_ITERATIONS=10       # Max reasoning steps
AGENT_ENABLE_CACHE=true       # Enable caching
AGENT_CACHE_TTL=300           # Cache TTL in seconds

# API settings
YFINANCE_TIMEOUT=10           # API timeout
AGENT_MAX_RETRIES=3           # Retry failed calls

# Debugging
AGENT_VERBOSE=false           # Verbose logging
AGENT_LOG_STEPS=true          # Log reasoning steps
```

## Cache Behavior

The agent uses a two-tier caching strategy:

1. **LLM Response Cache** (Phase 1) ✅
   - Caches identical queries
   - Default TTL: 5 minutes
   - In-memory storage

2. **HTTP Response Cache** (Phase 2)
   - Will cache API responses (yfinance, etc.)
   - Uses `requests-cache`

### Cache Stats

```python
stats = agent.get_cache_stats()
print(f"Hit rate: {stats['hit_rate_percent']}%")
```

## Testing

```bash
# Run agent tests
pytest tests/test_agent*.py -v

# Test with demo script
python examples/agent_demo.py
```

## Next Steps (Phase 2)

1. **Implement `get_stock_price()`**
   - Use `yfinance` library
   - Return price, volume, market cap
   - Add error handling for invalid tickers

2. **Implement `compare_financials()`**
   - Sub-agent that aggregates data
   - Combine live data + SEC filings
   - Generate structured comparison

3. **Wrap existing RAG system**
   - Expose `qa_engine.py` as a tool
   - Enable agent to query SEC filings

4. **Add HTTP caching**
   - Use `requests-cache` for API calls
   - Reduce API load by 80%+

## API (FastAPI Integration)

Coming in Phase 5:

```python
POST /agent/query
{
  "query": "What's AAPL's stock price?",
  "use_cache": true
}
```

## Performance

**Phase 1 Metrics:**
- Echo query: ~500-1000ms
- Cache hit: ~5-10ms (99% faster)
- Memory usage: ~50MB base + cache

**Phase 2 Target:**
- Stock price query: <2 seconds
- Complex comparison: <5 seconds
- Cache hit rate: >80%

## Dependencies

```toml
langchain >= 0.1.0
langgraph >= 0.0.20        # State management
yfinance >= 0.2.36         # Stock data (Phase 2)
requests-cache >= 1.1.1    # HTTP caching (Phase 2)
```

## Troubleshooting

**"OPENAI_API_KEY not found"**
- Copy `.env.example` to `.env`
- Add your OpenAI API key

**"Tool not found"**
- Check if using `use_all_tools=True`
- Some tools are placeholders in Phase 1

**Cache not working**
- Verify `AGENT_ENABLE_CACHE=true`
- Check cache stats with `agent.get_cache_stats()`

## Contributing

When adding new tools:

1. Define tool in `tools.py` with `@tool` decorator
2. Add to appropriate tool list (`get_phase1_tools()`, etc.)
3. Update prompts in `prompts.py` if needed
4. Write tests in `tests/test_agent_tools.py`
5. Update this README

## License

Same as parent project.
