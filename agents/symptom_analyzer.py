"""
Symptom Analyzer Agent using CrewAI.
"""
import json
from typing import Dict, Any
from loguru import logger
from crewai import Agent, Task, Crew
from langchain.tools import Tool

from services.llm_service import get_llm_service
from services.rag_service import get_rag_service
from config.prompts import SYMPTOM_ANALYSIS_PROMPT


class SymptomAnalyzerAgent:
    """Agent for analyzing symptoms and generating differential diagnoses."""
    
    def __init__(self):
        """Initialize the symptom analyzer agent."""
        self.llm_service = get_llm_service()
        self.rag_service = get_rag_service()
        self.agent = self._create_agent()
        logger.info("Symptom Analyzer Agent initialized")
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent."""
        return Agent(
            role="Medical Symptom Analysis Specialist",
            goal="Analyze patient symptoms and generate accurate differential diagnoses with ICD-10 codes",
            backstory="""You are an experienced medical diagnostician with over 20 years 
            of clinical experience. You excel at analyzing complex symptom patterns and 
            generating comprehensive differential diagnoses based on evidence-based medicine.""",
            verbose=True,
            allow_delegation=False
        )
    
    def _get_medical_context(self, symptoms: Dict[str, Any]) -> str:
        """Retrieve relevant medical context from RAG."""
        try:
            # Build query from symptoms
            symptom_names = [s.get('name', '') for s in symptoms.get('symptoms', [])]
            query = f"Differential diagnosis for: {', '.join(symptom_names)}"
            
            # Get context from RAG
            context = self.rag_service.get_relevant_context(
                query=query,
                include_pubmed=True,
                top_k=3
            )
            
            return json.dumps(context, indent=2)
        except Exception as e:
            logger.warning(f"Error retrieving medical context: {e}")
            return "{}"
    
    def analyze(self, patient_data: Dict[str, Any], symptoms: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze symptoms and generate differential diagnosis.
        
        Args:
            patient_data: Patient information (age, gender, history, etc.)
            symptoms: Symptom information
            
        Returns:
            Diagnosis results with ICD-10 codes
        """
        logger.info(f"Analyzing symptoms for patient: {patient_data.get('patient_id', 'unknown')}")
        
        try:
            # Get medical context
            medical_context = self._get_medical_context(symptoms)
            
            # Format symptoms for prompt
            symptom_list = symptoms.get('symptoms', [])
            symptoms_text = "\n".join([
                f"- {s['name']}: Severity {s['severity']}/10, Duration {s['duration_days']} days"
                for s in symptom_list
            ])
            
            # Prepare prompt
            prompt = SYMPTOM_ANALYSIS_PROMPT.format(
                symptoms=symptoms_text,
                history=", ".join(patient_data.get('medical_history', [])),
                age=patient_data.get('age', 'unknown'),
                gender=patient_data.get('gender', 'unknown'),
                duration=symptoms.get('onset', 'unknown')
            )
            
            # Add medical context
            prompt += f"\n\nRelevant Medical Literature:\n{medical_context}"
            
            # Generate response
            response = self.llm_service.generate_response(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for more consistent medical analysis
                json_mode=True
            )
            
            # Parse response
            result = json.loads(response)
            logger.info(f"Generated {len(result.get('diagnoses', []))} differential diagnoses")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing diagnosis response: {e}")
            # Return fallback response
            return {
                "diagnoses": [],
                "recommended_tests": [],
                "red_flags": [],
                "error": "Failed to parse diagnosis response"
            }
        except Exception as e:
            logger.error(f"Error analyzing symptoms: {e}")
            return {
                "diagnoses": [],
                "recommended_tests": [],
                "red_flags": [],
                "error": str(e)
            }
    
    def create_task(self, patient_data: Dict[str, Any], symptoms: Dict[str, Any]) -> Task:
        """
        Create a CrewAI task for symptom analysis.
        
        Args:
            patient_data: Patient information
            symptoms: Symptom information
            
        Returns:
            CrewAI Task
        """
        description = f"""
        Analyze the following patient symptoms and generate a differential diagnosis:
        
        Patient: {patient_data.get('name', 'Unknown')}
        Age: {patient_data.get('age', 'Unknown')}
        Gender: {patient_data.get('gender', 'Unknown')}
        Medical History: {', '.join(patient_data.get('medical_history', []))}
        Allergies: {', '.join(patient_data.get('allergies', []))}
        
        Symptoms:
        {json.dumps(symptoms, indent=2)}
        
        Generate a comprehensive differential diagnosis with:
        1. At least 3 possible diagnoses with ICD-10 codes
        2. Confidence scores for each diagnosis
        3. Recommended diagnostic tests
        4. Red flags that require immediate attention
        """
        
        return Task(
            description=description,
            agent=self.agent,
            expected_output="JSON formatted differential diagnosis with ICD-10 codes"
        )


# Singleton instance
_symptom_analyzer = None


def get_symptom_analyzer() -> SymptomAnalyzerAgent:
    """Get or create symptom analyzer instance."""
    global _symptom_analyzer
    if _symptom_analyzer is None:
        _symptom_analyzer = SymptomAnalyzerAgent()
    return _symptom_analyzer
