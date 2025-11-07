"""
Medical Knowledge Agent for research and literature review.
"""
import json
from typing import Dict, Any, List
from loguru import logger
from crewai import Agent, Task

from services.llm_service import get_llm_service
from services.rag_service import get_rag_service
from config.prompts import MEDICAL_RESEARCH_PROMPT


class MedicalKnowledgeAgent:
    """Agent for retrieving and validating medical knowledge."""
    
    def __init__(self):
        """Initialize the medical knowledge agent."""
        self.llm_service = get_llm_service()
        self.rag_service = get_rag_service()
        self.agent = self._create_agent()
        logger.info("Medical Knowledge Agent initialized")
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent."""
        return Agent(
            role="Medical Research Specialist",
            goal="Retrieve relevant medical literature and validate diagnoses with evidence-based research",
            backstory="""You are a medical research specialist with expertise in 
            evidence-based medicine and systematic literature review. You excel at 
            finding and synthesizing the latest medical research to support clinical decisions.""",
            verbose=True,
            allow_delegation=False
        )
    
    def research(self, diagnosis: Dict[str, Any], patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Research medical literature for a diagnosis.
        
        Args:
            diagnosis: Primary diagnosis to research
            patient_data: Patient information for context
            
        Returns:
            Research results with sources and recommendations
        """
        logger.info(f"Researching diagnosis: {diagnosis.get('name', 'unknown')}")
        
        try:
            # Build research query
            diagnosis_name = diagnosis.get('name', '')
            symptoms = diagnosis.get('reasoning', '')
            query = f"{diagnosis_name} diagnosis treatment guidelines"
            
            # Retrieve from PubMed
            pubmed_articles = self.rag_service.retrieve_pubmed_articles(
                query=query,
                max_results=10
            )
            
            # Perform vector search in knowledge base
            vector_results = self.rag_service.semantic_search(
                query=query,
                top_k=5
            )
            
            # Prepare prompt for LLM analysis
            prompt = MEDICAL_RESEARCH_PROMPT.format(
                query=query,
                diagnosis=json.dumps(diagnosis, indent=2)
            )
            
            # Add retrieved sources to prompt
            if pubmed_articles:
                sources_text = "\n".join([
                    f"- {article.get('title', 'Unknown')} ({article.get('url', '')})"
                    for article in pubmed_articles[:5]
                ])
                prompt += f"\n\nPubMed Sources:\n{sources_text}"
            
            # Generate research summary
            response = self.llm_service.generate_response(
                prompt=prompt,
                temperature=0.2,  # Low temperature for factual research
                json_mode=True
            )
            
            # Parse response
            result = json.loads(response)
            
            # Enrich with actual PubMed articles
            if 'sources' in result and isinstance(result['sources'], list):
                # Merge with actual PubMed data
                for i, article in enumerate(pubmed_articles[:len(result['sources'])]):
                    if i < len(result['sources']):
                        result['sources'][i].update({
                            'url': article.get('url', ''),
                            'pmid': article.get('pmid', '')
                        })
            
            logger.info(f"Retrieved {len(result.get('sources', []))} research sources")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing research response: {e}")
            return {
                "sources": pubmed_articles[:5] if pubmed_articles else [],
                "guidelines": [],
                "evidence_level": "unknown",
                "recommendations": [],
                "error": "Failed to parse research response"
            }
        except Exception as e:
            logger.error(f"Error during research: {e}")
            return {
                "sources": [],
                "guidelines": [],
                "evidence_level": "unknown",
                "recommendations": [],
                "error": str(e)
            }
    
    def validate_diagnosis(
        self,
        diagnoses: List[Dict[str, Any]],
        patient_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate multiple diagnoses with medical literature.
        
        Args:
            diagnoses: List of differential diagnoses
            patient_data: Patient information
            
        Returns:
            Validation results with evidence levels
        """
        logger.info(f"Validating {len(diagnoses)} diagnoses")
        
        results = {
            "validated_diagnoses": [],
            "evidence_summary": {},
            "recommendations": []
        }
        
        try:
            for diagnosis in diagnoses[:3]:  # Validate top 3 diagnoses
                research = self.research(diagnosis, patient_data)
                
                validated = {
                    "diagnosis": diagnosis,
                    "research": research,
                    "evidence_level": research.get('evidence_level', 'unknown'),
                    "source_count": len(research.get('sources', []))
                }
                
                results["validated_diagnoses"].append(validated)
            
            # Generate summary
            results["evidence_summary"] = {
                "total_sources": sum(
                    v["source_count"] for v in results["validated_diagnoses"]
                ),
                "avg_evidence_level": self._calculate_avg_evidence_level(
                    results["validated_diagnoses"]
                )
            }
            
            logger.info("Diagnosis validation completed")
            return results
            
        except Exception as e:
            logger.error(f"Error validating diagnoses: {e}")
            results["error"] = str(e)
            return results
    
    def _calculate_avg_evidence_level(self, validated_diagnoses: List[Dict[str, Any]]) -> str:
        """Calculate average evidence level."""
        levels = {"high": 3, "medium": 2, "low": 1, "unknown": 0}
        
        if not validated_diagnoses:
            return "unknown"
        
        total = sum(
            levels.get(d.get("evidence_level", "unknown"), 0)
            for d in validated_diagnoses
        )
        avg = total / len(validated_diagnoses)
        
        if avg >= 2.5:
            return "high"
        elif avg >= 1.5:
            return "medium"
        elif avg >= 0.5:
            return "low"
        else:
            return "unknown"
    
    def create_task(self, diagnoses: List[Dict[str, Any]], patient_data: Dict[str, Any]) -> Task:
        """
        Create a CrewAI task for medical research.
        
        Args:
            diagnoses: List of diagnoses to research
            patient_data: Patient information
            
        Returns:
            CrewAI Task
        """
        description = f"""
        Research and validate the following differential diagnoses:
        
        Patient: {patient_data.get('name', 'Unknown')}
        Age: {patient_data.get('age', 'Unknown')}
        
        Diagnoses to validate:
        {json.dumps(diagnoses, indent=2)}
        
        For each diagnosis:
        1. Search medical literature (PubMed, clinical guidelines)
        2. Assess evidence level (high/medium/low)
        3. Provide relevant citations
        4. Make recommendations based on evidence
        """
        
        return Task(
            description=description,
            agent=self.agent,
            expected_output="JSON formatted research results with sources and evidence levels"
        )


# Singleton instance
_medical_knowledge_agent = None


def get_medical_knowledge_agent() -> MedicalKnowledgeAgent:
    """Get or create medical knowledge agent instance."""
    global _medical_knowledge_agent
    if _medical_knowledge_agent is None:
        _medical_knowledge_agent = MedicalKnowledgeAgent()
    return _medical_knowledge_agent
