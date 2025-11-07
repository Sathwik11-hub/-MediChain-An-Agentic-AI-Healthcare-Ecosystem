# 🏥 MediChain: Quick Reference Guide

## System Overview

MediChain is a **Multi-Agent Medical AI System** that combines 5 specialized AI agents to provide comprehensive healthcare support.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                     (Streamlit Frontend)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Dashboard │  │ Patient  │  │   Case   │  │ Monitor  │      │
│  │          │  │   Mgmt   │  │ Analysis │  │  Vitals  │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER                                │
│                    (FastAPI Backend)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ /api/patients  │ /api/cases  │ /api/monitor/vitals      │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                           │
│                     (Crew Manager)                              │
│  Coordinates: Symptom → Knowledge → Treatment → Ethics         │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   AGENT 1    │  │   AGENT 2    │  │   AGENT 3    │
│   Symptom    │  │   Medical    │  │  Treatment   │
│   Analyzer   │  │  Knowledge   │  │ Recommender  │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐
│   AGENT 4    │  │   AGENT 5    │
│   Patient    │  │   Ethical    │
│   Monitor    │  │   & Safety   │
└──────────────┘  └──────────────┘
        │                │
        └────────────────┼────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  LLM Service │  │  RAG Service │  │   Database   │         │
│  │ GPT-4/Claude │  │Vector+PubMed │  │Neo4j+Postgres│         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Example

### Creating and Analyzing a Case

```
1. PATIENT REGISTRATION
   └─> POST /api/patients
       ├─> Store in PostgreSQL
       └─> Create node in Neo4j

2. CASE CREATION
   └─> POST /api/cases/create
       ├─> Patient ID
       └─> Symptoms (name, severity, duration)

3. CASE ANALYSIS
   └─> POST /api/cases/{id}/analyze
       │
       ├─> STEP 1: Symptom Analyzer
       │   ├─> Analyze symptoms
       │   ├─> Generate differential diagnoses
       │   └─> Output: ICD-10 codes + confidence
       │
       ├─> STEP 2: Medical Knowledge
       │   ├─> Search PubMed
       │   ├─> Retrieve evidence
       │   └─> Output: Research citations
       │
       ├─> STEP 3: Treatment Recommender
       │   ├─> Generate treatment plan
       │   ├─> Check allergies/contraindications
       │   └─> Output: Medications + monitoring
       │
       ├─> STEP 4: Ethical & Safety
       │   ├─> HIPAA compliance check
       │   ├─> FDA medication validation
       │   └─> Output: Compliance report
       │
       └─> STEP 5: Store Results
           ├─> Save to PostgreSQL
           └─> Update Neo4j graph

4. VIEW RESULTS
   └─> GET /api/cases/{id}
       ├─> Diagnoses with confidence
       ├─> Treatment plan
       ├─> Safety review
       └─> Medical citations
```

## Agent Capabilities

| Agent | Input | Output | Purpose |
|-------|-------|--------|---------|
| **Symptom Analyzer** | Patient symptoms | Differential diagnoses with ICD-10 | Primary diagnosis |
| **Medical Knowledge** | Diagnosis | Research papers, citations | Evidence validation |
| **Treatment Recommender** | Diagnosis + Patient data | Treatment plan, medications | Personalized treatment |
| **Patient Monitor** | Vital signs | Alerts, anomalies | Real-time monitoring |
| **Ethical & Safety** | All above | Compliance report | Safety validation |

## API Endpoints Quick Reference

### Patient Management
```bash
# Create patient
POST /api/patients
{
  "patient_id": "P12345",
  "name": "John Doe",
  "age": 45,
  "gender": "male",
  "medical_history": ["Hypertension"],
  "allergies": ["Penicillin"],
  "current_medications": ["Lisinopril"]
}

# Get patient
GET /api/patients/{patient_id}

# Get patient history
GET /api/patients/{patient_id}/history
```

