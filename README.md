# 🏥 MediChain: Multi-Agent Medical AI System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)

An advanced multi-agent AI healthcare ecosystem that leverages **CrewAI**, **LangChain**, and modern medical knowledge retrieval systems to provide intelligent diagnostic support, treatment recommendations, and patient monitoring.

## 🌟 Features

### 🤖 **Five Specialized AI Agents**
1. **Symptom Analyzer** - Analyzes patient symptoms and generates differential diagnoses with ICD-10 codes
2. **Medical Knowledge Agent** - Retrieves and validates diagnoses against PubMed and medical literature
3. **Treatment Recommender** - Generates evidence-based, personalized treatment plans
4. **Patient Monitor** - Real-time vital signs monitoring with anomaly detection and alerts
5. **Ethical & Safety Agent** - Ensures HIPAA compliance, FDA regulations, and medical ethics

### 🔧 **Core Technologies**
- **Multi-Agent AI**: CrewAI for agent orchestration
- **LLM Integration**: OpenAI GPT-4 / Anthropic Claude
- **RAG System**: Pinecone/FAISS vector database + PubMed integration
- **Graph Database**: Neo4j for patient knowledge graphs
- **Relational DB**: PostgreSQL for structured data
- **Backend**: FastAPI with async support
- **Frontend**: Streamlit for intuitive UI
- **Deployment**: Docker, Kubernetes, CI/CD ready

### 🔒 **Healthcare Compliance**
- HIPAA compliance for data privacy
- FDA medication validation
- Medical ethics guidelines enforcement
- Audit logging and access control

---

## 📁 Project Structure

```
medichain/
├── agents/                 # AI agent implementations
│   ├── symptom_analyzer.py
│   ├── medical_knowledge.py
│   ├── treatment_recommender.py
│   ├── patient_monitor.py
│   └── ethical_safety.py
├── services/              # Core services
│   ├── llm_service.py
│   ├── rag_service.py
│   └── database_service.py
├── orchestration/         # Agent workflow management
│   └── crew_manager.py
├── api/                   # FastAPI backend
│   └── main.py
├── frontend/              # Streamlit UI
│   └── app.py
├── models/                # Pydantic data models
│   └── patient.py
├── config/                # Configuration
│   ├── settings.py
│   └── prompts.py
├── tests/                 # Test suite
├── deployment/            # Deployment configs
│   ├── kubernetes/
│   └── terraform/
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenAI API key or Anthropic API key
- PostgreSQL (or use Docker)
- Neo4j (or use Docker)

### 1. Clone Repository

```bash
git clone https://github.com/Sathwik11-hub/-MediChain-An-Agentic-AI-Healthcare-Ecosystem.git
cd -MediChain-An-Agentic-AI-Healthcare-Ecosystem
```

### 2. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

**Required environment variables:**
```bash
OPENAI_API_KEY=sk-xxx                    # OpenAI API key
ANTHROPIC_API_KEY=sk-ant-xxx             # Or Anthropic API key
PINECONE_API_KEY=xxx                     # Vector database
PINECONE_ENVIRONMENT=xxx
POSTGRES_URI=postgresql://...            # Database connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 4. Run with Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Access:
# - API: http://localhost:8000
# - Frontend: http://localhost:8501
# - API Docs: http://localhost:8000/docs
```

### 5. Run Locally

```bash
# Terminal 1: Start databases (if not using Docker)
docker-compose up -d postgres neo4j

# Terminal 2: Start API
python api/main.py
# Or: uvicorn api.main:app --reload

# Terminal 3: Start Frontend
streamlit run frontend/app.py

# Access:
# - API: http://localhost:8000
# - Frontend: http://localhost:8501
```

---

## 📖 Usage Guide

### Creating a Patient

**Via Frontend:**
1. Navigate to "New Patient" page
2. Fill in patient information (ID, name, age, gender, medical history, allergies)
3. Click "Register Patient"

**Via API:**
```bash
curl -X POST http://localhost:8000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P12345",
    "name": "John Doe",
    "age": 45,
    "gender": "male",
    "medical_history": ["Hypertension", "Type 2 Diabetes"],
    "allergies": ["Penicillin"],
    "current_medications": ["Metformin", "Lisinopril"]
  }'
```

### Creating and Analyzing a Case

**Via Frontend:**
1. Go to "New Case" page
2. Enter patient ID
3. Describe symptoms (name, severity, duration)
4. Click "Create Case" then "Analyze Case Now"
5. View results: diagnoses, treatment plan, safety review

**Via API:**
```bash
# Create case
curl -X POST http://localhost:8000/api/cases/create \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P12345",
    "symptoms": {
      "symptoms": [
        {"name": "Fever", "severity": 7, "duration_days": 3, "description": "High fever with chills"},
        {"name": "Cough", "severity": 5, "duration_days": 3, "description": "Dry cough"}
      ],
      "chief_complaint": "Fever and cough",
      "onset": "3 days ago"
    }
  }'

