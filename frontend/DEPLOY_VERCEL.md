# Deploy Frontend to Vercel

## Quick Deploy Guide

### Step 1: Prepare for Deployment

Ensure your code is committed and pushed to GitHub:

```bash
git add frontend/
git commit -m "Add Next.js frontend with chat interface"
git push origin main
```

### Step 2: Deploy to Vercel

1. Go to https://vercel.com
2. Sign up/login with your GitHub account
3. Click **"Add New Project"**
4. Select your repository: `stock-research-assistant-v0`

### Step 3: Configure Project

**Framework Preset:** Next.js (auto-detected)

**Root Directory:** `frontend`

**Build Settings (auto-detected):**
- Build Command: `npm run build`
- Output Directory: `.next`
- Install Command: `npm install`

### Step 4: Environment Variables

⚠️ **CRITICAL:** Add this environment variable:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_BACKEND_URL` | `https://stock-research-assistant-v0.onrender.com` |

**How to add:**
1. Click "Environment Variables" section
2. Add key: `NEXT_PUBLIC_BACKEND_URL`
3. Add value: Your deployed backend URL
4. Click "Add"

### Step 5: Deploy!

1. Click **"Deploy"** button
2. Wait 2-3 minutes for build and deployment
3. Vercel will provide your URL:
   ```
   https://your-project.vercel.app
   ```

### Step 6: Test Deployed App

Visit your Vercel URL and test:
1. Chat interface loads
2. Example queries work
3. Agent responds with stock data
4. Tool calls display correctly

---

## Vercel Configuration File (Optional)

If you want to commit Vercel config, create `vercel.json` in root:

```json
{
  "buildCommand": "cd frontend && npm run build",
  "devCommand": "cd frontend && npm run dev",
  "installCommand": "cd frontend && npm install",
  "framework": "nextjs",
  "outputDirectory": "frontend/.next"
}
```

---

## Environment Variables

### Development (.env.local)
```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### Production (Vercel Dashboard)
```bash
NEXT_PUBLIC_BACKEND_URL=https://stock-research-assistant-v0.onrender.com
```

---

## Troubleshooting

### Build Fails

**Error:** Cannot find module '@/components/ChatInterface'

**Fix:** Ensure `tsconfig.json` has:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

### API Calls Fail

**Error:** Network request failed or CORS error

**Fix:**
1. Check `NEXT_PUBLIC_BACKEND_URL` is set correctly in Vercel
2. Ensure backend CORS is enabled (already done in backend/api.py)
3. Verify backend is running: visit backend URL `/docs`

### Page Not Found

**Fix:** Set Root Directory to `frontend` in Vercel project settings

---

## After Successful Deployment

✅ Save your frontend URL
✅ Test all features
✅ Update README.md with demo links
✅ Share with users!

**Your Vercel URL:** `___________________________________________`

---

## Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS (Vercel provides instructions)
4. SSL automatically configured!

---

## Monitoring & Analytics

Vercel provides:
- **Analytics:** Usage and performance metrics
- **Logs:** Runtime and build logs
- **Insights:** Web Vitals and performance

Access via: Dashboard → Your Project → Analytics/Logs

---

## Redeploy

Vercel auto-deploys on every push to `main` branch.

**Manual redeploy:**
1. Dashboard → Your Project
2. Deployments tab
3. Click "..." on latest deployment
4. Select "Redeploy"

---

## Cost

**Free Tier Includes:**
- Unlimited deployments
- 100GB bandwidth/month
- Automatic SSL
- Auto-scaling
- CDN globally

**Perfect for this demo!** 🎉
