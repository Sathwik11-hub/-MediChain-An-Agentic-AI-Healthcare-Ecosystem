"""
Pydantic models for data validation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class Gender(str, Enum):
    """Gender enumeration."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class CaseStatus(str, Enum):
    """Case status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"


class Urgency(str, Enum):
    """Urgency level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Patient(BaseModel):
    """Patient model."""
    patient_id: str = Field(..., description="Unique patient identifier")
    name: str = Field(..., description="Patient full name")
    age: int = Field(..., ge=0, le=150, description="Patient age")
    gender: Gender = Field(..., description="Patient gender")
    medical_history: List[str] = Field(default=[], description="Medical history")
    allergies: List[str] = Field(default=[], description="Known allergies")
    current_medications: List[str] = Field(default=[], description="Current medications")
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "P12345",
                "name": "John Doe",
                "age": 45,
                "gender": "male",
                "medical_history": ["Hypertension", "Type 2 Diabetes"],
                "allergies": ["Penicillin"],
                "current_medications": ["Metformin", "Lisinopril"]
            }
        }


class Symptom(BaseModel):
    """Symptom model."""
    name: str = Field(..., description="Symptom name")
    severity: int = Field(..., ge=1, le=10, description="Severity (1-10)")
    duration_days: int = Field(..., ge=0, description="Duration in days")
    description: Optional[str] = Field(None, description="Additional details")


class Symptoms(BaseModel):
    """Collection of symptoms."""
    symptoms: List[Symptom] = Field(..., description="List of symptoms")
    chief_complaint: str = Field(..., description="Main complaint")
    onset: str = Field(..., description="When symptoms started")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symptoms": [
                    {
                        "name": "Fever",
                        "severity": 7,
                        "duration_days": 3,
                        "description": "High fever with chills"
                    },
                    {
                        "name": "Cough",
                        "severity": 5,
                        "duration_days": 3,
                        "description": "Dry cough"
                    }
                ],
                "chief_complaint": "Fever and cough",
                "onset": "3 days ago"
            }
        }


class Diagnosis(BaseModel):
    """Diagnosis model."""
    name: str = Field(..., description="Diagnosis name")
    icd10_code: str = Field(..., description="ICD-10 code")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reasoning: str = Field(..., description="Reasoning for diagnosis")
    urgency: Urgency = Field(..., description="Urgency level")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Influenza",
                "icd10_code": "J11.1",
                "confidence": 0.85,
                "reasoning": "Patient presents with fever, cough, and fatigue consistent with influenza",
                "urgency": "medium"
            }
        }


class DiagnosisResult(BaseModel):
    """Diagnosis result from symptom analyzer."""
    diagnoses: List[Diagnosis] = Field(..., description="List of possible diagnoses")
    recommended_tests: List[str] = Field(default=[], description="Recommended tests")
    red_flags: List[str] = Field(default=[], description="Warning signs")


class Medication(BaseModel):
    """Medication model."""
    name: str = Field(..., description="Medication name")
    dosage: str = Field(..., description="Dosage information")
    frequency: str = Field(..., description="How often to take")
    duration: str = Field(..., description="Treatment duration")
    route: str = Field(..., description="Route of administration")
    precautions: List[str] = Field(default=[], description="Precautions")


class Monitoring(BaseModel):
    """Monitoring plan model."""
    vital_signs: List[str] = Field(..., description="Vital signs to monitor")
    lab_tests: List[str] = Field(default=[], description="Lab tests to perform")
    frequency: str = Field(..., description="Monitoring frequency")


class TreatmentPlan(BaseModel):
    """Treatment plan model."""
    medications: List[Medication] = Field(..., description="Prescribed medications")
    non_pharmacological: List[str] = Field(default=[], description="Non-drug interventions")
    monitoring: Monitoring = Field(..., description="Monitoring plan")
    follow_up: str = Field(..., description="Follow-up schedule")
    patient_education: List[str] = Field(default=[], description="Patient education points")
    
    class Config:
        json_schema_extra = {
            "example": {
                "medications": [
                    {
                        "name": "Oseltamivir",
                        "dosage": "75mg",
                        "frequency": "Twice daily",
                        "duration": "5 days",
                        "route": "oral",
                        "precautions": ["Take with food"]
                    }
                ],
                "non_pharmacological": ["Rest", "Increase fluid intake"],
                "monitoring": {
                    "vital_signs": ["Temperature", "Heart rate"],
                    "lab_tests": [],
                    "frequency": "Daily"
                },
                "follow_up": "7 days or if symptoms worsen",
                "patient_education": ["Stay home to prevent spread", "Cover coughs"]
            }
        }


class VitalSigns(BaseModel):
    """Vital signs model."""
    patient_id: str = Field(..., description="Patient identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Reading timestamp")
    heart_rate: Optional[int] = Field(None, ge=0, le=300, description="Heart rate (bpm)")
    blood_pressure_systolic: Optional[int] = Field(None, ge=0, le=300, description="Systolic BP")
    blood_pressure_diastolic: Optional[int] = Field(None, ge=0, le=200, description="Diastolic BP")
    temperature: Optional[float] = Field(None, ge=32.0, le=45.0, description="Temperature (C)")
    respiratory_rate: Optional[int] = Field(None, ge=0, le=100, description="Respiratory rate")
    oxygen_saturation: Optional[int] = Field(None, ge=0, le=100, description="O2 saturation (%)")


class MedicalSource(BaseModel):
    """Medical literature source."""
    title: str = Field(..., description="Publication title")
    authors: Optional[str] = Field(None, description="Authors")
    year: Optional[int] = Field(None, description="Publication year")
    url: str = Field(..., description="URL to source")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    key_findings: Optional[str] = Field(None, description="Key findings")


class CaseCreate(BaseModel):
    """Model for creating a new case."""
    patient_id: str = Field(..., description="Patient identifier")
    symptoms: Symptoms = Field(..., description="Patient symptoms")
    
    class Config:
        json_schema_extra = {
            "example": {
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
        }


class CaseResponse(BaseModel):
    """Model for case response."""
    case_id: str = Field(..., description="Case identifier")
    patient_id: str = Field(..., description="Patient identifier")
    status: CaseStatus = Field(..., description="Case status")
    symptoms: Optional[Dict[str, Any]] = Field(None, description="Symptoms")
    diagnosis: Optional[Dict[str, Any]] = Field(None, description="Diagnosis result")
    treatment_plan: Optional[Dict[str, Any]] = Field(None, description="Treatment plan")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class WorkflowStatus(BaseModel):
    """Workflow execution status."""
    case_id: str = Field(..., description="Case identifier")
    status: str = Field(..., description="Current status")
    current_step: str = Field(..., description="Current workflow step")
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    results: Dict[str, Any] = Field(default={}, description="Results from each step")
    errors: List[str] = Field(default=[], description="Any errors encountered")


class EthicsReview(BaseModel):
    """Ethics and safety review result."""
    compliant: bool = Field(..., description="Overall compliance status")
    hipaa_compliance: Dict[str, Any] = Field(..., description="HIPAA compliance check")
    fda_compliance: Dict[str, Any] = Field(..., description="FDA compliance check")
    ethical_concerns: List[str] = Field(default=[], description="Ethical concerns")
    recommendations: List[str] = Field(default=[], description="Recommendations")
    risk_level: str = Field(..., description="Risk level assessment")
