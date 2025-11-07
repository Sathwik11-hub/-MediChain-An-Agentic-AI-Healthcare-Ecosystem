"""
Unit tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# Mock the dependencies before importing the app
with patch('api.main.get_crew_manager'), \
     patch('api.main.get_postgres_service'), \
     patch('api.main.get_neo4j_service'):
    from api.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self):
        """Test health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'service' in data
        assert 'version' in data


class TestRootEndpoint:
    """Test root endpoint."""
    
    def test_root(self):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert 'docs' in data


class TestPatientEndpoints:
    """Test patient-related endpoints."""
    
    @patch('api.main.get_db')
    @patch('api.main.get_neo4j_service')
    def test_create_patient(self, mock_neo4j, mock_db):
        """Test patient creation."""
        # Mock database responses
        mock_db_instance = Mock()
        mock_db_instance.create_patient.return_value = "P12345"
        mock_db.return_value = mock_db_instance
        
        mock_neo4j_instance = Mock()
        mock_neo4j_instance.create_patient_node.return_value = True
        mock_neo4j.return_value = mock_neo4j_instance
        
        patient_data = {
            "patient_id": "P12345",
            "name": "Test Patient",
            "age": 30,
            "gender": "male",
            "medical_history": [],
            "allergies": [],
            "current_medications": []
        }
        
        response = client.post("/api/patients", json=patient_data)
        assert response.status_code == 200
        data = response.json()
        assert data['patient_id'] == "P12345"
        assert data['status'] == 'created'
    
    @patch('api.main.get_db')
    def test_get_patient_not_found(self, mock_db):
        """Test getting non-existent patient."""
        mock_db_instance = Mock()
        mock_db_instance.get_patient.return_value = None
        mock_db.return_value = mock_db_instance
        
        response = client.get("/api/patients/INVALID")
        assert response.status_code == 404


class TestCaseEndpoints:
    """Test case-related endpoints."""
    
    @patch('api.main.get_db')
    def test_create_case(self, mock_db):
        """Test case creation."""
        # Mock patient exists
        mock_db_instance = Mock()
        mock_db_instance.get_patient.return_value = {
            "patient_id": "P12345",
            "name": "Test Patient",
            "age": 30
        }
        mock_db_instance.create_case.return_value = "C12345"
        mock_db.return_value = mock_db_instance
        
        case_data = {
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
                "chief_complaint": "Fever",
                "onset": "3 days ago"
            }
        }
        
        response = client.post("/api/cases/create", json=case_data)
        assert response.status_code == 200
        data = response.json()
        assert 'case_id' in data
        assert data['status'] == 'created'
    
    @patch('api.main.get_db')
    def test_get_case_not_found(self, mock_db):
        """Test getting non-existent case."""
        mock_db_instance = Mock()
        mock_db_instance.get_case.return_value = None
        mock_db.return_value = mock_db_instance
        
        response = client.get("/api/cases/INVALID")
        assert response.status_code == 404
