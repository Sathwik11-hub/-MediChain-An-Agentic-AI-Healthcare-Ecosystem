# Environment Variables for Different Deployment Platforms

## 🔐 Required Environment Variables

### Core LLM APIs
```bash
OPENAI_API_KEY=sk-xxx                    # Required for OpenAI models
ANTHROPIC_API_KEY=sk-ant-xxx             # Required for Claude models
```

### Vector Database (Pinecone)
```bash
PINECONE_API_KEY=xxx                     # Pinecone API key
PINECONE_ENVIRONMENT=xxx                 # e.g., us-west1-gcp
PINECONE_INDEX_NAME=medichain            # Your index name
```

### Graph Database (Neo4j)
```bash
NEO4J_URI=bolt://localhost:7687          # Neo4j connection URI
NEO4J_USER=neo4j                         # Neo4j username
NEO4J_PASSWORD=password                  # Neo4j password
```

### Relational Database (PostgreSQL)
```bash
POSTGRES_URI=postgresql://user:password@localhost:5432/medichain
POSTGRES_USER=medichain
POSTGRES_PASSWORD=password
POSTGRES_DB=medichain
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### Application Configuration
```bash
SECRET_KEY=your-secret-key-change-in-production-use-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### API Configuration
```bash
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=https://your-backend.railway.app  # Backend URL for frontend
```

### External APIs (Optional)
```bash
PUBMED_API_KEY=xxx                       # For medical research access
PUBMED_EMAIL=your-email@example.com
```

---

## 🚀 Platform-Specific Setup

### Vercel (Frontend Only)

**Required Variables:**
```bash
BACKEND_API_URL=https://your-backend.railway.app
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
```

**Setup in Vercel Dashboard:**
1. Go to Project Settings → Environment Variables
2. Add each variable with appropriate scope (Production, Preview, Development)
3. Redeploy after adding variables

**CLI Setup:**
```bash
vercel env add BACKEND_API_URL production
vercel env add OPENAI_API_KEY production
vercel env add ANTHROPIC_API_KEY production
```

---

### Railway (Full Stack)

**Required Variables:**
```bash
# Core APIs
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
PINECONE_API_KEY=xxx
PINECONE_ENVIRONMENT=xxx
PINECONE_INDEX_NAME=medichain

# Database (Railway provides these automatically if you add a database)
DATABASE_URL=postgresql://...  # Auto-provided by Railway
NEO4J_URI=bolt://...           # If using Neo4j plugin

# Security
SECRET_KEY=generate-long-random-string-here

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Setup in Railway:**
1. Go to Project → Variables
2. Add each variable
3. Railway auto-restarts on variable changes

**CLI Setup:**
```bash
railway variables set OPENAI_API_KEY=sk-xxx
railway variables set ANTHROPIC_API_KEY=sk-ant-xxx
railway variables set SECRET_KEY=$(openssl rand -hex 32)
```

---

### Render (Full Stack)

**Required Variables:**
```bash
# Core APIs
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
PINECONE_API_KEY=xxx
PINECONE_ENVIRONMENT=xxx
PINECONE_INDEX_NAME=medichain

# Database (Render provides DATABASE_URL automatically)
DATABASE_URL=postgresql://...  # Auto-provided if you add Postgres

# Security
SECRET_KEY=generate-long-random-string-here

# Environment
ENVIRONMENT=production
PYTHON_VERSION=3.11
```

**Setup in Render Dashboard:**
1. Go to Service → Environment
2. Add each variable
3. Variables in `render.yaml` are synchronized automatically
4. Manual additions take precedence

---

### Google Cloud Run

**Required Variables:**
```bash
# Core APIs
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
PINECONE_API_KEY=xxx
PINECONE_ENVIRONMENT=xxx

# Database (use Cloud SQL or external)
POSTGRES_URI=postgresql://...
NEO4J_URI=bolt://...

# Security
SECRET_KEY=generate-long-random-string-here
```

**Setup via CLI:**
```bash
gcloud run deploy medichain-api \
  --set-env-vars="OPENAI_API_KEY=sk-xxx,ANTHROPIC_API_KEY=sk-ant-xxx" \
  --set-env-vars="PINECONE_API_KEY=xxx,PINECONE_ENVIRONMENT=xxx" \
  --set-env-vars="SECRET_KEY=$(openssl rand -hex 32)" \
  --set-env-vars="ENVIRONMENT=production"
