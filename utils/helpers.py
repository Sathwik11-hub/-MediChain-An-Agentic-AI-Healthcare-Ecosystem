"""Utility functions."""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional


def generate_patient_id() -> str:
    """Generate a unique patient ID."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_suffix = secrets.token_hex(3).upper()
    return f"P{timestamp}{random_suffix}"


def generate_case_id() -> str:
    """Generate a unique case ID."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_suffix = secrets.token_hex(3).upper()
    return f"C{timestamp}{random_suffix}"


def hash_patient_id(patient_id: str) -> str:
    """Hash patient ID for anonymization."""
    return hashlib.sha256(patient_id.encode()).hexdigest()


def calculate_age_from_dob(dob: datetime) -> int:
    """Calculate age from date of birth."""
    today = datetime.utcnow()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age


def is_adult(age: int) -> bool:
    """Check if patient is an adult (>= 18 years)."""
    return age >= 18


def is_pediatric(age: int) -> bool:
    """Check if patient is pediatric (< 18 years)."""
    return age < 18


def is_geriatric(age: int) -> bool:
    """Check if patient is geriatric (>= 65 years)."""
    return age >= 65


def format_vital_signs(vitals: dict) -> str:
    """Format vital signs for display."""
    parts = []
    
    if vitals.get('heart_rate'):
        parts.append(f"HR: {vitals['heart_rate']} bpm")
    if vitals.get('blood_pressure_systolic') and vitals.get('blood_pressure_diastolic'):
        parts.append(f"BP: {vitals['blood_pressure_systolic']}/{vitals['blood_pressure_diastolic']} mmHg")
    if vitals.get('temperature'):
        parts.append(f"Temp: {vitals['temperature']}°C")
    if vitals.get('respiratory_rate'):
        parts.append(f"RR: {vitals['respiratory_rate']}/min")
    if vitals.get('oxygen_saturation'):
        parts.append(f"SpO2: {vitals['oxygen_saturation']}%")
    
    return " | ".join(parts) if parts else "No vitals recorded"
