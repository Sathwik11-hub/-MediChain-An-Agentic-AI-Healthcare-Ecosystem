"""
Unit tests for Pydantic models.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from models.patient import (
    Patient, Symptom, Symptoms, Diagnosis, Medication,
    TreatmentPlan, VitalSigns, Gender, CaseStatus
)


class TestPatientModel:
    """Test Patient model."""
    
    def test_valid_patient(self):
        """Test creating a valid patient."""
        patient = Patient(
            patient_id="P12345",
            name="John Doe",
            age=45,
            gender=Gender.MALE,
            medical_history=["Hypertension"],
            allergies=["Penicillin"],
            current_medications=["Lisinopril"]
        )
        
        assert patient.patient_id == "P12345"
        assert patient.name == "John Doe"
        assert patient.age == 45
        assert patient.gender == Gender.MALE
    
    def test_invalid_age(self):
        """Test patient with invalid age."""
        with pytest.raises(ValidationError):
            Patient(
                patient_id="P12345",
                name="John Doe",
                age=200,  # Invalid age
                gender=Gender.MALE
            )


class TestSymptomModel:
    """Test Symptom model."""
    
    def test_valid_symptom(self):
        """Test creating a valid symptom."""
        symptom = Symptom(
            name="Fever",
            severity=7,
            duration_days=3,
            description="High fever with chills"
        )
        
        assert symptom.name == "Fever"
        assert symptom.severity == 7
        assert symptom.duration_days == 3
    
    def test_invalid_severity(self):
        """Test symptom with invalid severity."""
        with pytest.raises(ValidationError):
            Symptom(
                name="Fever",
                severity=15,  # Invalid (must be 1-10)
                duration_days=3
            )


class TestDiagnosisModel:
    """Test Diagnosis model."""
    
    def test_valid_diagnosis(self):
        """Test creating a valid diagnosis."""
        diagnosis = Diagnosis(
            name="Influenza",
            icd10_code="J11.1",
            confidence=0.85,
            reasoning="Patient presents with fever and cough",
            urgency="medium"
        )
        
        assert diagnosis.name == "Influenza"
        assert diagnosis.icd10_code == "J11.1"
        assert diagnosis.confidence == 0.85
    
    def test_invalid_confidence(self):
        """Test diagnosis with invalid confidence."""
        with pytest.raises(ValidationError):
            Diagnosis(
                name="Influenza",
                icd10_code="J11.1",
                confidence=1.5,  # Invalid (must be 0-1)
                reasoning="Test",
                urgency="medium"
            )


class TestVitalSignsModel:
    """Test VitalSigns model."""
    
    def test_valid_vitals(self):
        """Test creating valid vital signs."""
        vitals = VitalSigns(
            patient_id="P12345",
            heart_rate=75,
            blood_pressure_systolic=120,
            blood_pressure_diastolic=80,
            temperature=37.0,
            respiratory_rate=16,
            oxygen_saturation=98
        )
        
        assert vitals.patient_id == "P12345"
        assert vitals.heart_rate == 75
        assert vitals.temperature == 37.0
    
    def test_invalid_heart_rate(self):
        """Test vitals with invalid heart rate."""
        with pytest.raises(ValidationError):
            VitalSigns(
                patient_id="P12345",
                heart_rate=500,  # Invalid
                temperature=37.0
            )