```

**Or use Secret Manager:**
```bash
# Store secrets
echo "sk-xxx" | gcloud secrets create openai-api-key --data-file=-

# Reference in deployment
gcloud run deploy medichain-api \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest"
```

---

### Fly.io

**Required Variables:**
```bash
# Same as Railway/Render
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
# ... etc
```

**Setup via CLI:**
```bash
fly secrets set OPENAI_API_KEY=sk-xxx
fly secrets set ANTHROPIC_API_KEY=sk-ant-xxx
fly secrets set SECRET_KEY=$(openssl rand -hex 32)
```

---

## 🔒 Security Best Practices

### Generating Secure Keys

```bash
# Generate SECRET_KEY (256-bit)
openssl rand -hex 32

# Generate SECRET_KEY (512-bit, more secure)
openssl rand -hex 64

# Python method
python -c "import secrets; print(secrets.token_hex(32))"
```

### Never Commit Secrets
```bash
# Always in .gitignore
.env
.env.local
.env.*.local

# Exception: .env.example (with placeholder values)
```

### Use Different Keys Per Environment
```bash
# Development
SECRET_KEY=dev-key-not-secure

# Staging
SECRET_KEY=staging-key-$(openssl rand -hex 32)

# Production
SECRET_KEY=prod-key-$(openssl rand -hex 64)
```

---

## 🧪 Testing Environment Variables

### Local Testing
```bash
# Create .env from template
cp .env.example .env

# Edit with your values
nano .env  # or code .env

# Test loading
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓ Loaded:', os.getenv('OPENAI_API_KEY')[:10] + '...')"
```

### Verify in Application
```python
# Add to your app startup
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = [
    'OPENAI_API_KEY',
    'ANTHROPIC_API_KEY',
    'SECRET_KEY'
]

for var in required_vars:
    if not os.getenv(var):
        raise ValueError(f"Missing required environment variable: {var}")
    print(f"✓ {var} is set")
```

---

## 📋 Environment Variable Checklist

### Frontend Deployment (Vercel)
- [ ] `BACKEND_API_URL`
- [ ] `OPENAI_API_KEY` (if using OpenAI directly)
- [ ] `ENVIRONMENT=production`

### Backend Deployment (Railway/Render)
- [ ] `OPENAI_API_KEY`
- [ ] `ANTHROPIC_API_KEY`
- [ ] `PINECONE_API_KEY`
- [ ] `PINECONE_ENVIRONMENT`
- [ ] `PINECONE_INDEX_NAME`
- [ ] `NEO4J_URI`
- [ ] `NEO4J_USER`
- [ ] `NEO4J_PASSWORD`
- [ ] `DATABASE_URL` or `POSTGRES_URI`
- [ ] `SECRET_KEY`
- [ ] `ENVIRONMENT=production`
- [ ] `LOG_LEVEL=INFO`

### Optional but Recommended
- [ ] `SENTRY_DSN` (error tracking)
- [ ] `PUBMED_API_KEY` (medical research)
- [ ] `SLACK_WEBHOOK_URL` (notifications)

---

## 🔄 Migration from Development to Production

```bash
# 1. Copy .env.example to .env.production
cp .env.example .env.production

# 2. Generate production secrets
echo "SECRET_KEY=$(openssl rand -hex 64)" >> .env.production

# 3. Update with production values
nano .env.production

# 4. Upload to platform (example: Railway)
cat .env.production | while IFS='=' read -r key value; do
  [ -z "$key" ] || railway variables set "$key=$value"
done

# 5. Verify
railway variables
```

---

## 🆘 Troubleshooting

### Variable Not Found
```bash
# Check if variable is set
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY%  # Windows

# In Python
import os
print(os.getenv('OPENAI_API_KEY'))
```

### Variable Not Loading
```bash
# Ensure .env is in root directory
ls -la .env

# Check file format (no BOM, UTF-8)
file .env

# Test with python-dotenv
python -c "from dotenv import load_dotenv; load_dotenv(verbose=True)"
```

### Platform Not Recognizing Variables
```bash
# Redeploy after setting variables
vercel --prod --force  # Vercel
railway up --force     # Railway
fly deploy             # Fly.io

# Check logs
vercel logs
railway logs
fly logs
```

---

## 📚 Additional Resources

- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Railway Environment Variables](https://docs.railway.app/develop/variables)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [12-Factor App: Config](https://12factor.net/config)
