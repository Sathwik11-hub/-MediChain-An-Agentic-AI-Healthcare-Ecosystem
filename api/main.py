"""
FastAPI backend application for MediChain.
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from typing import Dict, Any
import sys

from config.settings import settings
from models import (
    Patient, CaseCreate, CaseResponse, VitalSigns,
    WorkflowStatus, CaseStatus
)
from orchestration import get_crew_manager
from services import get_postgres_service, get_neo4j_service

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)
logger.add(
    "logs/medichain.log",
    rotation="500 MB",
    retention="10 days",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
)

# Create FastAPI app
app = FastAPI(
    title="MediChain API",
    description="Multi-Agent Medical AI System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# Dependency injection
def get_crew():
    """Get crew manager instance."""
    return get_crew_manager()


def get_db():
    """Get database service instance."""
    return get_postgres_service()


# Health check
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "MediChain API",
        "version": "1.0.0",
        "environment": settings.environment
    }


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to MediChain API",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }


# Patient endpoints
@app.post("/api/patients", tags=["Patients"], response_model=Dict[str, str])
async def create_patient(patient: Patient, db=Depends(get_db)):
    """
    Create a new patient record.
    
    Args:
        patient: Patient information
        
    Returns:
        Created patient ID
    """
    logger.info(f"Creating patient: {patient.patient_id}")
    
    try:
        # Convert to dict
        patient_data = patient.model_dump()
        
        # Create in PostgreSQL
        patient_id = db.create_patient(patient_data)
        
        if not patient_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create patient"
            )
        
        # Create in Neo4j
        neo4j = get_neo4j_service()
        neo4j.create_patient_node({
            "patient_id": patient.patient_id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender.value
        })
        
        logger.info(f"Patient created successfully: {patient_id}")
        return {"patient_id": patient_id, "status": "created"}
        
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/patients/{patient_id}", tags=["Patients"])
async def get_patient(patient_id: str, db=Depends(get_db)):
    """
    Get patient by ID.
    
    Args:
        patient_id: Patient identifier
        
    Returns:
        Patient information
    """
    logger.info(f"Retrieving patient: {patient_id}")
    
    patient = db.get_patient(patient_id)
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    
    return patient


@app.get("/api/patients/{patient_id}/history", tags=["Patients"])
async def get_patient_history(patient_id: str, crew=Depends(get_crew)):
    """
    Get patient medical history.
    
    Args:
        patient_id: Patient identifier
        
    Returns:
        Patient history with cases and diagnoses
    """
    logger.info(f"Retrieving history for patient: {patient_id}")
    
    try:
        history = crew.get_patient_history(patient_id)
        return history
        
    except Exception as e:
        logger.error(f"Error retrieving patient history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Case endpoints
@app.post("/api/cases/create", tags=["Cases"], response_model=Dict[str, str])
async def create_case(case: CaseCreate, db=Depends(get_db)):
    """
    Create a new medical case.
    
    Args:
        case: Case information with patient ID and symptoms
        
    Returns:
        Created case ID
    """
    logger.info(f"Creating case for patient: {case.patient_id}")
    
    try:
        # Get patient data
        patient = db.get_patient(case.patient_id)
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {case.patient_id} not found"
            )
        
        # Create case in database
        import uuid
        case_id = str(uuid.uuid4())
        
        case_data = {
            "case_id": case_id,
            "patient_id": case.patient_id,
            "symptoms": case.symptoms.model_dump(),
            "diagnosis": None,
            "treatment_plan": None,
            "status": CaseStatus.PENDING.value
        }
        
        db.create_case(case_data)
        
        logger.info(f"Case created: {case_id}")
        return {
            "case_id": case_id,
            "status": "created",
            "message": "Case created. Use /api/cases/{case_id}/analyze to start analysis."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/cases/{case_id}/analyze", tags=["Cases"])
async def analyze_case(
    case_id: str,
    crew=Depends(get_crew),
    db=Depends(get_db)
):
    """
    Analyze a medical case using the agent workflow.
    
    Args:
        case_id: Case identifier
        
    Returns:
        Analysis results from all agents
    """
    logger.info(f"Analyzing case: {case_id}")
    
    try:
        # Get case data
        case = db.get_case(case_id)
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found"
            )
        
        # Get patient data
        patient = db.get_patient(case['patient_id'])
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {case['patient_id']} not found"
            )
        
        # Update case status
        db.update_case(case_id, {"status": CaseStatus.IN_PROGRESS.value})
        
        # Execute diagnostic workflow
        results = crew.execute_diagnostic_workflow(
            patient_data=patient,
            symptoms=case['symptoms']
        )
        
        # Update case with results
        if results['status'] == 'completed':
            update_data = {
                "status": CaseStatus.COMPLETED.value,
                "diagnosis": results['steps'].get('symptom_analysis', {}).get('result'),
                "treatment_plan": results['steps'].get('treatment_planning', {}).get('result')
            }
            db.update_case(case_id, update_data)
        
        logger.info(f"Case analysis completed: {case_id}")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing case: {e}")
        # Update case status to reflect error
        try:
            db.update_case(case_id, {"status": "error"})
        except:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/cases/{case_id}", tags=["Cases"])
async def get_case(case_id: str, db=Depends(get_db)):
    """
    Get case details.
    
    Args:
        case_id: Case identifier
        
    Returns:
        Case information
    """
    logger.info(f"Retrieving case: {case_id}")
    
    case = db.get_case(case_id)
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found"
        )
    
    return case


@app.get("/api/cases/{case_id}/status", tags=["Cases"])
async def get_case_status(case_id: str, db=Depends(get_db)):
    """
    Get case analysis status.
    
    Args:
        case_id: Case identifier
        
    Returns:
        Case status and progress
    """
    logger.info(f"Checking status for case: {case_id}")
    
    case = db.get_case(case_id)
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found"
        )
    
    return {
        "case_id": case_id,
        "status": case['status'],
        "patient_id": case['patient_id'],
        "has_diagnosis": case['diagnosis'] is not None,
        "has_treatment_plan": case['treatment_plan'] is not None
    }


# Monitoring endpoints
@app.post("/api/monitor/vitals", tags=["Monitoring"])
async def monitor_vitals(vitals: VitalSigns, crew=Depends(get_crew)):
    """
    Monitor patient vital signs.
    
    Args:
        vitals: Vital signs data
        
    Returns:
        Monitoring analysis with alerts
    """
    logger.info(f"Monitoring vitals for patient: {vitals.patient_id}")
    
    try:
        # Convert to dict
        vitals_data = vitals.model_dump()
        
        # Execute monitoring workflow
        results = crew.execute_monitoring_workflow(
            patient_id=vitals.patient_id,
            vitals=vitals_data
        )
        
        logger.info(f"Vitals monitoring completed for patient: {vitals.patient_id}")
        return results
        
    except Exception as e:
        logger.error(f"Error monitoring vitals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Statistics endpoint
@app.get("/api/stats", tags=["System"])
async def get_statistics(db=Depends(get_db)):
    """
    Get system statistics.
    
    Returns:
        System usage statistics
    """
    try:
        # In production, implement proper statistics collection
        from services import get_llm_service
        
        llm_stats = get_llm_service().get_usage_stats()
        
        return {
            "llm_usage": llm_stats,
            "environment": settings.environment
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return {
            "error": str(e)
        }


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Execute on application startup."""
    logger.info("MediChain API starting up...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Log level: {settings.log_level}")


@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown."""
    logger.info("MediChain API shutting down...")
    
    # Close database connections
    try:
        neo4j = get_neo4j_service()
        neo4j.close()
    except:
        pass


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
