# Quick Deploy Reference - Render

## Essential Settings

### Service Configuration
```
Name: stock-research-api
Runtime: Python 3
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn api:app --host 0.0.0.0 --port $PORT
Plan: Free
```

### Environment Variables (REQUIRED)
```bash
OPENAI_API_KEY=sk-proj-your-key-here
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-key-here
```

### Optional Environment Variables
```bash
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=1000
```

## Quick Test Commands

After deployment, test with:

```bash
# Replace YOUR_URL with your actual Render URL
export API_URL=https://stock-research-api.onrender.com

# Test 1: Health check
curl $API_URL/

# Test 2: Stock price
curl $API_URL/stock/AAPL

# Test 3: Agent query
curl -X POST $API_URL/agent/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Tesla stock price?"}'
```

## Deployment URL

After deployment, save your URL here:

**API URL:** `_______________________________________`

**Swagger Docs:** `${API_URL}/docs`

This URL will be used as `NEXT_PUBLIC_BACKEND_URL` in Phase 3 (Frontend).
