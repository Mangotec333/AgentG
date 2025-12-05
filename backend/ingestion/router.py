"""
Ingestion API router - FastAPI endpoint for receiving agent events.
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared.schemas.events import BatchEvent
from shared.logger import backend_logger
from backend.ingestion.validator import EventValidator
from backend.ingestion.normalizer import EventNormalizer
from backend.ingestion.storage import EventStorage
from backend.ingestion.security import verify_api_key
from backend.compliance_engine.router import router as compliance_router

# Import test runner (only if available)
try:
    from backend.test_runner.api import router as test_runner_router
    TEST_RUNNER_AVAILABLE = True
except ImportError:
    TEST_RUNNER_AVAILABLE = False


app = FastAPI(title="AI Workflow Shield - Ingestion API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include compliance router
app.include_router(compliance_router)

# Include test runner router (if available)
if TEST_RUNNER_AVAILABLE:
    app.include_router(test_runner_router)

# Initialize components
validator = EventValidator()
normalizer = EventNormalizer()
storage = EventStorage()


@app.post("/api/v1/ingest")
async def ingest_events(
    batch: BatchEvent,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Ingest a batch of events from Guardian Agent.
    
    Args:
        batch: Batch of events
        x_api_key: API key for authentication
    
    Returns:
        Success response
    """
    try:
        # Verify API key
        if not verify_api_key(x_api_key, batch.workspace_id):
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        backend_logger.info(
            f"Received batch: {len(batch.events)} events from agent {batch.agent_id}"
        )
        
        # Validate events
        validated_events = []
        for event in batch.events:
            if validator.validate(event):
                validated_events.append(event)
            else:
                backend_logger.warning(f"Invalid event rejected: {event.event_type}")
        
        if not validated_events:
            raise HTTPException(status_code=400, detail="No valid events in batch")
        
        # Normalize events
        normalized_events = []
        for event in validated_events:
            normalized = normalizer.normalize(event)
            normalized_events.append(normalized)
        
        # Store events
        stored_count = await storage.store_events(normalized_events, batch.workspace_id)
        
        # Queue for threat engine processing
        await storage.queue_for_threat_engine(normalized_events)
        
        backend_logger.info(f"Stored {stored_count} events, queued for threat engine")
        
        return {
            "status": "success",
            "events_received": len(batch.events),
            "events_stored": stored_count,
            "batch_id": batch.batch_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        backend_logger.error(f"Error ingesting events: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ingestion-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

