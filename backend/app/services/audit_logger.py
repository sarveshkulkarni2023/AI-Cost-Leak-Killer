"""Audit logging service."""
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import AuditLog


class AuditLogger:
    """Handle audit logging for all system decisions."""

    @staticmethod
    def log_detection(
        db: Session,
        anomaly_type: str,
        transaction_id: int,
        confidence_score: float,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log anomaly detection event."""
        log = AuditLog(
            event_type='detection',
            event_description=f"Anomaly detected: {anomaly_type} with confidence {confidence_score:.2%}",
            entity_type='anomaly',
            entity_id=transaction_id,
            user_action='system_detection',
            details={
                'anomaly_type': anomaly_type,
                'confidence_score': float(confidence_score),
                'event_details': details or {}
            },
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        return log

    @staticmethod
    def log_analysis(
        db: Session,
        anomaly_id: int,
        root_cause: str,
        severity: str,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log root cause analysis event."""
        log = AuditLog(
            event_type='analysis',
            event_description=f"Root cause analysis completed: {root_cause} (severity: {severity})",
            entity_type='anomaly',
            entity_id=anomaly_id,
            user_action='system_analysis',
            details={
                'root_cause': root_cause,
                'severity': severity,
                'event_details': details or {}
            },
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        return log

    @staticmethod
    def log_action_triggered(
        db: Session,
        action_id: int,
        action_type: str,
        priority: str,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log action trigger event."""
        log = AuditLog(
            event_type='action',
            event_description=f"Action triggered: {action_type} (priority: {priority})",
            entity_type='action',
            entity_id=action_id,
            user_action='system_action_trigger',
            details={
                'action_type': action_type,
                'priority': priority,
                'event_details': details or {}
            },
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        return log

    @staticmethod
    def log_action_execution(
        db: Session,
        action_id: int,
        status: str,
        result: str,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log action execution event."""
        log = AuditLog(
            event_type='action',
            event_description=f"Action executed: {action_id} - Status: {status}",
            entity_type='action',
            entity_id=action_id,
            user_action='system_execution',
            details={
                'status': status,
                'result': result,
                'event_details': details or {}
            },
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        return log

    @staticmethod
    def log_resolution(
        db: Session,
        anomaly_id: int,
        resolution_type: str,
        savings_realized: float,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log anomaly resolution event."""
        log = AuditLog(
            event_type='resolution',
            event_description=f"Anomaly resolved via {resolution_type} ({savings_realized:,.2f} savings)",
            entity_type='anomaly',
            entity_id=anomaly_id,
            user_action='system_resolution',
            details={
                'resolution_type': resolution_type,
                'savings_realized': float(savings_realized),
                'event_details': details or {}
            },
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        return log

    @staticmethod
    def log_user_action(
        db: Session,
        action_type: str,
        description: str,
        entity_type: str,
        entity_id: int,
        user_identifier: str,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log user-initiated action."""
        log = AuditLog(
            event_type='user_action',
            event_description=description,
            entity_type=entity_type,
            entity_id=entity_id,
            user_action=f"{user_identifier}:{action_type}",
            details=details or {},
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        return log

    @staticmethod
    def get_logs(
        db: Session,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        limit: int = 100
    ) -> list:
        """Retrieve audit logs with optional filtering."""
        query = db.query(AuditLog).order_by(AuditLog.timestamp.desc())
        
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        
        return query.limit(limit).all()
