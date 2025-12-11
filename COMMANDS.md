# Quick Command Reference for MediChain Deployment

## 🧹 Cleanup Commands (Run these first!)

```bash
# Run automated cleanup script
./cleanup.sh

# OR manually:

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# Remove virtual environments
rm -rf venv/ env/ .venv/ ENV/

# Remove test artifacts
rm -rf .pytest_cache/ .coverage htmlcov/ .tox/

# Remove build artifacts
rm -rf build/ dist/ *.egg-info/
```

## 🔍 Analysis Commands

```bash
# Find files larger than 10MB
find . -type f -size +10M -exec ls -lh {} \; | awk '{print $5, $9}'

# Find files larger than 5MB
find . -type f -size +5M -exec ls -lh {} \; | awk '{print $5, $9}'

# Check directory sizes (sorted)
du -sh */ | sort -hr

# Check total project size
du -sh .

# Count files by type
find . -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -20

# Find all Python cache directories
find . -type d -name "__pycache__" -o -name "*.egg-info" -o -name ".pytest_cache"

# Check what git will include (respects .gitignore)
git ls-files -z | xargs -0 du -ch | tail -n1

# Check what's being ignored by git
git status --ignored

# List largest files in git
git ls-files | xargs -I {} ls -lh {} | sort -k5 -hr | head -20
```

## 🚀 Deployment Commands

### Option 1: Vercel (Frontend Only)

```bash
# Switch to lightweight requirements
cp requirements-vercel.txt requirements.txt

# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# Debug deployment
vercel --debug
```

### Option 2: Railway (Full Stack)

```bash
# Switch to full requirements
cp requirements-full.txt requirements.txt

# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# View logs
railway logs
```

### Option 3: Render (Full Stack)

```bash
# Switch to full requirements
cp requirements-full.txt requirements.txt

# Deployment is done via Render Dashboard or:
# 1. Connect GitHub repo in Render dashboard
# 2. Select "New Web Service"
# 3. Render will detect render.yaml automatically

# Or use Render CLI (if installed)
render deploy
```

### Option 4: Google Cloud Run

```bash
# Switch to full requirements
cp requirements-full.txt requirements.txt

# Build and deploy
gcloud run deploy medichain-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --timeout 300 \
  --max-instances 10

# View logs
gcloud run logs read --service medichain-api --limit 50
```

### Option 5: Docker (Local Test)

```bash
# Build Docker image
docker build -t medichain:latest .

# Run container
docker run -p 8000:8000 --env-file .env medichain:latest

# Check image size
docker images medichain:latest

# Remove unused Docker data
docker system prune -a
```

### Option 6: Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch app
fly launch

# Deploy
fly deploy

# View logs
fly logs
```

## 📦 Dependency Management

```bash
# Create requirements from current environment
pip freeze > requirements-current.txt

# Install from requirements
pip install -r requirements-vercel.txt    # For frontend
pip install -r requirements-full.txt      # For backend

# Check installed package sizes
pip list --format=freeze | while read pkg; do 
  pip show ${pkg%=*} | grep -E "^(Name|Location)"; 
  du -sh $(pip show ${pkg%=*} | grep Location | cut -d' ' -f2) 2>/dev/null; 
done | paste - - - | sort -k6 -hr | head -20

# Uninstall heavy packages (if not needed)
pip uninstall sentence-transformers faiss-cpu torch -y
```

## 🧪 Testing Commands

```bash
# Run tests locally
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api.py -v

# Check code quality
flake8 . --max-line-length=120 --exclude=venv,env

# Type checking (if using mypy)
mypy . --ignore-missing-imports
```

## 🔐 Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env  # or vim, code, etc.

# Test environment loading
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓ Environment loaded')"
```

## 🗄️ Database Commands

```bash
# PostgreSQL (if using locally)
psql -U postgres -d medichain

# Neo4j (if using locally)
docker run -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# Check database connection
python -c "from services.database_service import DatabaseService; print('✓ DB connected')"
```

## 📊 Monitoring Commands

```bash
# Check service health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# Check Streamlit frontend
streamlit run frontend/app.py

# Monitor resources
htop  # or top on macOS
```

## 🆘 Troubleshooting Commands

```bash
# Check Python version
python --version

# Check pip version
pip --version

# Verify packages installed
pip list

# Clear pip cache
pip cache purge

# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall --no-cache-dir

# Check for conflicts
pip check

# Debug import errors
python -c "import langchain; print('✓ langchain OK')"
python -c "import streamlit; print('✓ streamlit OK')"

# Check port availability
lsof -i :8000  # Check if port 8000 is in use

# Kill process on port
kill -9 $(lsof -t -i:8000)
```

## 🔄 Git Commands

```bash
# Check what's tracked
git ls-files

# Check repository size
git count-objects -vH

# Clean untracked files (BE CAREFUL!)
git clean -fdx  # Removes all untracked files

# Add all changes
git add .

# Commit with message
git commit -m "Fixed deployment size issues"

# Push to GitHub
git push origin main

# Create new branch for deployment
git checkout -b deployment-optimization
```

## 📈 Performance Testing

```bash
# Test API endpoint response time
time curl http://localhost:8000/health

# Load testing with Apache Bench (if installed)
ab -n 100 -c 10 http://localhost:8000/health

# Test Streamlit performance
streamlit run frontend/app.py --logger.level=debug
```

## 🎯 Quick Deployment Checklist

```bash
# 1. Clean project
./cleanup.sh

# 2. Verify size
du -sh .

# 3. Choose requirements
cp requirements-vercel.txt requirements.txt  # OR requirements-full.txt

# 4. Test locally
python -m pytest tests/
streamlit run frontend/app.py

# 5. Deploy
vercel --prod  # OR railway up, OR fly deploy

# 6. Verify deployment
curl https://your-app.vercel.app/health
```

## 🆘 Emergency Size Reduction

If you're still over the limit:

```bash
# 1. Remove ALL cache aggressively
find . -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".git" -exec du -sh {} \;  # Check git size

# 2. Clean git history (if git is huge)
git gc --aggressive --prune=now

# 3. Remove git history (NUCLEAR OPTION - creates new repo)
rm -rf .git
git init
git add .
git commit -m "Initial commit - cleaned"

# 4. Use git-lfs for large files
git lfs install
git lfs track "*.pkl" "*.h5" "*.pt"

# 5. Verify final size
du -sh .
```
