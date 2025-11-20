# Render Deployment Guide - Stock Research Assistant Backend

## Prerequisites

Before starting, ensure you have:
- ✅ GitHub account with this repository pushed
- ✅ OpenAI API key (get from https://platform.openai.com/api-keys)
- ✅ Qdrant Cloud credentials (URL and API key from https://cloud.qdrant.io)

---

## Step-by-Step Deployment Instructions

### Step 1: Create Render Account

1. Go to https://render.com
2. Click **"Get Started"** or **"Sign Up"**
3. Sign up with your GitHub account (recommended for easy repo connection)
4. Verify your email if required

---

### Step 2: Connect GitHub Repository

1. In Render dashboard, click **"New +"** button in top right
2. Select **"Web Service"**
3. Click **"Connect GitHub"** (if not already connected)
4. Authorize Render to access your GitHub repositories
5. Find and select: `stock-research-assistant-v0`

---

### Step 3: Configure Web Service

Fill in the following settings:

**Basic Settings:**
- **Name:** `stock-research-api` (or your preferred name)
- **Region:** Choose closest to your users (e.g., Oregon, Frankfurt)
- **Branch:** `main` (or your default branch)
- **Root Directory:** `backend` ⚠️ IMPORTANT!

**Build Settings:**
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn api:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- Select **"Free"** (for demo/testing)
  - Note: Free tier has cold starts (~30s after 15min inactivity)
  - Upgrade to $7/month for no cold starts if needed

---

### Step 4: Set Environment Variables

⚠️ **CRITICAL STEP** - Click **"Advanced"** to expand environment variables section.

Add the following environment variables:

| Key | Value | Notes |
|-----|-------|-------|
| `OPENAI_API_KEY` | `sk-proj-...` | Your OpenAI API key |
| `QDRANT_URL` | `https://xxx.cloud.qdrant.io` | From Qdrant Cloud dashboard |
| `QDRANT_API_KEY` | `eyJhbGci...` | From Qdrant Cloud dashboard |
| `OPENAI_MODEL` | `gpt-4-turbo-preview` | Optional (has default) |
| `OPENAI_TEMPERATURE` | `0.1` | Optional (has default) |
| `OPENAI_MAX_TOKENS` | `1000` | Optional (has default) |

**How to add each variable:**
1. Click **"Add Environment Variable"**
2. Enter **Key** and **Value**
3. Repeat for all variables above

**Security Note:** Never commit these values to Git! Render encrypts them.

---

### Step 5: Deploy!

1. Review all settings carefully
2. Click **"Create Web Service"** button at the bottom
3. Render will start building and deploying your backend

**Build Process (takes ~3-5 minutes):**
```
==> Cloning from GitHub
==> Installing dependencies (pip install -r requirements.txt)
==> Starting service (uvicorn api:app...)
==> Deploy successful! 🎉
```

---

### Step 6: Get Your API URL

Once deployed, Render provides a URL:

**Free Tier Format:**
```
https://stock-research-api.onrender.com
```

**Custom Domain (optional, paid plans):**
```
https://api.yourcompany.com
```

**Copy this URL** - you'll need it for:
- Testing endpoints
- Configuring the frontend in Phase 3

---

### Step 7: Test Deployed API

#### Test 1: Health Check
```bash
curl https://stock-research-api.onrender.com/
```

Expected response:
```json
{
  "status": "healthy",
  "message": "RAG Pipeline API with Q&A, Live Stock Data, and AI Agent",
  "endpoints": { ... }
}
```

#### Test 2: API Documentation
Visit in browser:
```
https://stock-research-api.onrender.com/docs
```

You should see the **Swagger UI** with all endpoints documented.

#### Test 3: Stock Price Endpoint
```bash
curl https://stock-research-api.onrender.com/stock/AAPL
```

Expected: Current Apple stock price data

#### Test 4: Agent Endpoint
```bash
curl -X POST https://stock-research-api.onrender.com/agent/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Apple stock price?", "max_iterations": 5}'
```

Expected: AI agent response with tool calls

---

## Troubleshooting

### Issue 1: Build Fails - "No module named..."

**Cause:** Missing dependency in requirements.txt

**Fix:**
1. On your local machine: `cd backend && pip freeze > requirements.txt`
2. Commit and push changes
3. Render will auto-redeploy

---

### Issue 2: App Crashes - "OpenAI API key not configured"

**Cause:** Missing environment variable

**Fix:**
1. Go to Render dashboard → Your service
2. Click **"Environment"** tab
3. Add missing `OPENAI_API_KEY` variable
4. Save changes (auto-redeploys)

---

### Issue 3: "Qdrant connection failed"

**Cause:** Incorrect Qdrant credentials or URL

**Fix:**
1. Verify Qdrant Cloud cluster is active
2. Check URL format: `https://xxx-xxx-xxx.cloud.qdrant.io` (no trailing slash)
3. Verify API key is correct
4. Update environment variables in Render

---

### Issue 4: Slow Cold Starts (30+ seconds)

**This is expected on Render free tier!**

**Solutions:**
- **Option A:** Accept it for demo (first request after 15min idle is slow)
- **Option B:** Upgrade to $7/month plan (no cold starts)
- **Option C:** Use Railway instead (better free tier performance)

---

### Issue 5: Build Succeeds but App Crashes on Start

**Check Render logs:**
1. Go to your service dashboard
2. Click **"Logs"** tab
3. Look for error messages

**Common causes:**
- Incorrect start command (should be: `uvicorn api:app --host 0.0.0.0 --port $PORT`)
- Port binding issue (ensure using `$PORT` variable, not hardcoded 8000)
- Missing `backend/` root directory setting

---

## Monitoring & Maintenance

### View Logs
```
Dashboard → Your Service → Logs tab
```

Filter by:
- **Build logs** - Installation and build process
- **Deploy logs** - Startup and runtime

### Redeploy
Render auto-deploys when you push to GitHub.

**Manual redeploy:**
1. Dashboard → Your Service
2. Click **"Manual Deploy"** button
3. Select **"Deploy latest commit"**

### Check Status
```
Dashboard → Your Service
```

**Status indicators:**
- 🟢 **Live** - Service is running
- 🟡 **Building** - Currently deploying
- 🔴 **Failed** - Deployment failed (check logs)

---

## Next Steps After Successful Deployment

✅ Save your deployed API URL (e.g., `https://stock-research-api.onrender.com`)

This URL will be used in:
- **Phase 3:** Frontend configuration (`NEXT_PUBLIC_BACKEND_URL`)
- **Testing:** All API requests from the frontend
- **Documentation:** README demo links

---

## Cost Breakdown

### Free Tier (Current Setup):
- ✅ **Backend hosting:** FREE (750 hours/month)
- ⚠️ **Cold starts:** ~30s delay after 15min idle
- ✅ **SSL/HTTPS:** Included
- ✅ **Auto-deploy:** Included

### Paid Upgrade ($7/month):
- ✅ No cold starts
- ✅ Faster builds
- ✅ Priority support
- ✅ Custom domains

### External Services:
- **OpenAI API:** ~$5-20/month (pay-as-you-go, depends on usage)
- **Qdrant Cloud:** FREE tier (1GB storage)
- **Yahoo Finance:** FREE (no API key needed)

**Total for demo:** ~$5-20/month (just OpenAI API usage)

---

## Alternative: Railway Deployment

If you prefer Railway over Render:

1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select `stock-research-assistant-v0`
5. Set root directory: `backend`
6. Add same environment variables
7. Railway auto-detects Python and uses your start command

**Railway Benefits:**
- Faster cold starts (~5s)
- $5 free credit/month
- Modern UI

---

## Security Best Practices

✅ **DO:**
- Use environment variables for secrets
- Enable HTTPS (Render provides by default)
- Regularly rotate API keys
- Monitor usage and costs

❌ **DON'T:**
- Commit API keys to Git
- Share your Render dashboard access
- Use weak OpenAI API key restrictions

---

## Support

**Render Documentation:** https://render.com/docs
**Render Community:** https://community.render.com
**This Project Issues:** https://github.com/your-username/stock-research-assistant-v0/issues

---

## Summary Checklist

Before moving to Phase 3 (Frontend), ensure:

- ✅ Render account created
- ✅ GitHub repo connected
- ✅ Web service configured with `backend/` root directory
- ✅ All environment variables added (OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY)
- ✅ Deployment successful (green status)
- ✅ Health check endpoint works
- ✅ Swagger UI accessible at `/docs`
- ✅ Stock price endpoint tested
- ✅ Agent endpoint tested
- ✅ API URL saved for frontend configuration

**Your Deployed API URL:** `___________________________`

Save this URL! You'll need it in Phase 3.
