"""
Database services for Neo4j and PostgreSQL.
"""
from typing import Dict, Any, List, Optional
from loguru import logger
from neo4j import GraphDatabase
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from config.settings import settings


Base = declarative_base()


class PatientRecord(Base):
    """SQLAlchemy model for patient records."""
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    age = Column(Integer)
    gender = Column(String(20))
    medical_history = Column(JSON)
    allergies = Column(JSON)
    current_medications = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CaseRecord(Base):
    """SQLAlchemy model for medical cases."""
    __tablename__ = 'cases'
    
    id = Column(Integer, primary_key=True)
    case_id = Column(String(50), unique=True, nullable=False)
    patient_id = Column(String(50), nullable=False)
    symptoms = Column(JSON)
    diagnosis = Column(JSON)
    treatment_plan = Column(JSON)
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Neo4jService:
    """Service for Neo4j graph database operations."""
    
    def __init__(self):
        """Initialize Neo4j connection."""
        try:
            self.driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password)
            )
            logger.info("Connected to Neo4j")
            self._create_constraints()
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self.driver = None
    
    def _create_constraints(self) -> None:
        """Create database constraints and indexes."""
        if not self.driver:
            return
        
        constraints = [
            "CREATE CONSTRAINT patient_id IF NOT EXISTS FOR (p:Patient) REQUIRE p.patient_id IS UNIQUE",
            "CREATE CONSTRAINT case_id IF NOT EXISTS FOR (c:Case) REQUIRE c.case_id IS UNIQUE",
            "CREATE INDEX patient_name IF NOT EXISTS FOR (p:Patient) ON (p.name)"
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    logger.debug(f"Constraint creation: {e}")
    
    def create_patient_node(self, patient_data: Dict[str, Any]) -> bool:
        """
        Create a patient node in the graph.
        
        Args:
            patient_data: Patient information
            
        Returns:
            Success status
        """
        if not self.driver:
            return False
        
        query = """
        MERGE (p:Patient {patient_id: $patient_id})
        SET p.name = $name,
            p.age = $age,
            p.gender = $gender,
            p.created_at = datetime()
        RETURN p
        """
        
        try:
            with self.driver.session() as session:
                session.run(query, **patient_data)
            logger.info(f"Created patient node: {patient_data['patient_id']}")
            return True
        except Exception as e:
            logger.error(f"Error creating patient node: {e}")
            return False
    
    def create_case_node(self, case_data: Dict[str, Any]) -> bool:
        """
        Create a case node and link to patient.
        
        Args:
            case_data: Case information
            
        Returns:
            Success status
        """
        if not self.driver:
            return False
        
        query = """
        MATCH (p:Patient {patient_id: $patient_id})
        CREATE (c:Case {
            case_id: $case_id,
            status: $status,
            created_at: datetime()
        })
        CREATE (p)-[:HAS_CASE]->(c)
        RETURN c
        """
        
        try:
            with self.driver.session() as session:
                session.run(query, **case_data)
            logger.info(f"Created case node: {case_data['case_id']}")
            return True
        except Exception as e:
            logger.error(f"Error creating case node: {e}")
            return False
    
    def add_diagnosis(self, case_id: str, diagnosis: Dict[str, Any]) -> bool:
        """
        Add diagnosis to a case.
        
        Args:
            case_id: Case identifier
            diagnosis: Diagnosis information
            
        Returns:
            Success status
        """
        if not self.driver:
            return False
        
        query = """
        MATCH (c:Case {case_id: $case_id})
        CREATE (d:Diagnosis {
            name: $name,
            icd10_code: $icd10_code,
            confidence: $confidence,
            created_at: datetime()
        })
        CREATE (c)-[:HAS_DIAGNOSIS]->(d)
        RETURN d
        """
        
        try:
            with self.driver.session() as session:
                session.run(query, case_id=case_id, **diagnosis)
            logger.info(f"Added diagnosis to case: {case_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding diagnosis: {e}")
            return False
    
    def get_patient_history(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get patient's medical history from graph.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            List of cases with diagnoses
        """
        if not self.driver:
            return []
        
        query = """
        MATCH (p:Patient {patient_id: $patient_id})-[:HAS_CASE]->(c:Case)
        OPTIONAL MATCH (c)-[:HAS_DIAGNOSIS]->(d:Diagnosis)
        RETURN c.case_id as case_id, c.status as status, 
               collect(d.name) as diagnoses, c.created_at as created_at
        ORDER BY c.created_at DESC
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, patient_id=patient_id)
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Error getting patient history: {e}")
            return []
    
    def close(self) -> None:
        """Close database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")


class PostgresService:
    """Service for PostgreSQL database operations."""
    
    def __init__(self):
        """Initialize PostgreSQL connection."""
        try:
            self.engine = create_engine(settings.postgres_uri)
            Base.metadata.create_all(self.engine)
            self.SessionLocal = sessionmaker(bind=self.engine)
            logger.info("Connected to PostgreSQL")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            self.engine = None
            self.SessionLocal = None
    
    def create_patient(self, patient_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a patient record.
        
        Args:
            patient_data: Patient information
            
        Returns:
            Patient ID or None
        """
        if not self.SessionLocal:
            return None
        
        session = self.SessionLocal()
        try:
            patient = PatientRecord(**patient_data)
            session.add(patient)
            session.commit()
            patient_id = patient.patient_id
            logger.info(f"Created patient: {patient_id}")
            return patient_id
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating patient: {e}")
            return None
        finally:
            session.close()
    
    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get patient by ID.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Patient data or None
        """
        if not self.SessionLocal:
            return None
        
        session = self.SessionLocal()
        try:
            patient = session.query(PatientRecord).filter_by(patient_id=patient_id).first()
            if patient:
                return {
                    'patient_id': patient.patient_id,
                    'name': patient.name,
                    'age': patient.age,
                    'gender': patient.gender,
                    'medical_history': patient.medical_history,
                    'allergies': patient.allergies,
                    'current_medications': patient.current_medications
                }
            return None
        except Exception as e:
            logger.error(f"Error getting patient: {e}")
            return None
        finally:
            session.close()
    
    def create_case(self, case_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a case record.
        
        Args:
            case_data: Case information
            
        Returns:
            Case ID or None
        """
        if not self.SessionLocal:
            return None
        
        session = self.SessionLocal()
        try:
            case = CaseRecord(**case_data)
            session.add(case)
            session.commit()
            case_id = case.case_id
            logger.info(f"Created case: {case_id}")
            return case_id
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating case: {e}")
            return None
        finally:
            session.close()
    
    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        Get case by ID.
        
        Args:
            case_id: Case identifier
            
        Returns:
            Case data or None
        """
        if not self.SessionLocal:
            return None
        
        session = self.SessionLocal()
        try:
            case = session.query(CaseRecord).filter_by(case_id=case_id).first()
            if case:
                return {
                    'case_id': case.case_id,
                    'patient_id': case.patient_id,
                    'symptoms': case.symptoms,
                    'diagnosis': case.diagnosis,
                    'treatment_plan': case.treatment_plan,
                    'status': case.status,
                    'created_at': case.created_at.isoformat() if case.created_at else None
                }
            return None
        except Exception as e:
            logger.error(f"Error getting case: {e}")
            return None
        finally:
            session.close()
    
    def update_case(self, case_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update case information.
        
        Args:
            case_id: Case identifier
            updates: Fields to update
            
        Returns:
            Success status
        """
        if not self.SessionLocal:
            return False
        
        session = self.SessionLocal()
        try:
            case = session.query(CaseRecord).filter_by(case_id=case_id).first()
            if case:
                for key, value in updates.items():
                    if hasattr(case, key):
                        setattr(case, key, value)
                case.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"Updated case: {case_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating case: {e}")
            return False
        finally:
            session.close()


# Singleton instances
_neo4j_service = None
_postgres_service = None


def get_neo4j_service() -> Neo4jService:
    """Get or create Neo4j service instance."""
    global _neo4j_service
    if _neo4j_service is None:
        _neo4j_service = Neo4jService()
    return _neo4j_service


def get_postgres_service() -> PostgresService:
    """Get or create PostgreSQL service instance."""
    global _postgres_service
    if _postgres_service is None:
        _postgres_service = PostgresService()
    return _postgres_service