### Case Management
```bash
# Create case
POST /api/cases/create
{
  "patient_id": "P12345",
  "symptoms": {
    "symptoms": [
      {
        "name": "Fever",
        "severity": 7,
        "duration_days": 3,
        "description": "High fever"
      }
    ],
    "chief_complaint": "Fever and cough",
    "onset": "3 days ago"
  }
}

# Analyze case
POST /api/cases/{case_id}/analyze

# Get case details
GET /api/cases/{case_id}

# Get case status
GET /api/cases/{case_id}/status
```

### Monitoring
```bash
# Monitor vitals
POST /api/monitor/vitals
{
  "patient_id": "P12345",
  "heart_rate": 120,
  "blood_pressure_systolic": 140,
  "blood_pressure_diastolic": 90,
  "temperature": 38.5,
  "respiratory_rate": 22,
  "oxygen_saturation": 95
}
```

## Configuration Quick Start

### 1. Environment Variables
```bash
# Copy template
cp .env.example .env

# Required variables
OPENAI_API_KEY=sk-xxx                    # Or ANTHROPIC_API_KEY
POSTGRES_URI=postgresql://...
NEO4J_URI=bolt://localhost:7687
PINECONE_API_KEY=xxx                     # Optional
```

### 2. Docker Deployment
```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### 3. Local Development
```bash
# Terminal 1: Start databases
docker-compose up -d postgres neo4j

# Terminal 2: Start API
python api/main.py

# Terminal 3: Start Frontend
streamlit run frontend/app.py
```

### 4. Kubernetes Deployment
```bash
# Apply configurations
kubectl apply -f deployment/kubernetes/

# Check status
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/medichain-api
```

## Project Structure

```
medichain/
├── agents/              # 5 AI agents
├── services/            # LLM, RAG, Database
├── orchestration/       # Workflow management
├── api/                 # FastAPI backend
├── frontend/            # Streamlit UI
├── models/              # Data models
├── config/              # Settings & prompts
├── tests/               # Test suite
├── deployment/          # K8s configs
├── docker-compose.yml   # Docker setup
└── requirements.txt     # Dependencies
```

## Common Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=.

# Start API
python api/main.py

# Start Frontend
streamlit run frontend/app.py
```

### Docker
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean up
docker-compose down -v
```

### Kubernetes
```bash
# Deploy
kubectl apply -f deployment/kubernetes/

# Scale
kubectl scale deployment medichain-api --replicas=5

# Update
kubectl rollout restart deployment/medichain-api

# Delete
kubectl delete -f deployment/kubernetes/
```

## Troubleshooting

### Issue: Cannot connect to API
**Solution:**
```bash
# Check if API is running
curl http://localhost:8000/health

# Check Docker logs
docker-compose logs api

# Verify environment variables
docker-compose config
```

### Issue: Database connection error
**Solution:**
```bash
# Check database status
docker-compose ps

# Restart databases
docker-compose restart postgres neo4j

# Check connection strings in .env
```

### Issue: LLM API errors
**Solution:**
- Verify API key in .env
- Check API quota/limits
- Review logs for specific error
- Try alternative provider (OpenAI ↔ Anthropic)

## Performance Tips

1. **Use Docker for databases** - More reliable than local installs
2. **Enable caching** - RAG results can be cached
3. **Tune LLM parameters** - Adjust temperature and max_tokens
4. **Monitor costs** - Use token tracking in LLM service
5. **Scale horizontally** - Use Kubernetes HPA for auto-scaling

## Security Checklist

- [ ] API keys stored in .env (not in code)
- [ ] .env added to .gitignore
- [ ] HTTPS enabled in production
- [ ] Authentication enabled for API
- [ ] Database credentials secured
- [ ] Audit logging enabled
- [ ] HIPAA compliance verified
- [ ] Regular security updates

## Resources

- **Documentation**: README.md, IMPLEMENTATION.md
- **API Docs**: http://localhost:8000/docs
- **Source Code**: GitHub repository
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## Support

For help:
1. Check README.md and IMPLEMENTATION.md
2. Review API documentation
3. Check logs for errors
4. Search existing GitHub issues
5. Create new issue with details

---

**Built with ❤️ for the future of AI in healthcare**

*Remember: This is for educational purposes only. Not for clinical use.*
