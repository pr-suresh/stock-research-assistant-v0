# Render Deployment Checklist

Use this checklist to ensure successful deployment.

## Pre-Deployment

- [ ] GitHub repository is up to date with all backend changes
- [ ] You have your OpenAI API key ready
- [ ] You have your Qdrant Cloud URL and API key ready
- [ ] You've tested the backend locally (`cd backend && uvicorn api:app`)

## Render Setup

- [ ] Created Render account at https://render.com
- [ ] Connected GitHub account to Render
- [ ] Clicked "New +" → "Web Service"
- [ ] Selected `stock-research-assistant-v0` repository

## Service Configuration

- [ ] Set **Root Directory** to: `backend`
- [ ] Set **Build Command** to: `pip install -r requirements.txt`
- [ ] Set **Start Command** to: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- [ ] Selected **Free** instance type

## Environment Variables

- [ ] Added `OPENAI_API_KEY` = `sk-proj-...`
- [ ] Added `QDRANT_URL` = `https://...cloud.qdrant.io`
- [ ] Added `QDRANT_API_KEY` = `eyJhbGci...`
- [ ] (Optional) Added `OPENAI_MODEL` = `gpt-4-turbo-preview`
- [ ] (Optional) Added `OPENAI_TEMPERATURE` = `0.1`
- [ ] (Optional) Added `OPENAI_MAX_TOKENS` = `1000`

## Deployment

- [ ] Clicked "Create Web Service"
- [ ] Build started successfully
- [ ] Build completed without errors
- [ ] Service shows "Live" status (green)

## Testing

- [ ] Copied deployment URL: `https://__________________.onrender.com`
- [ ] Health check works: `curl https://your-url.onrender.com/`
- [ ] Swagger UI accessible: `https://your-url.onrender.com/docs`
- [ ] Stock endpoint works: `/stock/AAPL`
- [ ] Agent endpoint works: `/agent/query`

## Post-Deployment

- [ ] Saved API URL in safe place
- [ ] Updated `backend/DEPLOY.md` with your URL
- [ ] Tested all 8 endpoints via Swagger UI
- [ ] Verified no errors in Render logs
- [ ] Ready for Phase 3 (Frontend development)

---

## Your Deployment Info

Fill this in after successful deployment:

**Deployment URL:** `_______________________________________________`

**Deployed Date:** `_______________`

**Render Service Name:** `_______________________________________________`

**Status:** ✅ Live | ⏳ Building | ❌ Failed

---

## Troubleshooting

If deployment fails, check:

1. **Logs tab** in Render dashboard for error messages
2. **Root directory** is set to `backend`
3. **Environment variables** are all added
4. **Build command** and **start command** are correct
5. Local backend works: `cd backend && uvicorn api:app`

## Next Phase

Once all checkboxes are ✅, you're ready for:

**Phase 3: Frontend Development** (Next.js + Vercel AI SDK)
