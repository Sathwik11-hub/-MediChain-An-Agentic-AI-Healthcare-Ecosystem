"""
Treatment Recommendation Agent.
"""
import json
from typing import Dict, Any, List
from loguru import logger
from crewai import Agent, Task

from services.llm_service import get_llm_service
from config.prompts import TREATMENT_PROMPT


class TreatmentRecommenderAgent:
    """Agent for generating evidence-based treatment plans."""
    
    def __init__(self):
        """Initialize the treatment recommender agent."""
        self.llm_service = get_llm_service()
        self.agent = self._create_agent()
        logger.info("Treatment Recommender Agent initialized")
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent."""
        return Agent(
            role="Clinical Treatment Specialist",
            goal="Generate safe, evidence-based treatment plans tailored to individual patients",
            backstory="""You are a clinical pharmacologist and treatment specialist with 
            extensive experience in personalized medicine. You excel at creating comprehensive 
            treatment plans that consider patient-specific factors, contraindications, and 
            evidence-based guidelines.""",
            verbose=True,
            allow_delegation=False
        )
    
    def recommend(
        self,
        diagnosis: Dict[str, Any],
        patient_data: Dict[str, Any],
        research_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate treatment recommendations.
        
        Args:
            diagnosis: Primary diagnosis
            patient_data: Patient information
            research_data: Optional research data to inform treatment
            
        Returns:
            Treatment plan with medications and monitoring
        """
        logger.info(f"Generating treatment plan for: {diagnosis.get('name', 'unknown')}")
        
        try:
            # Prepare patient context
            comorbidities = patient_data.get('medical_history', [])
            allergies = patient_data.get('allergies', [])
            current_meds = patient_data.get('current_medications', [])
            
            # Build prompt
            prompt = TREATMENT_PROMPT.format(
                diagnosis=diagnosis.get('name', 'Unknown'),
                age=patient_data.get('age', 'unknown'),
                allergies=", ".join(allergies) if allergies else "None",
                comorbidities=", ".join(comorbidities) if comorbidities else "None",
                current_medications=", ".join(current_meds) if current_meds else "None"
            )
            
            # Add research context if available
            if research_data and 'recommendations' in research_data:
                recommendations_text = "\n".join(research_data['recommendations'])
                prompt += f"\n\nEvidence-Based Recommendations:\n{recommendations_text}"
            
            # Add safety warnings
            prompt += f"\n\nIMPORTANT: Consider the following contraindications:"
            if allergies:
                prompt += f"\n- Patient is allergic to: {', '.join(allergies)}"
            if "pregnancy" in str(comorbidities).lower() or "pregnant" in str(comorbidities).lower():
                prompt += "\n- Patient may be pregnant - avoid teratogenic medications"
            
            # Generate treatment plan
            response = self.llm_service.generate_response(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for safer recommendations
                json_mode=True
            )
            
            # Parse response
            result = json.loads(response)
            
            # Validate medications against allergies
            result = self._validate_medications(result, allergies)
            
            logger.info(f"Generated treatment plan with {len(result.get('medications', []))} medications")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing treatment response: {e}")
            return {
                "medications": [],
                "non_pharmacological": [],
                "monitoring": {
                    "vital_signs": [],
                    "lab_tests": [],
                    "frequency": "unknown"
                },
                "follow_up": "Consult healthcare provider",
                "patient_education": [],
                "error": "Failed to parse treatment response"
            }
        except Exception as e:
            logger.error(f"Error generating treatment plan: {e}")
            return {
                "medications": [],
                "non_pharmacological": [],
                "monitoring": {
                    "vital_signs": [],
                    "lab_tests": [],
                    "frequency": "unknown"
                },
                "follow_up": "Consult healthcare provider",
                "patient_education": [],
                "error": str(e)
            }
    
    def _validate_medications(
        self,
        treatment_plan: Dict[str, Any],
        allergies: List[str]
    ) -> Dict[str, Any]:
        """
        Validate medications against patient allergies.
        
        Args:
            treatment_plan: Treatment plan to validate
            allergies: List of patient allergies
            
        Returns:
            Validated treatment plan with warnings
        """
        if not allergies or 'medications' not in treatment_plan:
            return treatment_plan
        
        # Check each medication
        warnings = []
        for med in treatment_plan.get('medications', []):
            med_name = med.get('name', '').lower()
            
            for allergy in allergies:
                allergy_lower = allergy.lower()
                # Simple check - in production, use drug database
                if allergy_lower in med_name or med_name in allergy_lower:
                    warning = f"WARNING: {med['name']} may be contraindicated due to {allergy} allergy"
                    warnings.append(warning)
                    if 'precautions' not in med:
                        med['precautions'] = []
                    med['precautions'].insert(0, warning)
        
        if warnings:
            treatment_plan['allergy_warnings'] = warnings
            logger.warning(f"Allergy warnings generated: {len(warnings)}")
        
        return treatment_plan
    
    def create_task(
        self,
        diagnosis: Dict[str, Any],
        patient_data: Dict[str, Any],
        research_data: Optional[Dict[str, Any]] = None
    ) -> Task:
        """
        Create a CrewAI task for treatment recommendation.
        
        Args:
            diagnosis: Diagnosis information
            patient_data: Patient information
            research_data: Optional research context
            
        Returns:
            CrewAI Task
        """
        description = f"""
        Generate a comprehensive, evidence-based treatment plan for:
        
        Diagnosis: {diagnosis.get('name', 'Unknown')} (ICD-10: {diagnosis.get('icd10_code', 'Unknown')})
        Confidence: {diagnosis.get('confidence', 0) * 100:.1f}%
        
        Patient: {patient_data.get('name', 'Unknown')}
        Age: {patient_data.get('age', 'Unknown')}
        Gender: {patient_data.get('gender', 'Unknown')}
        Medical History: {', '.join(patient_data.get('medical_history', []))}
        Allergies: {', '.join(patient_data.get('allergies', [])) or 'None'}
        Current Medications: {', '.join(patient_data.get('current_medications', [])) or 'None'}
        
        Generate a treatment plan that includes:
        1. Medications with dosage, frequency, duration, and precautions
        2. Non-pharmacological interventions
        3. Monitoring plan (vital signs, lab tests, frequency)
        4. Follow-up schedule
        5. Patient education points
        
        CRITICAL: Avoid medications that may interact with allergies or current medications.
        """
        
        return Task(
            description=description,
            agent=self.agent,
            expected_output="JSON formatted treatment plan with medications and monitoring"
        )


# Singleton instance
_treatment_recommender = None


def get_treatment_recommender() -> TreatmentRecommenderAgent:
    """Get or create treatment recommender instance."""
    global _treatment_recommender
    if _treatment_recommender is None:
        _treatment_recommender = TreatmentRecommenderAgent()
    return _treatment_recommender
