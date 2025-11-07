"""
Streamlit frontend application for MediChain.
"""
import streamlit as st
import httpx
import json
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, Optional

# Page configuration
st.set_page_config(
    page_title="MediChain - Medical AI System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'
if 'patient_id' not in st.session_state:
    st.session_state.patient_id = None
if 'case_id' not in st.session_state:
    st.session_state.case_id = None


def make_api_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
    """Make API request to backend."""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        with httpx.Client(timeout=60.0) as client:
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json=data)
            elif method == "PUT":
                response = client.put(url, json=data)
            else:
                return {"error": f"Unsupported method: {method}"}
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API error: {response.status_code}", "detail": response.text}
    except Exception as e:
        return {"error": str(e)}


def show_dashboard():
    """Display dashboard page."""
    st.markdown('<p class="main-header">🏥 MediChain Dashboard</p>', unsafe_allow_html=True)
    
    # Check API health
    health = make_api_request("/health")
    
    if "error" not in health:
        st.success(f"✅ System Status: {health.get('status', 'unknown').upper()}")
    else:
        st.error("❌ Cannot connect to backend. Please ensure the API is running.")
        st.code(f"Run: python api/main.py")
        return
    
    # Statistics
    st.markdown('<p class="sub-header">System Statistics</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Cases", "0", help="Currently active cases")
    
    with col2:
        st.metric("Patients", "0", help="Total patients in system")
    
    with col3:
        st.metric("Diagnoses", "0", help="Total diagnoses made")
    
    with col4:
        st.metric("Accuracy", "N/A", help="Average diagnosis confidence")
    
    # Recent activity
    st.markdown('<p class="sub-header">Recent Activity</p>', unsafe_allow_html=True)
    st.info("No recent activity. Create a new case to get started.")
    
    # Quick actions
    st.markdown('<p class="sub-header">Quick Actions</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ New Patient", use_container_width=True):
            st.session_state.current_page = 'New Patient'
            st.rerun()
    
    with col2:
        if st.button("📋 New Case", use_container_width=True):
            st.session_state.current_page = 'New Case'
            st.rerun()
    
    with col3:
        if st.button("🔍 Search Cases", use_container_width=True):
            st.session_state.current_page = 'Case Search'
            st.rerun()


def show_new_patient():
    """Display new patient form."""
    st.markdown('<p class="main-header">➕ New Patient Registration</p>', unsafe_allow_html=True)
    
    with st.form("patient_form"):
        st.markdown('<p class="sub-header">Patient Information</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            patient_id = st.text_input("Patient ID *", placeholder="P12345")
            name = st.text_input("Full Name *", placeholder="John Doe")
            age = st.number_input("Age *", min_value=0, max_value=150, value=30)
        
        with col2:
            gender = st.selectbox("Gender *", ["male", "female", "other"])
            medical_history = st.text_area("Medical History", placeholder="Hypertension, Diabetes (comma-separated)")
            allergies = st.text_area("Allergies", placeholder="Penicillin, Latex (comma-separated)")
        
        current_medications = st.text_area("Current Medications", placeholder="Metformin, Lisinopril (comma-separated)")
        
        submitted = st.form_submit_button("Register Patient", use_container_width=True)
        
        if submitted:
            if not patient_id or not name or not age:
                st.error("Please fill in all required fields (*)")
            else:
                # Prepare data
                patient_data = {
                    "patient_id": patient_id,
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "medical_history": [h.strip() for h in medical_history.split(",") if h.strip()],
                    "allergies": [a.strip() for a in allergies.split(",") if a.strip()],
                    "current_medications": [m.strip() for m in current_medications.split(",") if m.strip()]
                }
                
                # Create patient
                with st.spinner("Registering patient..."):
                    result = make_api_request("/api/patients", method="POST", data=patient_data)
                
                if "error" not in result:
                    st.success(f"✅ Patient registered successfully! ID: {result.get('patient_id')}")
                    st.session_state.patient_id = result.get('patient_id')
                else:
                    st.error(f"❌ Error: {result.get('error')}")


def show_new_case():
    """Display new case form."""
    st.markdown('<p class="main-header">📋 New Medical Case</p>', unsafe_allow_html=True)
    
    # Patient selection
    patient_id = st.text_input("Patient ID *", value=st.session_state.get('patient_id', ''), placeholder="P12345")
    
    if patient_id:
        # Fetch patient info
        with st.spinner("Loading patient information..."):
            patient = make_api_request(f"/api/patients/{patient_id}")
        
        if "error" not in patient:
            st.success(f"✅ Patient found: {patient.get('name')} (Age: {patient.get('age')})")
            
            # Display patient info
            with st.expander("Patient Information"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Name:** {patient.get('name')}")
                    st.write(f"**Age:** {patient.get('age')}")
                    st.write(f"**Gender:** {patient.get('gender')}")
                with col2:
                    st.write(f"**Medical History:** {', '.join(patient.get('medical_history', []) or ['None'])}")
                    st.write(f"**Allergies:** {', '.join(patient.get('allergies', []) or ['None'])}")
        else:
            st.error("❌ Patient not found. Please register the patient first.")
            return
    
    # Symptoms form
    st.markdown('<p class="sub-header">Symptoms</p>', unsafe_allow_html=True)
    
    chief_complaint = st.text_input("Chief Complaint *", placeholder="Fever and cough")
    onset = st.text_input("Onset *", placeholder="3 days ago")
    
    st.markdown("**Symptom Details**")
    
    num_symptoms = st.number_input("Number of symptoms", min_value=1, max_value=10, value=2)
    
    symptoms = []
    for i in range(num_symptoms):
        st.markdown(f"**Symptom {i+1}**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            symptom_name = st.text_input(f"Name {i+1}", key=f"symptom_name_{i}", placeholder="Fever")
        with col2:
            severity = st.slider(f"Severity {i+1}", 1, 10, 5, key=f"severity_{i}")
        with col3:
            duration = st.number_input(f"Duration (days) {i+1}", min_value=0, value=3, key=f"duration_{i}")
        
        if symptom_name:
            symptoms.append({
                "name": symptom_name,
                "severity": severity,
                "duration_days": duration,
                "description": f"{symptom_name} for {duration} days"
            })
    
    # Submit case
    if st.button("Create Case", use_container_width=True):
        if not patient_id or not chief_complaint or not onset or len(symptoms) == 0:
            st.error("Please fill in all required fields (*)")
        else:
            # Prepare data
            case_data = {
                "patient_id": patient_id,
                "symptoms": {
                    "symptoms": symptoms,
                    "chief_complaint": chief_complaint,
                    "onset": onset
                }
            }
            
            # Create case
            with st.spinner("Creating case..."):
                result = make_api_request("/api/cases/create", method="POST", data=case_data)
            
            if "error" not in result:
                case_id = result.get('case_id')
                st.success(f"✅ Case created successfully! Case ID: {case_id}")
                st.session_state.case_id = case_id
                
                # Option to analyze
                if st.button("🔬 Analyze Case Now"):
                    st.session_state.current_page = 'Case Analysis'
                    st.rerun()
            else:
                st.error(f"❌ Error: {result.get('error')}")


def show_case_analysis():
    """Display case analysis page."""
    st.markdown('<p class="main-header">🔬 Case Analysis</p>', unsafe_allow_html=True)
    
    case_id = st.text_input("Case ID", value=st.session_state.get('case_id', ''), placeholder="Enter case ID")
    
    if st.button("Analyze Case", use_container_width=True) and case_id:
        with st.spinner("Running diagnostic workflow... This may take a minute."):
            result = make_api_request(f"/api/cases/{case_id}/analyze", method="POST")
        
        if "error" not in result:
            st.success("✅ Analysis completed!")
            
            # Display results
            st.markdown('<p class="sub-header">Analysis Results</p>', unsafe_allow_html=True)
            
            # Summary
            if 'summary' in result:
                summary = result['summary']
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Primary Diagnosis", summary.get('primary_diagnosis', 'N/A'))
                with col2:
                    st.metric("Confidence", f"{summary.get('confidence', 0)*100:.1f}%")
                with col3:
                    st.metric("ICD-10", summary.get('icd10_code', 'N/A'))
            
            # Diagnosis details
            if 'steps' in result and 'symptom_analysis' in result['steps']:
                diagnosis_result = result['steps']['symptom_analysis'].get('result', {})
                
                st.markdown("**Differential Diagnoses**")
                for i, dx in enumerate(diagnosis_result.get('diagnoses', [])[:3]):
                    with st.expander(f"Diagnosis {i+1}: {dx.get('name')} ({dx.get('confidence', 0)*100:.0f}%)"):
                        st.write(f"**ICD-10:** {dx.get('icd10_code')}")
                        st.write(f"**Urgency:** {dx.get('urgency')}")
                        st.write(f"**Reasoning:** {dx.get('reasoning')}")
            
            # Treatment plan
            if 'steps' in result and 'treatment_planning' in result['steps']:
                treatment = result['steps']['treatment_planning'].get('result', {})
                
                st.markdown("**Treatment Plan**")
                medications = treatment.get('medications', [])
                
                if medications:
                    for med in medications:
                        st.markdown(f"- **{med.get('name')}**: {med.get('dosage')} {med.get('frequency')} for {med.get('duration')}")
            
            # Safety review
            if 'steps' in result and 'safety_review' in result['steps']:
                safety = result['steps']['safety_review'].get('result', {})
                
                if safety.get('compliant'):
                    st.success("✅ Safety and compliance checks passed")
                else:
                    st.warning("⚠️ Safety concerns detected - manual review required")
            
            # Show full results
            with st.expander("View Full Results"):
                st.json(result)
        else:
            st.error(f"❌ Error: {result.get('error')}")


def show_patient_monitor():
    """Display patient monitoring page."""
    st.markdown('<p class="main-header">📊 Patient Monitoring</p>', unsafe_allow_html=True)
    
    patient_id = st.text_input("Patient ID", placeholder="P12345")
    
    st.markdown('<p class="sub-header">Vital Signs</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        heart_rate = st.number_input("Heart Rate (bpm)", min_value=0, max_value=300, value=75)
        bp_sys = st.number_input("Blood Pressure (Systolic)", min_value=0, max_value=300, value=120)
        temperature = st.number_input("Temperature (°C)", min_value=32.0, max_value=45.0, value=37.0, step=0.1)
    
    with col2:
        respiratory_rate = st.number_input("Respiratory Rate (/min)", min_value=0, max_value=100, value=16)
        bp_dia = st.number_input("Blood Pressure (Diastolic)", min_value=0, max_value=200, value=80)
        oxygen_sat = st.number_input("Oxygen Saturation (%)", min_value=0, max_value=100, value=98)
    
    if st.button("Monitor Vitals", use_container_width=True) and patient_id:
        vitals_data = {
            "patient_id": patient_id,
            "heart_rate": heart_rate,
            "blood_pressure_systolic": bp_sys,
            "blood_pressure_diastolic": bp_dia,
            "temperature": temperature,
            "respiratory_rate": respiratory_rate,
            "oxygen_saturation": oxygen_sat,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        with st.spinner("Analyzing vitals..."):
            result = make_api_request("/api/monitor/vitals", method="POST", data=vitals_data)
        
        if "error" not in result:
            status = result.get('status', 'unknown')
            
            if status == 'critical':
                st.error("🚨 CRITICAL: Immediate attention required!")
            elif status == 'warning':
                st.warning("⚠️ Warning: Abnormal values detected")
            else:
                st.success("✅ Vitals within normal range")
            
            # Display alerts
            if 'monitoring_result' in result:
                monitoring = result['monitoring_result']
                alerts = monitoring.get('alerts', [])
                
                if alerts:
                    st.markdown("**Alerts:**")
                    for alert in alerts:
                        alert_type = alert.get('type', 'routine')
                        if alert_type == 'urgent':
                            st.error(f"🚨 {alert.get('message')}")
                            st.write(f"Action: {alert.get('action_required')}")
                        else:
                            st.info(f"ℹ️ {alert.get('message')}")
            
            with st.expander("View Full Analysis"):
                st.json(result)
        else:
            st.error(f"❌ Error: {result.get('error')}")


# Sidebar navigation
with st.sidebar:
    st.markdown("## 🏥 MediChain")
    st.markdown("Multi-Agent Medical AI System")
    st.markdown("---")
    
    pages = {
        "Dashboard": "📊",
        "New Patient": "➕",
        "New Case": "📋",
        "Case Analysis": "🔬",
        "Patient Monitoring": "📊",
        "Case Search": "🔍"
    }
    
    for page, icon in pages.items():
        if st.button(f"{icon} {page}", use_container_width=True):
            st.session_state.current_page = page
            st.rerun()
    
    st.markdown("---")
    st.markdown("### System Info")
    st.markdown(f"**Environment:** Development")
    st.markdown(f"**Version:** 1.0.0")


# Main content area
current_page = st.session_state.current_page

if current_page == "Dashboard":
    show_dashboard()
elif current_page == "New Patient":
    show_new_patient()
elif current_page == "New Case":
    show_new_case()
elif current_page == "Case Analysis":
    show_case_analysis()
elif current_page == "Patient Monitoring":
    show_patient_monitor()
elif current_page == "Case Search":
    st.markdown('<p class="main-header">🔍 Case Search</p>', unsafe_allow_html=True)
    st.info("Case search functionality coming soon...")
else:
    show_dashboard()