# Analyze case
curl -X POST http://localhost:8000/api/cases/{case_id}/analyze
```

### Monitoring Patient Vitals

**Via Frontend:**
1. Navigate to "Patient Monitoring" page
2. Enter patient ID and vital signs
3. Click "Monitor Vitals"
4. View analysis with alerts and recommendations

**Via API:**
```bash
curl -X POST http://localhost:8000/api/monitor/vitals \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P12345",
    "heart_rate": 120,
    "blood_pressure_systolic": 140,
    "blood_pressure_diastolic": 90,
    "temperature": 38.5,
    "respiratory_rate": 22,
    "oxygen_saturation": 95
  }'
```

---

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## 🐳 Docker Deployment

### Development

```bash
docker-compose up -d
```

### Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## ☸️ Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace medichain

# Apply configurations
kubectl apply -f deployment/kubernetes/deployment.yaml
kubectl apply -f deployment/kubernetes/service.yaml
kubectl apply -f deployment/kubernetes/ingress.yaml
kubectl apply -f deployment/kubernetes/hpa.yaml

# Check status
kubectl get pods -n medichain
kubectl get services -n medichain

# View logs
kubectl logs -f deployment/medichain-api -n medichain
```

---

## 📊 API Documentation

Once the API is running, access interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/patients` | POST | Create patient |
| `/api/patients/{id}` | GET | Get patient info |
| `/api/patients/{id}/history` | GET | Get patient history |
| `/api/cases/create` | POST | Create new case |
| `/api/cases/{id}/analyze` | POST | Analyze case |
| `/api/cases/{id}` | GET | Get case details |
| `/api/monitor/vitals` | POST | Monitor vital signs |

---

## 🔐 Security & Compliance

### HIPAA Compliance
- Encrypted data at rest and in transit
- Audit logging for all access
- Role-based access control (RBAC)
- De-identification of sensitive data

### FDA Validation
- Medication approval checking
- Off-label use flagging
- Contraindication detection

### Data Privacy
- No PHI in logs
- Secure credential management
- Regular security audits

---

## 🛠️ Configuration

### LLM Provider

Edit `config/settings.py` or set environment variables:

```bash
# Use OpenAI
LLM_PROVIDER=openai
LLM_MODEL=gpt-4

# Or use Anthropic
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-opus-20240229
```

### Vector Database

```bash
# Use Pinecone (recommended for production)
PINECONE_API_KEY=xxx
PINECONE_ENVIRONMENT=xxx

# Or FAISS will be used automatically (in-memory)
```

---

## 📈 Monitoring & Logging

### Application Logs

```bash
# View logs
tail -f logs/medichain.log

# Docker logs
docker-compose logs -f api
```

### Metrics

- LLM usage tracking (tokens, cost)
- API response times
- Database query performance
- Agent execution times

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LangChain** - LLM framework
- **CrewAI** - Multi-agent orchestration
- **FastAPI** - Modern Python web framework
- **Streamlit** - Interactive web apps
- **PubMed/NCBI** - Medical literature database

---

## 📞 Support

For issues, questions, or contributions:

- **Issues**: [GitHub Issues](https://github.com/Sathwik11-hub/-MediChain-An-Agentic-AI-Healthcare-Ecosystem/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Sathwik11-hub/-MediChain-An-Agentic-AI-Healthcare-Ecosystem/discussions)

---

## 🎓 Use Cases

This project is perfect for:

- ✅ Final year engineering project
- ✅ Research paper on AI in healthcare
- ✅ Portfolio project for job applications
- ✅ Startup MVP for health tech
- ✅ Learning multi-agent AI systems

---

## ⚠️ Disclaimer

**This system is for educational and research purposes only. It is NOT intended for clinical use or to replace professional medical advice. Always consult qualified healthcare professionals for medical decisions.**

---

## 🚀 Roadmap

- [ ] Add real-time collaboration features
- [ ] Integrate with FHIR (Fast Healthcare Interoperability Resources)
- [ ] Add telemedicine capabilities
- [ ] Implement advanced analytics dashboard
- [ ] Mobile application (iOS/Android)
- [ ] Multi-language support
- [ ] Integration with wearable devices
- [ ] Advanced ML models for prediction

---

**Built with ❤️ by Sathwik**