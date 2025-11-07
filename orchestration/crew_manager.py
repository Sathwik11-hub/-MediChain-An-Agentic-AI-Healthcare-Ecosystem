"""
Crew Manager for orchestrating multi-agent workflows.
"""
from typing import Dict, Any, Optional
from loguru import logger
import uuid
from datetime import datetime

from agents import (
    get_symptom_analyzer,
    get_medical_knowledge_agent,
    get_treatment_recommender,
    get_patient_monitor,
    get_ethical_safety_agent
)
from services import get_neo4j_service, get_postgres_service


class CrewManager:
    """Manager for orchestrating AI agent workflows."""
    
    def __init__(self):
        """Initialize the crew manager."""
        # Initialize all agents
        self.symptom_analyzer = get_symptom_analyzer()
        self.medical_knowledge = get_medical_knowledge_agent()
        self.treatment_recommender = get_treatment_recommender()
        self.patient_monitor = get_patient_monitor()
        self.ethical_safety = get_ethical_safety_agent()
        
        # Initialize database services
        self.neo4j = get_neo4j_service()
        self.postgres = get_postgres_service()
        
        logger.info("Crew Manager initialized with all agents")
    
    def execute_diagnostic_workflow(
        self,
        patient_data: Dict[str, Any],
        symptoms: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the complete diagnostic workflow.
        
        Workflow steps:
        1. Symptom Analysis → Generate differential diagnosis
        2. Medical Knowledge → Validate diagnosis with research
        3. Treatment Recommendation → Generate treatment plan
        4. Ethical & Safety → Validate compliance
        5. Store results in databases
        
        Args:
            patient_data: Patient information
            symptoms: Symptom information
            
        Returns:
            Complete workflow results
        """
        case_id = str(uuid.uuid4())
        logger.info(f"Starting diagnostic workflow for case: {case_id}")
        
        workflow_results = {
            "case_id": case_id,
            "patient_id": patient_data.get('patient_id'),
            "status": "in_progress",
            "steps": {},
            "errors": [],
            "started_at": datetime.utcnow().isoformat()
        }
        
        try:
            # Step 1: Symptom Analysis
            logger.info("Step 1/5: Symptom Analysis")
            workflow_results["current_step"] = "symptom_analysis"
            
            diagnosis_result = self.symptom_analyzer.analyze(
                patient_data=patient_data,
                symptoms=symptoms
            )
            
            workflow_results["steps"]["symptom_analysis"] = {
                "status": "completed",
                "result": diagnosis_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Check if we got valid diagnoses
            if not diagnosis_result.get('diagnoses'):
                error = "No diagnoses generated"
                workflow_results["errors"].append(error)
                logger.warning(error)
                workflow_results["status"] = "failed"
                return workflow_results
            
            # Get primary diagnosis
            primary_diagnosis = diagnosis_result['diagnoses'][0]
            
            # Step 2: Medical Knowledge Research
            logger.info("Step 2/5: Medical Knowledge Research")
            workflow_results["current_step"] = "medical_research"
            
            research_result = self.medical_knowledge.validate_diagnosis(
                diagnoses=diagnosis_result['diagnoses'][:3],  # Top 3 diagnoses
                patient_data=patient_data
            )
            
            workflow_results["steps"]["medical_research"] = {
                "status": "completed",
                "result": research_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Step 3: Treatment Recommendation
            logger.info("Step 3/5: Treatment Recommendation")
            workflow_results["current_step"] = "treatment_planning"
            
            # Get research data for primary diagnosis if available
            research_data = None
            if research_result.get('validated_diagnoses'):
                research_data = research_result['validated_diagnoses'][0].get('research')
            
            treatment_plan = self.treatment_recommender.recommend(
                diagnosis=primary_diagnosis,
                patient_data=patient_data,
                research_data=research_data
            )
            
            workflow_results["steps"]["treatment_planning"] = {
                "status": "completed",
                "result": treatment_plan,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Step 4: Ethical & Safety Review
            logger.info("Step 4/5: Ethical & Safety Review")
            workflow_results["current_step"] = "safety_review"
            
            safety_review = self.ethical_safety.review(
                diagnosis=primary_diagnosis,
                treatment_plan=treatment_plan,
                patient_data=patient_data
            )
            
            workflow_results["steps"]["safety_review"] = {
                "status": "completed",
                "result": safety_review,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Check compliance
            if not safety_review.get('compliant', False):
                workflow_results["errors"].append(
                    "Safety compliance issues detected. Manual review required."
                )
                logger.warning("Safety compliance issues detected")
            
            # Step 5: Store Results
            logger.info("Step 5/5: Storing Results")
            workflow_results["current_step"] = "storing_results"
            
            self._store_results(
                case_id=case_id,
                patient_data=patient_data,
                diagnosis_result=diagnosis_result,
                treatment_plan=treatment_plan
            )
            
            workflow_results["steps"]["data_storage"] = {
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Workflow complete
            workflow_results["status"] = "completed"
            workflow_results["current_step"] = "completed"
            workflow_results["completed_at"] = datetime.utcnow().isoformat()
            
            # Summary
            workflow_results["summary"] = {
                "primary_diagnosis": primary_diagnosis.get('name'),
                "icd10_code": primary_diagnosis.get('icd10_code'),
                "confidence": primary_diagnosis.get('confidence'),
                "treatment_medications": len(treatment_plan.get('medications', [])),
                "safety_compliant": safety_review.get('compliant', False),
                "research_sources": len(research_result.get('validated_diagnoses', []))
            }
            
            logger.info(f"Diagnostic workflow completed for case: {case_id}")
            return workflow_results
            
        except Exception as e:
            logger.error(f"Error in diagnostic workflow: {e}")
            workflow_results["status"] = "failed"
            workflow_results["errors"].append(str(e))
            workflow_results["completed_at"] = datetime.utcnow().isoformat()
            return workflow_results
    
    def execute_monitoring_workflow(
        self,
        patient_id: str,
        vitals: Dict[str, Any],
        patient_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute patient monitoring workflow.
        
        Args:
            patient_id: Patient identifier
            vitals: Current vital signs
            patient_data: Optional patient information
            
        Returns:
            Monitoring results with alerts
        """
        logger.info(f"Starting monitoring workflow for patient: {patient_id}")
        
        try:
            # Get patient data if not provided
            if not patient_data:
                patient_data = self.postgres.get_patient(patient_id)
            
            # Analyze vitals
            monitoring_result = self.patient_monitor.analyze_vitals(
                patient_id=patient_id,
                vitals=vitals,
                patient_data=patient_data
            )
            
            # Check for critical alerts
            alerts = monitoring_result.get('alerts', [])
            critical_alerts = [a for a in alerts if a.get('type') == 'urgent']
            
            return {
                "patient_id": patient_id,
                "status": monitoring_result.get('status'),
                "monitoring_result": monitoring_result,
                "critical_alerts_count": len(critical_alerts),
                "requires_immediate_attention": len(critical_alerts) > 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in monitoring workflow: {e}")
            return {
                "patient_id": patient_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _store_results(
        self,
        case_id: str,
        patient_data: Dict[str, Any],
        diagnosis_result: Dict[str, Any],
        treatment_plan: Dict[str, Any]
    ) -> None:
        """Store workflow results in databases."""
        try:
            patient_id = patient_data.get('patient_id')
            
            # Store in PostgreSQL
            case_data = {
                "case_id": case_id,
                "patient_id": patient_id,
                "symptoms": {},  # Would include actual symptoms
                "diagnosis": diagnosis_result,
                "treatment_plan": treatment_plan,
                "status": "completed"
            }
            
            self.postgres.create_case(case_data)
            
            # Store in Neo4j graph
            self.neo4j.create_case_node({
                "case_id": case_id,
                "patient_id": patient_id,
                "status": "completed"
            })
            
            # Add diagnosis to graph
            if diagnosis_result.get('diagnoses'):
                for diagnosis in diagnosis_result['diagnoses'][:3]:
                    self.neo4j.add_diagnosis(
                        case_id=case_id,
                        diagnosis={
                            "name": diagnosis.get('name', 'Unknown'),
                            "icd10_code": diagnosis.get('icd10_code', 'Unknown'),
                            "confidence": diagnosis.get('confidence', 0.0)
                        }
                    )
            
            logger.info(f"Results stored for case: {case_id}")
            
        except Exception as e:
            logger.error(f"Error storing results: {e}")
    
    def get_case_status(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        Get case status from database.
        
        Args:
            case_id: Case identifier
            
        Returns:
            Case information or None
        """
        return self.postgres.get_case(case_id)
    
    def get_patient_history(self, patient_id: str) -> Dict[str, Any]:
        """
        Get patient history from graph database.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Patient history with cases and diagnoses
        """
        history = self.neo4j.get_patient_history(patient_id)
        
        return {
            "patient_id": patient_id,
            "case_count": len(history),
            "cases": history
        }


# Singleton instance
_crew_manager = None


def get_crew_manager() -> CrewManager:
    """Get or create crew manager instance."""
    global _crew_manager
    if _crew_manager is None:
        _crew_manager = CrewManager()
    return _crew_manager
