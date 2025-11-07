"""
Patient Monitoring Agent.
"""
import json
from typing import Dict, Any, List, Optional
from loguru import logger
from crewai import Agent, Task
from datetime import datetime

from services.llm_service import get_llm_service
from config.prompts import PATIENT_MONITORING_PROMPT


class PatientMonitorAgent:
    """Agent for monitoring patient vitals and detecting anomalies."""
    
    def __init__(self):
        """Initialize the patient monitor agent."""
        self.llm_service = get_llm_service()
        self.agent = self._create_agent()
        logger.info("Patient Monitor Agent initialized")
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent."""
        return Agent(
            role="Clinical Monitoring Specialist",
            goal="Monitor patient vital signs, detect anomalies, and generate timely alerts",
            backstory="""You are an ICU monitoring specialist with expertise in vital signs 
            interpretation and early warning systems. You excel at identifying subtle changes 
            in patient conditions and providing actionable alerts to clinical staff.""",
            verbose=True,
            allow_delegation=False
        )
    
    def analyze_vitals(
        self,
        patient_id: str,
        vitals: Dict[str, Any],
        baseline: Optional[Dict[str, Any]] = None,
        patient_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze patient vital signs for anomalies.
        
        Args:
            patient_id: Patient identifier
            vitals: Current vital signs
            baseline: Baseline/normal vitals for comparison
            patient_data: Patient medical information
            
        Returns:
            Analysis results with alerts and recommendations
        """
        logger.info(f"Analyzing vitals for patient: {patient_id}")
        
        try:
            # Prepare vitals summary
            vitals_text = self._format_vitals(vitals)
            baseline_text = self._format_vitals(baseline) if baseline else "Not available"
            
            # Get patient conditions
            conditions = []
            age = "unknown"
            if patient_data:
                conditions = patient_data.get('medical_history', [])
                age = patient_data.get('age', 'unknown')
            
            # Build prompt
            prompt = PATIENT_MONITORING_PROMPT.format(
                patient_id=patient_id,
                vitals=vitals_text,
                baseline=baseline_text,
                conditions=", ".join(conditions) if conditions else "None reported",
                age=age
            )
            
            # Generate analysis
            response = self.llm_service.generate_response(
                prompt=prompt,
                temperature=0.2,  # Low temperature for consistent monitoring
                json_mode=True
            )
            
            # Parse response
            result = json.loads(response)
            
            # Enhance with rule-based checks
            result = self._add_rule_based_alerts(result, vitals, patient_data)
            
            # Add timestamp
            result['timestamp'] = datetime.utcnow().isoformat()
            result['patient_id'] = patient_id
            
            logger.info(f"Analysis complete. Status: {result.get('status', 'unknown')}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing monitoring response: {e}")
            return {
                "status": "error",
                "anomalies": [],
                "alerts": [],
                "trends": [],
                "recommendations": [],
                "error": "Failed to parse monitoring response"
            }
        except Exception as e:
            logger.error(f"Error analyzing vitals: {e}")
            return {
                "status": "error",
                "anomalies": [],
                "alerts": [],
                "trends": [],
                "recommendations": [],
                "error": str(e)
            }
    
    def _format_vitals(self, vitals: Dict[str, Any]) -> str:
        """Format vitals for display."""
        if not vitals:
            return "None"
        
        parts = []
        
        if 'heart_rate' in vitals:
            parts.append(f"Heart Rate: {vitals['heart_rate']} bpm")
        if 'blood_pressure_systolic' in vitals and 'blood_pressure_diastolic' in vitals:
            parts.append(f"Blood Pressure: {vitals['blood_pressure_systolic']}/{vitals['blood_pressure_diastolic']} mmHg")
        if 'temperature' in vitals:
            parts.append(f"Temperature: {vitals['temperature']}°C")
        if 'respiratory_rate' in vitals:
            parts.append(f"Respiratory Rate: {vitals['respiratory_rate']} /min")
        if 'oxygen_saturation' in vitals:
            parts.append(f"O2 Saturation: {vitals['oxygen_saturation']}%")
        
        return ", ".join(parts) if parts else "None"
    
    def _add_rule_based_alerts(
        self,
        result: Dict[str, Any],
        vitals: Dict[str, Any],
        patient_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Add rule-based alerts for critical values."""
        critical_alerts = []
        
        # Heart rate checks
        hr = vitals.get('heart_rate')
        if hr:
            if hr > 120:
                critical_alerts.append({
                    "type": "urgent",
                    "message": f"Critical: Tachycardia detected (HR: {hr})",
                    "action_required": "Immediate medical evaluation required"
                })
            elif hr < 50:
                critical_alerts.append({
                    "type": "urgent",
                    "message": f"Critical: Bradycardia detected (HR: {hr})",
                    "action_required": "Immediate medical evaluation required"
                })
        
        # Blood pressure checks
        bp_sys = vitals.get('blood_pressure_systolic')
        bp_dia = vitals.get('blood_pressure_diastolic')
        if bp_sys:
            if bp_sys > 180 or bp_dia and bp_dia > 120:
                critical_alerts.append({
                    "type": "urgent",
                    "message": f"Critical: Hypertensive crisis (BP: {bp_sys}/{bp_dia})",
                    "action_required": "Immediate medical intervention required"
                })
            elif bp_sys < 90:
                critical_alerts.append({
                    "type": "urgent",
                    "message": f"Critical: Hypotension detected (SBP: {bp_sys})",
                    "action_required": "Immediate medical evaluation required"
                })
        
        # Temperature checks
        temp = vitals.get('temperature')
        if temp:
            if temp > 39.5:
                critical_alerts.append({
                    "type": "urgent",
                    "message": f"Critical: High fever (Temp: {temp}°C)",
                    "action_required": "Antipyretic treatment and evaluation"
                })
            elif temp < 35:
                critical_alerts.append({
                    "type": "urgent",
                    "message": f"Critical: Hypothermia (Temp: {temp}°C)",
                    "action_required": "Warming measures required"
                })
        
        # Oxygen saturation checks
        o2 = vitals.get('oxygen_saturation')
        if o2 and o2 < 90:
            critical_alerts.append({
                "type": "urgent",
                "message": f"Critical: Hypoxemia (O2 Sat: {o2}%)",
                "action_required": "Oxygen therapy and immediate evaluation"
            })
        
        # Add critical alerts to result
        if critical_alerts:
            if 'alerts' not in result:
                result['alerts'] = []
            result['alerts'].extend(critical_alerts)
            
            # Upgrade status if critical alerts present
            if result.get('status') != 'critical':
                result['status'] = 'critical'
        
        return result
    
    def monitor_trends(
        self,
        patient_id: str,
        vitals_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze trends in vital signs over time.
        
        Args:
            patient_id: Patient identifier
            vitals_history: List of historical vital sign readings
            
        Returns:
            Trend analysis with predictions
        """
        logger.info(f"Analyzing trends for patient: {patient_id}")
        
        if len(vitals_history) < 2:
            return {
                "patient_id": patient_id,
                "trends": [],
                "predictions": [],
                "note": "Insufficient data for trend analysis (minimum 2 readings required)"
            }
        
        try:
            # Calculate trends for each vital
            trends = {}
            
            for vital in ['heart_rate', 'blood_pressure_systolic', 'temperature', 'oxygen_saturation']:
                values = [v.get(vital) for v in vitals_history if v.get(vital) is not None]
                
                if len(values) >= 2:
                    # Calculate simple trend
                    trend = "increasing" if values[-1] > values[0] else "decreasing" if values[-1] < values[0] else "stable"
                    change = values[-1] - values[0]
                    
                    trends[vital] = {
                        "trend": trend,
                        "change": change,
                        "current": values[-1],
                        "baseline": values[0]
                    }
            
            return {
                "patient_id": patient_id,
                "trends": trends,
                "readings_analyzed": len(vitals_history),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return {
                "patient_id": patient_id,
                "trends": {},
                "error": str(e)
            }
    
    def create_task(
        self,
        patient_id: str,
        vitals: Dict[str, Any],
        patient_data: Dict[str, Any]
    ) -> Task:
        """
        Create a CrewAI task for patient monitoring.
        
        Args:
            patient_id: Patient identifier
            vitals: Current vital signs
            patient_data: Patient information
            
        Returns:
            CrewAI Task
        """
        description = f"""
        Monitor and analyze vital signs for patient {patient_id}:
        
        Patient: {patient_data.get('name', 'Unknown')}
        Age: {patient_data.get('age', 'Unknown')}
        Conditions: {', '.join(patient_data.get('medical_history', []))}
        
        Current Vitals:
        {json.dumps(vitals, indent=2)}
        
        Tasks:
        1. Assess each vital sign against normal ranges
        2. Identify any anomalies or concerning values
        3. Generate alerts for urgent conditions
        4. Provide monitoring recommendations
        5. Suggest any immediate interventions needed
        """
        
        return Task(
            description=description,
            agent=self.agent,
            expected_output="JSON formatted vital signs analysis with alerts and recommendations"
        )


# Singleton instance
_patient_monitor = None


def get_patient_monitor() -> PatientMonitorAgent:
    """Get or create patient monitor instance."""
    global _patient_monitor
    if _patient_monitor is None:
        _patient_monitor = PatientMonitorAgent()
    return _patient_monitor
