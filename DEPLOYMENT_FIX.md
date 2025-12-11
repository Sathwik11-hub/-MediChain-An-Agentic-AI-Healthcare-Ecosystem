# MediChain Deployment Guide

## 🚨 CRITICAL: Vercel Size Limit Issue

Your project exceeded Vercel's 4GB deployment limit (4.43GB detected) due to heavy ML dependencies.

## 📊 Size Analysis

**Heavy Dependencies (~3.5GB when installed):**
- `sentence-transformers`: ~1.2GB (includes PyTorch models)
- `faiss-cpu`: ~500MB
- `langchain` + `crewai`: ~800MB
- `biopython`: ~200MB
- Other ML libraries: ~800MB

**Your source code:** ~280KB (perfectly fine!)

## ✅ SOLUTION 1: Split Architecture (RECOMMENDED)

Deploy as microservices:

### Frontend on Vercel
- Deploy only the Streamlit frontend
- Use `requirements-vercel.txt` (lightweight, ~200MB)
- Connect to backend API via HTTP

### Backend on Railway/Render/Cloud Run
- Deploy FastAPI with full ML stack
- Use `requirements-full.txt`
- Handles all heavy AI/ML processing

## 🛠️ Implementation Steps

### Step 1: Clean Your Repository

```bash
# Remove all build artifacts, cache, and virtual environments
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete

# Remove virtual environments
rm -rf venv/ env/ .venv/ ENV/

# Remove any data files or models (move to cloud storage)
# rm -rf data/ models/ checkpoints/ *.pkl *.h5 *.pt
```

### Step 2: Check Directory Sizes

```bash
# Find large files (>10MB)
find . -type f -size +10M -exec ls -lh {} \;

# Check directory sizes
du -sh */ | sort -hr

# Total project size
du -sh .
```

### Step 3A: Deploy Frontend to Vercel

1. **Update requirements.txt for Vercel:**
   ```bash
   cp requirements-vercel.txt requirements.txt
   ```

2. **Set environment variables in Vercel dashboard:**
   - `BACKEND_API_URL`: Your backend API URL
   - `OPENAI_API_KEY`: Your OpenAI key (if used in frontend)

3. **Deploy:**
   ```bash
   vercel --prod
   ```

### Step 3B: Deploy Backend to Railway

1. **Create Railway project:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and initialize
   railway login
   railway init
   ```

2. **Use full requirements:**
   ```bash
   cp requirements-full.txt requirements.txt
   ```

3. **Create `Procfile` for Railway:**
   ```bash
   echo "web: uvicorn api.main:app --host 0.0.0.0 --port \$PORT" > Procfile
   ```

4. **Deploy:**
   ```bash
   railway up
   ```

### Step 3C: Alternative - Deploy Backend to Render

1. **Create `render.yaml`:**
   ```yaml
   services:
     - type: web
       name: medichain-api
       env: python
       buildCommand: pip install -r requirements-full.txt
       startCommand: uvicorn api.main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: PYTHON_VERSION
           value: 3.11
   ```

2. **Deploy via Render dashboard** or CLI

### Step 3D: Alternative - Google Cloud Run

```bash
# Build and deploy with full requirements
gcloud run deploy medichain-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --timeout 300 \
  --max-instances 10
```

## 📋 Files Created

1. **`.vercelignore`** - Excludes heavy files from Vercel
2. **`vercel.json`** - Vercel configuration (frontend only)
3. **`requirements-vercel.txt`** - Lightweight deps for frontend (~200MB)
4. **`requirements-full.txt`** - Full deps for backend (~3.5GB)
5. **`.dockerignore`** - Optimized Docker builds

## 🔧 Architecture Options

### Option A: Full Separation (Best for Production)
```
Frontend (Vercel)     →     Backend API (Railway/Render)
- Streamlit           →     - FastAPI
- User Interface      →     - ML Models
- ~200MB              →     - Vector DB
                      →     - ~3.5GB
```

### Option B: Use External APIs Only
```
Frontend (Vercel)
- Streamlit
- Direct API calls to OpenAI/Anthropic
- No local ML models
- ~150MB
```

### Option C: Docker Container (Any Cloud)
```
Docker (Cloud Run/ECS/Azure Container Apps)
- Full Stack
- All dependencies
- Auto-scaling
- ~4GB image
```

## 💡 Cost Comparison

| Platform | Free Tier | Cost (Prod) | Best For |
|----------|-----------|-------------|----------|
| Vercel (Frontend) | 100GB-hours | ~$20/mo | Frontend only |
| Railway | $5 credit | ~$15-30/mo | Full-stack, easy setup |
| Render | 750 hours | ~$20-50/mo | Reliable, managed |
| Cloud Run | 2M requests | Pay-per-use | Scalable, cost-effective |
| Fly.io | 3 VMs free | ~$10-30/mo | Global edge deployment |

## 🚀 Quick Start (Recommended Path)

1. **For Frontend-Only on Vercel:**
   ```bash
   # Use lightweight requirements
   cp requirements-vercel.txt requirements.txt
   vercel --prod
   ```

2. **For Full-Stack on Railway:**
   ```bash
   # Use full requirements
   cp requirements-full.txt requirements.txt
   railway login
   railway init
   railway up
   ```

## 🔍 Debugging Size Issues

```bash
# Check what Vercel will upload
git ls-files -z | xargs -0 du -ch | tail -n1

# Check ignored files
git status --ignored

# Verify .vercelignore is working
vercel --debug
```

## 📚 Additional Resources

- [Vercel Python Deployment](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Railway Python Guide](https://docs.railway.app/guides/python)
- [Render Python Docs](https://render.com/docs/deploy-python)
- [Cloud Run Quickstart](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service)

## ⚠️ Important Notes

1. **Never commit virtual environments** - Always in `.gitignore`
2. **Use `.vercelignore`** - Not just `.gitignore`
3. **Split heavy processing** - Frontend ≠ ML backend
4. **Use managed ML APIs** - OpenAI/Anthropic instead of local models when possible
5. **Store models externally** - S3/GCS for large model files
6. **Environment variables** - Never hardcode API keys

## 🎯 Expected Sizes After Optimization

- **Frontend deployment (Vercel):** ~200MB
- **Backend deployment (Railway/Render):** ~3.5GB
- **Source code repository:** ~300KB
- **Docker image (if used):** ~4GB

## ✅ Success Criteria

After following this guide, you should have:
- [ ] Repository cleaned of cache/venv
- [ ] `.vercelignore` and `vercel.json` configured
- [ ] Separate requirements files created
- [ ] Chosen deployment architecture
- [ ] Frontend deployed and accessible
- [ ] Backend deployed (if split architecture)
- [ ] Environment variables configured
- [ ] API connectivity tested
