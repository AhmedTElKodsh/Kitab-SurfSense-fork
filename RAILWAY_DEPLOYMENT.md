# Kitab - Railway Deployment Guide

## Prerequisites

- GitHub account with access to this repository
- Railway account (https://railway.app)
- Vercel account (https://vercel.com)
- Supabase account (https://supabase.com)
- Upstash Redis (already configured)

## Deployment Overview

- **Backend**: Railway Web Service (FastAPI)
- **Frontend**: Vercel (Next.js)
- **Database**: Supabase (PostgreSQL + pgvector)
- **Redis**: Upstash (already configured)
- **Worker**: Railway Background Worker (Celery)

---

## Step 1: Deploy Backend to Railway

### 1.1 Create Railway Project

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select `AhmedTElKodsh/Kitab-SurfSense-fork`
4. Select branch: `kitab-poc-deployment`

### 1.2 Configure Service

**Service Settings:**

- **Root Directory**: `surfsense_backend`
- **Build Command**: `pip install .`
- **Start Command**: `uvicorn app.app:app --host 0.0.0.0 --port $PORT`

### 1.3 Environment Variables (Phase 1 - Temporary CORS)

Add these environment variables in Railway dashboard (Variables tab):

```bash
# CORS (temporary - will update after Vercel deployment)
CORS_ORIGINS=*

# Python
PYTHONPATH=/app

# Redis (Upstash - already configured)
UPSTASH_REDIS_REST_URL=https://loyal-katydid-37671.upstash.io
UPSTASH_REDIS_REST_TOKEN=AZMnAAIncDI1M2ZiYThmNzJjOTk0NWI5YjJlZWNmOTk1MGVmMjM0MnAyMzc2NzE
REDIS_URL=https://loyal-katydid-37671.upstash.io
CELERY_BROKER_URL=https://loyal-katydid-37671.upstash.io
CELERY_RESULT_BACKEND=https://loyal-katydid-37671.upstash.io

# Auth
AUTH_TYPE=LOCAL
REGISTRATION_ENABLED=true

# ETL Service
ETL_SERVICE=DOCLING

# Database (will add Supabase URL later in Step 4)
# DATABASE_URL=postgresql://...

# LLM API Keys (add your keys)
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_API_KEY=...
```

### 1.4 Deploy and Get URL

1. Railway will automatically start deploying
2. Wait for deployment to complete (5-10 minutes)
3. Go to Settings tab → Generate Domain (if not auto-generated)
4. Copy the Railway URL (e.g., `https://kitab-backend-production.up.railway.app`)
5. Test health endpoint:
   ```bash
   curl https://your-railway-url.railway.app/api/v1/health
   ```
   Expected: `{"status": "healthy", "service": "kitab-backend"}`

---

## Step 2: Deploy Frontend to Vercel

### 2.1 Import Project

1. Go to https://vercel.com/new
2. Import `AhmedTElKodsh/Kitab-SurfSense-fork`
3. Select branch: `kitab-poc-deployment`

### 2.2 Configure Project

**Framework Preset**: Next.js (auto-detected)

**Root Directory**: `surfsense_web`

**Build Settings**: (leave defaults)

- Build Command: `npm run build`
- Output Directory: `.next`
- Install Command: `npm install`

### 2.3 Environment Variables

Add these in Vercel dashboard:

```bash
# Backend URL (from Railway Step 1.4)
NEXT_PUBLIC_FASTAPI_BACKEND_URL=https://your-railway-url.railway.app

# Auth
NEXT_PUBLIC_FASTAPI_BACKEND_AUTH_TYPE=LOCAL

# ETL
NEXT_PUBLIC_ETL_SERVICE=DOCLING

# NextAuth (generate secret with: openssl rand -base64 32)
NEXTAUTH_SECRET=your-generated-secret-here
NEXTAUTH_URL=https://your-vercel-url.vercel.app

# App
NODE_ENV=production
NEXT_PUBLIC_APP_NAME=Kitab
```

### 2.4 Deploy

1. Click "Deploy"
2. Wait for deployment (3-5 minutes)
3. Copy Vercel URL (e.g., `https://kitab.vercel.app`)
4. Test: Visit URL in browser

---

## Step 3: Update Railway CORS

### 3.1 Update Environment Variable

1. Go to Railway dashboard → Your backend service
2. Go to "Variables" tab
3. Find `CORS_ORIGINS` variable
4. Update value to:
   ```
   https://your-app.vercel.app,https://*.vercel.app,http://localhost:3000
   ```
5. Railway will automatically redeploy

### 3.2 Verify

1. Wait for redeployment to complete
2. Test CORS: Open browser console on Vercel URL, check for CORS errors (should be none)

---

## Step 4: Configure Supabase Database

### 4.1 Create Project

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Settings:
   - **Name**: kitab-production
   - **Database Password**: (generate strong password - save it!)
   - **Region**: Choose closest to your users
4. Click "Create new project"
5. Wait for project creation (2-3 minutes)

### 4.2 Enable pgvector Extension

1. Go to Database → Extensions
2. Search for "vector"
3. Click "Enable" on `vector` extension

### 4.3 Get Connection String

1. Go to Settings → Database
2. Find "Connection string" section
3. Select "URI" tab
4. Copy the connection string
5. Replace `[YOUR-PASSWORD]` with your actual password

Example:

```
postgresql://postgres.abc123:YOUR_PASSWORD@aws-0-us-west-1.pooler.supabase.com:5432/postgres
```

### 4.4 Run Migrations (Local Machine)

**IMPORTANT**: Run from your local machine, NOT from Railway.

```bash
# Navigate to backend directory
cd surfsense_backend

# Set database URL
export DATABASE_URL="postgresql://postgres.abc123:YOUR_PASSWORD@aws-0-us-west-1.pooler.supabase.com:5432/postgres"

# Run migrations
alembic upgrade head
```

### 4.5 Verify Tables

1. Go to Supabase Dashboard → Table Editor
2. Verify tables exist:
   - users
   - search_spaces
   - documents
   - chats
   - podcasts
   - etc.

### 4.6 Configure Storage

1. Go to Storage → "Create a new bucket"
2. Settings:
   - **Name**: documents
   - **Public**: false (unchecked)
3. Click "Create bucket"

### 4.7 Update Railway with Database URL

1. Go to Railway dashboard → Your backend service
2. Go to "Variables" tab
3. Add new environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: Your Supabase connection string
4. Railway will automatically redeploy

---

## Step 5: Deploy Celery Worker to Railway

### 5.1 Create New Service

1. In Railway project, click "New"
2. Select "GitHub Repo"
3. Select same repository: `AhmedTElKodsh/Kitab-SurfSense-fork`
4. Select branch: `kitab-poc-deployment`

### 5.2 Configure Worker Service

**Service Settings:**

- **Name**: `kitab-celery-worker`
- **Root Directory**: `surfsense_backend`
- **Build Command**: `pip install .`
- **Start Command**: `celery -A app.celery_app worker --loglevel=info --concurrency=2 --pool=solo`

### 5.3 Environment Variables

**IMPORTANT**: Copy ALL environment variables from the backend service.

Go to backend service → Variables tab → Copy all variables, then paste into worker service.

Required variables:

- All Redis/Upstash variables
- DATABASE_URL
- PYTHONPATH
- AUTH_TYPE
- ETL_SERVICE
- All API keys

### 5.4 Deploy Worker

1. Railway will automatically deploy
2. Monitor logs to verify worker starts successfully
3. Look for: `celery@[hostname] ready`

---

## Step 6: Verification & Testing

### 6.1 Backend Health

```bash
curl https://your-railway-url.railway.app/api/v1/health
```

Expected: `{"status": "healthy", "service": "kitab-backend"}`

### 6.2 Frontend Access

1. Visit Vercel URL
2. Check browser console (F12) - should be no errors
3. Verify "Kitab" branding appears

### 6.3 User Registration

1. Click "Register"
2. Create test account
3. Verify user appears in Supabase → Authentication → Users

### 6.4 Document Upload (Tests Celery)

1. Login to dashboard
2. Upload a small PDF
3. Check Celery worker logs in Railway
4. Verify document appears in documents list

### 6.5 Chat Test

1. Navigate to Researcher/Chat
2. Send message: "Who are you?"
3. Verify response says "I am Kitab"

---

## Complete Environment Variables Reference

### Railway Backend Service

```bash
# CORS
CORS_ORIGINS=https://your-app.vercel.app,https://*.vercel.app,http://localhost:3000

# Python
PYTHONPATH=/app

# Database
DATABASE_URL=postgresql://postgres.abc123:PASSWORD@aws-0-us-west-1.pooler.supabase.com:5432/postgres

# Redis (Upstash)
UPSTASH_REDIS_REST_URL=https://loyal-katydid-37671.upstash.io
UPSTASH_REDIS_REST_TOKEN=AZMnAAIncDI1M2ZiYThmNzJjOTk0NWI5YjJlZWNmOTk1MGVmMjM0MnAyMzc2NzE
REDIS_URL=https://loyal-katydid-37671.upstash.io
CELERY_BROKER_URL=https://loyal-katydid-37671.upstash.io
CELERY_RESULT_BACKEND=https://loyal-katydid-37671.upstash.io

# Auth
AUTH_TYPE=LOCAL
SECRET=generate-random-secret-key
REGISTRATION_ENABLED=true
BACKEND_URL=https://your-railway-url.railway.app

# ETL
ETL_SERVICE=DOCLING

# LLM API Keys (add your actual keys)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
GROQ_API_KEY=...

# Optional: LangSmith
LANGCHAIN_TRACING_V2=false
```

### Vercel Frontend

```bash
# Backend
NEXT_PUBLIC_FASTAPI_BACKEND_URL=https://your-railway-url.railway.app

# Auth
NEXT_PUBLIC_FASTAPI_BACKEND_AUTH_TYPE=LOCAL
NEXTAUTH_SECRET=generate-with-openssl-rand-base64-32
NEXTAUTH_URL=https://your-vercel-url.vercel.app

# ETL
NEXT_PUBLIC_ETL_SERVICE=DOCLING

# App
NODE_ENV=production
NEXT_PUBLIC_APP_NAME=Kitab
```

---

## Troubleshooting

### Railway Service Won't Start

- Check logs in Railway dashboard
- Verify `PYTHONPATH=/app` is set correctly
- Ensure `runtime.txt` contains `python-3.12`

### Frontend Can't Connect to Backend

- Verify `NEXT_PUBLIC_FASTAPI_BACKEND_URL` is correct
- Check CORS configuration in Railway
- Look for CORS errors in browser console

### Database Connection Fails

- Verify Supabase connection string is correct
- Check password is properly URL-encoded
- Ensure pgvector extension is enabled

### Celery Worker Not Processing

- Check worker logs in Railway
- Verify Redis URL is correct
- Ensure all env vars copied from backend service

### CORS Errors

- Verify `CORS_ORIGINS` includes your Vercel URL
- Check for typos in domain names
- Ensure Railway redeployed after CORS update

---

## Deployment Checklist

- [ ] Backend deployed to Railway
- [ ] Backend health endpoint working
- [ ] Frontend deployed to Vercel
- [ ] Frontend loads without errors
- [ ] CORS updated with Vercel URL
- [ ] Supabase project created
- [ ] pgvector extension enabled
- [ ] Migrations run successfully
- [ ] Storage bucket created
- [ ] Database URL added to Railway
- [ ] Celery worker deployed
- [ ] Worker shows "ready" in logs
- [ ] User registration works
- [ ] Document upload works
- [ ] Chat functionality works
- [ ] All branding shows "Kitab"

---

## Next Steps

1. Follow TEST_CHECKLIST.md for comprehensive testing
2. Set up custom domain (optional)
3. Configure monitoring
4. Set up database backups
5. Document any deployment-specific issues

---

## Support Resources

- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- Supabase Docs: https://supabase.com/docs
- Upstash Docs: https://docs.upstash.com/redis
