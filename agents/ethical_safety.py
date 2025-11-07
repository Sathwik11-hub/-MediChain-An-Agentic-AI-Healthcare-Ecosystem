"""
Ethical and Safety Agent.
"""
import json
from typing import Dict, Any, List
from loguru import logger
from crewai import Agent, Task

from services.llm_service import get_llm_service
from config.prompts import ETHICAL_SAFETY_PROMPT


class EthicalSafetyAgent:
    """Agent for ethical and safety compliance validation."""
    
    def __init__(self):
        """Initialize the ethical safety agent."""
        self.llm_service = get_llm_service()
        self.agent = self._create_agent()
        
        # FDA approved medication list (simplified - in production use comprehensive database)
        self.fda_approved_drugs = self._load_fda_approved_drugs()
        
        logger.info("Ethical Safety Agent initialized")
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent."""
        return Agent(
            role="Medical Ethics and Safety Officer",
            goal="Ensure all medical decisions comply with HIPAA, FDA regulations, and medical ethics guidelines",
            backstory="""You are a medical ethics officer and regulatory compliance specialist 
            with expertise in HIPAA, FDA regulations, and medical ethics. You ensure all clinical 
            decisions meet the highest standards of safety, privacy, and ethical practice.""",
            verbose=True,
            allow_delegation=False
        )
    
    def _load_fda_approved_drugs(self) -> set:
        """Load FDA approved drug list (simplified)."""
        # In production, this would load from a comprehensive database
        return {
            "acetaminophen", "ibuprofen", "aspirin", "amoxicillin", 
            "metformin", "lisinopril", "atorvastatin", "omeprazole",
            "levothyroxine", "albuterol", "oseltamivir", "azithromycin"
        }
    
    def review(
        self,
        diagnosis: Dict[str, Any],
        treatment_plan: Dict[str, Any],
        patient_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Review case for ethical and safety compliance.
        
        Args:
            diagnosis: Diagnosis information
            treatment_plan: Proposed treatment plan
            patient_data: Patient information (for privacy review)
            
        Returns:
            Compliance review results
        """
        logger.info("Conducting ethical and safety review")
        
        try:
            # Prepare review context
            demographics = {
                "age": patient_data.get('age', 'unknown'),
                "gender": patient_data.get('gender', 'unknown'),
                "has_medical_history": bool(patient_data.get('medical_history'))
            }
            
            # Build prompt
            prompt = ETHICAL_SAFETY_PROMPT.format(
                diagnosis=json.dumps(diagnosis, indent=2),
                treatment_plan=json.dumps(treatment_plan, indent=2),
                demographics=json.dumps(demographics, indent=2),
                privacy_concerns="Standard HIPAA compliance required"
            )
            
            # Generate review
            response = self.llm_service.generate_response(
                prompt=prompt,
                temperature=0.1,  # Very low temperature for consistent compliance checks
                json_mode=True
            )
            
            # Parse response
            result = json.loads(response)
            
            # Add rule-based compliance checks
            result = self._add_rule_based_checks(result, diagnosis, treatment_plan, patient_data)
            
            logger.info(f"Review complete. Compliant: {result.get('compliant', False)}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing safety review response: {e}")
            return {
                "compliant": False,
                "hipaa_compliance": {"passed": False, "issues": ["Failed to parse response"]},
                "fda_compliance": {"passed": False, "unapproved_medications": []},
                "ethical_concerns": ["Review failed"],
                "recommendations": ["Manual review required"],
                "risk_level": "high",
                "error": "Failed to parse safety review response"
            }
        except Exception as e:
            logger.error(f"Error during safety review: {e}")
            return {
                "compliant": False,
                "hipaa_compliance": {"passed": False, "issues": [str(e)]},
                "fda_compliance": {"passed": False, "unapproved_medications": []},
                "ethical_concerns": [str(e)],
                "recommendations": ["Manual review required"],
                "risk_level": "high",
                "error": str(e)
            }
    
    def _add_rule_based_checks(
        self,
        result: Dict[str, Any],
        diagnosis: Dict[str, Any],
        treatment_plan: Dict[str, Any],
        patient_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add rule-based compliance checks."""
        
        # FDA compliance check
        fda_issues = []
        unapproved = []
        
        medications = treatment_plan.get('medications', [])
        for med in medications:
            med_name = med.get('name', '').lower()
            # Simplified check - in production use comprehensive drug database
            if med_name not in self.fda_approved_drugs:
                unapproved.append(med['name'])
                fda_issues.append(f"Medication '{med['name']}' needs FDA approval verification")
        
        if 'fda_compliance' not in result:
            result['fda_compliance'] = {}
        
        result['fda_compliance']['unapproved_medications'] = unapproved
        if unapproved:
            result['fda_compliance']['passed'] = False
            if 'issues' not in result['fda_compliance']:
                result['fda_compliance']['issues'] = []
            result['fda_compliance']['issues'].extend(fda_issues)
        
        # HIPAA compliance check
        hipaa_issues = []
        
        # Check for PII handling
        if 'patient_id' in patient_data:
            # In production, verify PII is properly encrypted and handled
            pass
        
        # Check consent
        if not patient_data.get('consent_obtained', False):
            hipaa_issues.append("Patient consent documentation should be verified")
        
        if 'hipaa_compliance' not in result:
            result['hipaa_compliance'] = {}
        
        if hipaa_issues:
            if 'issues' not in result['hipaa_compliance']:
                result['hipaa_compliance']['issues'] = []
            result['hipaa_compliance']['issues'].extend(hipaa_issues)
        
        # Ethical checks
        ethical_concerns = []
        
        # Check for vulnerable populations
        age = patient_data.get('age', 0)
        if age < 18:
            ethical_concerns.append("Pediatric patient - ensure appropriate consent from guardian")
        elif age > 65:
            ethical_concerns.append("Geriatric patient - consider dose adjustments and polypharmacy risks")
        
        # Check for high-risk medications
        for med in medications:
            precautions = med.get('precautions', [])
            if any('warning' in p.lower() for p in precautions):
                ethical_concerns.append(f"High-risk medication prescribed: {med.get('name')}")
        
        if ethical_concerns:
            if 'ethical_concerns' not in result:
                result['ethical_concerns'] = []
            result['ethical_concerns'].extend(ethical_concerns)
        
        # Overall compliance determination
        has_fda_issues = not result['fda_compliance'].get('passed', True)
        has_hipaa_issues = bool(result['hipaa_compliance'].get('issues', []))
        has_ethical_issues = bool(result.get('ethical_concerns', []))
        
        result['compliant'] = not (has_fda_issues or has_hipaa_issues or has_ethical_issues)
        
        # Risk level assessment
        if has_fda_issues or has_hipaa_issues:
            result['risk_level'] = 'high'
        elif has_ethical_issues:
            result['risk_level'] = 'medium'
        else:
            result['risk_level'] = 'low'
        
        return result
    
    def validate_data_privacy(self, data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate data privacy compliance.
        
        Args:
            data: Data to validate
            
        Returns:
            Privacy validation results
        """
        validation = {
            "encrypted": True,  # In production, actually check encryption
            "anonymized": True,  # In production, check for PII
            "audit_logged": True,  # In production, verify audit logs
            "access_controlled": True  # In production, verify access controls
        }
        
        # Check for obvious PII in data
        pii_fields = ['ssn', 'social_security', 'credit_card', 'passport']
        for field in pii_fields:
            if field in str(data).lower():
                validation['anonymized'] = False
                logger.warning(f"Potential PII detected: {field}")
        
        return validation
    
    def create_task(
        self,
        diagnosis: Dict[str, Any],
        treatment_plan: Dict[str, Any],
        patient_data: Dict[str, Any]
    ) -> Task:
        """
        Create a CrewAI task for ethical safety review.
        
        Args:
            diagnosis: Diagnosis information
            treatment_plan: Treatment plan
            patient_data: Patient information
            
        Returns:
            CrewAI Task
        """
        description = f"""
        Conduct comprehensive ethical and safety review:
        
        Diagnosis:
        {json.dumps(diagnosis, indent=2)}
        
        Treatment Plan:
        {json.dumps(treatment_plan, indent=2)}
        
        Patient Demographics:
        - Age: {patient_data.get('age', 'Unknown')}
        - Gender: {patient_data.get('gender', 'Unknown')}
        
        Review requirements:
        1. HIPAA Compliance
           - Verify patient data privacy
           - Check consent requirements
           - Validate data encryption and access controls
        
        2. FDA Compliance
           - Verify all medications are FDA approved
           - Check for off-label uses
           - Validate dosing recommendations
        
        3. Medical Ethics
           - Assess beneficence (benefit to patient)
           - Ensure non-maleficence (do no harm)
           - Verify patient autonomy respected
           - Check justice and fairness in treatment
        
        4. Risk Assessment
           - Identify potential safety concerns
           - Evaluate treatment appropriateness
           - Check for contraindications
        
        Provide detailed findings and recommendations.
        """
        
        return Task(
            description=description,
            agent=self.agent,
            expected_output="JSON formatted compliance review with HIPAA, FDA, and ethics assessment"
        )


# Singleton instance
_ethical_safety_agent = None


def get_ethical_safety_agent() -> EthicalSafetyAgent:
    """Get or create ethical safety agent instance."""
    global _ethical_safety_agent
    if _ethical_safety_agent is None:
        _ethical_safety_agent = EthicalSafetyAgent()
    return _ethical_safety_agent
