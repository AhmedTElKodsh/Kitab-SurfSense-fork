# Kitab Platform - Deployment Guide

This guide walks through deploying the Kitab platform to production using Railway (backend), Vercel (frontend), and Supabase (database).

## Prerequisites

- GitHub account with access to this repository
- Railway account (https://railway.app)
- Vercel account (https://vercel.com)
- Supabase account (https://supabase.com)
- Upstash account for Redis (https://upstash.com) - optional, can use Railway Redis

## Deployment Sequence

**IMPORTANT**: Follow this exact order to resolve circular dependencies:

1. Deploy Railway Backend (with temporary CORS: `*`)
2. Deploy Vercel Frontend (using Railway URL)
3. Update Railway CORS (with actual Vercel URL)
4. Configure Supabase and run migrations
5. Set up Redis for Celery
6. Deploy Celery Worker

---

## Step 1: Railway Backend Deployment (Initial)

### 1.1 Create Railway Project

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select `AhmedTElKodsh/Kitab-SurfSense-fork`
4. Select branch: `kitab-poc-deployment`

### 1.2 Configure Service

1. **Root Directory**: `surfsense_backend`
2. **Build Command**: `pip install .`
3. **Start Command**: `uvicorn app.app:app --host 0.0.0.0 --port $PORT`

### 1.3 Environment Variables (Phase 1 - Temporary CORS)

Add these environment variables in Railway dashboard:

```bash
# Temporary CORS (will update after Vercel deployment)
CORS_ORIGINS=*

# Python
PYTHONPATH=/app

# Database (will add Supabase URL later)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis (will add later)
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379

# Auth
AUTH_TYPE=LOCAL
SECRET=your-secret-key-here
REGISTRATION_ENABLED=true

# LLM API Keys (add your keys)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# ETL Service
ETL_SERVICE=DOCLING
```

### 1.4 Deploy and Get URL

1. Click "Deploy"
2. Wait for deployment to complete
3. Copy the Railway URL (e.g., `https://kitab-backend-production.up.railway.app`)
4. Test health endpoint: `curl https://your-railway-url/api/v1/health`

---

## Step 2: Vercel Frontend Deployment

### 2.1 Import Project

1. Go to https://vercel.com/new
2. Import `AhmedTElKodsh/Kitab-SurfSense-fork`
3. Select branch: `kitab-poc-deployment`

### 2.2 Configure Project

1. **Root Directory**: `surfsense_web`
2. **Framework Preset**: Next.js
3. **Build Command**: (leave default) `npm run build`
4. **Output Directory**: (leave default) `.next`

### 2.3 Environment Variables

Add these in Vercel dashboard:

```bash
# Backend URL (from Railway Step 1.4)
NEXT_PUBLIC_FASTAPI_BACKEND_URL=https://your-railway-url.railway.app

# Auth
NEXT_PUBLIC_FASTAPI_BACKEND_AUTH_TYPE=LOCAL

# ETL
NEXT_PUBLIC_ETL_SERVICE=DOCLING

# NextAuth
NEXTAUTH_SECRET=generate-with-openssl-rand-base64-32
NEXTAUTH_URL=https://your-vercel-url.vercel.app

# App
NODE_ENV=production
NEXT_PUBLIC_APP_NAME=Kitab
```

### 2.4 Deploy and Get URL

1. Click "Deploy"
2. Wait for deployment to complete
3. Copy the Vercel URL (e.g., `https://kitab.vercel.app`)
4. Test: Visit the URL in browser

---

## Step 3: Update Railway CORS (Finalize)

### 3.1 Update Environment Variable

1. Go back to Railway dashboard
2. Find your backend service
3. Update `CORS_ORIGINS` environment variable:

```bash
CORS_ORIGINS=https://your-app.vercel.app,https://*.vercel.app,http://localhost:3000
```

### 3.2 Redeploy

1. Railway will automatically redeploy
2. Wait for deployment to complete
3. Test CORS: Open browser console on Vercel URL, check for CORS errors

---

## Step 4: Supabase Database Setup

### 4.1 Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Choose organization and region
4. Set database password (save it!)
5. Wait for project to be created

### 4.2 Enable pgvector Extension

1. Go to Database → Extensions
2. Search for "vector"
3. Enable the extension

### 4.3 Get Connection String

1. Go to Settings → Database
2. Copy "Connection string" (URI format)
3. Replace `[YOUR-PASSWORD]` with your actual password

### 4.4 Run Migrations from Local Machine

**IMPORTANT**: Run migrations from your local machine, NOT from Railway.

```bash
cd surfsense_backend
export DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"
alembic upgrade head
```

### 4.5 Verify Tables Created

1. Go to Supabase Dashboard → Table Editor
2. Verify tables exist: `users`, `search_spaces`, `documents`, etc.

### 4.6 Configure Authentication

1. Go to Authentication → Providers
2. Email provider should be enabled by default
3. Configure email templates if needed

### 4.7 Set Up Storage

1. Go to Storage → Create bucket
2. Name: `documents`
3. Public: `false`

### 4.8 Update Railway with Supabase URL

1. Go to Railway dashboard
2. Update `DATABASE_URL` environment variable with Supabase connection string
3. Railway will automatically redeploy

---

## Step 5: Redis for Celery

### Option A: Upstash (Recommended for POC)

1. Go to https://console.upstash.com
2. Create new Redis database
3. Copy connection URL (format: `rediss://...`)
4. Add to Railway environment variables:

```bash
REDIS_URL=rediss://default:[PASSWORD]@[HOST]:[PORT]
CELERY_BROKER_URL=rediss://default:[PASSWORD]@[HOST]:[PORT]
CELERY_RESULT_BACKEND=rediss://default:[PASSWORD]@[HOST]:[PORT]
```

### Option B: Railway Redis Plugin

1. In Railway project, click "New"
2. Select "Database" → "Redis"
3. Copy connection URL from plugin
4. Add to Railway environment variables (same as above)

---

## Step 6: Celery Worker Service

### 6.1 Create New Service in Railway

1. In Railway project, click "New" → "GitHub Repo"
2. Select same repository and branch
3. Name it: `kitab-celery-worker`

### 6.2 Configure Worker Service

1. **Root Directory**: `surfsense_backend`
2. **Build Command**: `pip install .`
3. **Start Command**: `celery -A app.celery_app worker --loglevel=info --concurrency=2 --pool=solo`

### 6.3 Copy Environment Variables

Copy ALL environment variables from main backend service to worker service.

### 6.4 Deploy Worker

1. Click "Deploy"
2. Monitor logs to verify worker starts successfully
3. Look for: `celery@[hostname] ready`

---

## Verification Checklist

### Backend Health

- [ ] Railway backend URL accessible
- [ ] Health endpoint returns: `{"status": "healthy", "service": "kitab-backend"}`
- [ ] No errors in Railway logs

### Frontend Health

- [ ] Vercel URL loads successfully
- [ ] No console errors in browser
- [ ] "Kitab" branding appears correctly

### Database Connection

- [ ] Register new user account works
- [ ] User appears in Supabase dashboard
- [ ] No database connection errors in logs

### CORS Configuration

- [ ] No CORS errors in browser console
- [ ] API requests from frontend succeed

### Celery Worker

- [ ] Worker logs show "ready" status
- [ ] Upload document test triggers worker task
- [ ] Document processing completes

---

## Environment Variables Reference

### Railway Backend (Complete List)

```bash
# CORS
CORS_ORIGINS=https://your-app.vercel.app,https://*.vercel.app,http://localhost:3000

# Python
PYTHONPATH=/app

# Database
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# Redis
REDIS_URL=rediss://default:[PASSWORD]@[HOST]:[PORT]
CELERY_BROKER_URL=rediss://default:[PASSWORD]@[HOST]:[PORT]
CELERY_RESULT_BACKEND=rediss://default:[PASSWORD]@[HOST]:[PORT]

# Auth
AUTH_TYPE=LOCAL
SECRET=your-secret-key-here
REGISTRATION_ENABLED=true
BACKEND_URL=https://your-railway-url.railway.app

# LLM Providers (add your keys)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
GROQ_API_KEY=...

# ETL Service
ETL_SERVICE=DOCLING

# Optional: LangSmith Tracing
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=...
LANGCHAIN_PROJECT=kitab-production
```

### Vercel Frontend (Complete List)

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

### Backend won't start

- Check Railway logs for errors
- Verify `PYTHONPATH=/app` is set
- Ensure `runtime.txt` contains `python-3.12`

### Frontend can't connect to backend

- Verify `NEXT_PUBLIC_FASTAPI_BACKEND_URL` is correct
- Check CORS configuration in Railway
- Look for CORS errors in browser console

### Database connection fails

- Verify Supabase connection string is correct
- Check password is properly URL-encoded
- Ensure pgvector extension is enabled

### Celery worker not processing tasks

- Check worker logs in Railway
- Verify Redis connection URL is correct
- Ensure all environment variables are copied to worker service

### CORS errors

- Verify `CORS_ORIGINS` includes your Vercel URL
- Check for typos in domain names
- Ensure Railway redeployed after CORS update

---

## Rollback Plan

If deployment fails:

```bash
# Switch back to main branch
git checkout main

# Or reset to backup tag
git reset --hard pre-kitab-backup

# Force push if needed (CAUTION)
git push origin main --force
```

---

## Next Steps After Deployment

1. Test all functionality (see TEST_CHECKLIST.md)
2. Monitor logs for errors
3. Set up custom domain (optional)
4. Configure monitoring/alerting
5. Set up backup strategy
6. Document any deployment-specific issues

---

## Support

- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- Supabase Docs: https://supabase.com/docs
- GitHub Issues: https://github.com/AhmedTElKodsh/Kitab-SurfSense-fork/issues
