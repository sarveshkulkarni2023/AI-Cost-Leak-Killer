"""API routes for audit logs."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AuditLog
from app.schemas import AuditLogResponse
from typing import List

router = APIRouter(prefix="/api", tags=["logs"])


@router.get("/logs", response_model=List[AuditLogResponse])
async def get_logs(
    event_type: str = None,
    entity_type: str = None,
    entity_id: int = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get audit logs with optional filtering."""
    query = db.query(AuditLog).order_by(AuditLog.timestamp.desc())

    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)

    return query.limit(limit).all()


@router.get("/logs/stats")
async def get_log_stats(db: Session = Depends(get_db)):
    """Get audit log statistics."""
    total_logs = db.query(AuditLog).count()
    
    # Count by event type
    event_types = db.query(AuditLog.event_type).distinct().all()
    event_counts = {}
    for et in event_types:
        count = db.query(AuditLog).filter(AuditLog.event_type == et[0]).count()
        event_counts[et[0]] = count

    return {
        'total_logs': total_logs,
        'event_type_distribution': event_counts,
        'message': 'Audit log statistics'
    }
