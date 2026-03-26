"""API routes for anomaly detection and analysis."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Transaction, Anomaly
from app.services.anomaly_detector import AnomalyDetector
from app.services.root_cause_analyzer import RootCauseAnalyzer, ActionDecisionEngine
from app.services.audit_logger import AuditLogger
from app.schemas import AnomalyResponse
from typing import List

router = APIRouter(prefix="/api", tags=["anomalies"])

detector = AnomalyDetector()
analyzer = RootCauseAnalyzer()
decision_engine = ActionDecisionEngine()


@router.post("/detect-anomalies")
async def detect_anomalies(db: Session = Depends(get_db)):
    """
    Run anomaly detection on all loaded transactions.
    Creates Anomaly records and returns results.
    """
    try:
        # Get all transactions
        transactions = db.query(Transaction).all()
        
        if not transactions:
            raise HTTPException(status_code=400, detail="No transactions found. Upload data first.")

        # Convert to list of dicts for ML processing
        trans_list = [
            {
                'id': t.id,
                'vendor': t.vendor,
                'amount': t.amount,
                'category': t.category,
                'date': t.date.isoformat() if hasattr(t.date, 'isoformat') else str(t.date),
                'description': t.description
            }
            for t in transactions
        ]

        # Run detection
        detected_anomalies = detector.detect_all_anomalies(trans_list)

        # Store anomalies in database
        stored_anomalies = []
        for anom in detected_anomalies:
            # Check if anomaly already exists for this transaction
            existing = db.query(Anomaly).filter(
                Anomaly.transaction_id == anom['transaction_id'],
                Anomaly.anomaly_type == anom['anomaly_type']
            ).first()

            if not existing:
                try:
                    # Perform root cause analysis
                    root_cause = analyzer.analyze(anom)
                    
                    # Create anomaly record
                    db_anomaly = Anomaly(
                        transaction_id=anom['transaction_id'],
                        anomaly_type=anom['anomaly_type'],
                        confidence_score=anom['confidence_score'],
                        severity=anom['severity'],
                        description=anom['description'],
                        root_cause=root_cause,
                        potential_savings=anom['potential_savings'],
                        details=anom.get('details'),
                        status='new'
                    )
                    db.add(db_anomaly)
                    db.flush()

                    # Log detection
                    AuditLogger.log_detection(
                        db, anom['anomaly_type'],
                        anom['transaction_id'],
                        anom['confidence_score'],
                        anom.get('details')
                    )

                    stored_anomalies.append(db_anomaly)
                except Exception as inner_err:
                    print(f"Error processing anomaly {anom}: {str(inner_err)}")
                    import traceback
                    traceback.print_exc()
                    db.rollback()
                    continue

        db.commit()

        return {
            'anomalies_detected': len(stored_anomalies),
            'total_potential_savings': sum(a.potential_savings for a in stored_anomalies),
            'anomalies': [
                {
                    'id': a.id,
                    'transaction_id': a.transaction_id,
                    'type': a.anomaly_type,
                    'severity': a.severity,
                    'confidence': f"{a.confidence_score:.1%}",
                    'description': a.description,
                    'savings': a.potential_savings
                }
                for a in stored_anomalies
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in detect_anomalies: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Detection error: {str(e)}")


@router.get("/anomalies", response_model=List[AnomalyResponse])
async def get_anomalies(
    status: str = None,
    severity: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get detected anomalies with optional filtering."""
    query = db.query(Anomaly).order_by(Anomaly.created_at.desc())

    if status:
        query = query.filter(Anomaly.status == status)
    
    if severity:
        query = query.filter(Anomaly.severity == severity)

    return query.limit(limit).all()


@router.get("/anomalies/{anomaly_id}", response_model=AnomalyResponse)
async def get_anomaly(anomaly_id: int, db: Session = Depends(get_db)):
    """Get a specific anomaly by ID."""
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    
    return anomaly


@router.patch("/anomalies/{anomaly_id}")
async def update_anomaly(
    anomaly_id: int,
    status: str = None,
    root_cause: str = None,
    db: Session = Depends(get_db)
):
    """Update anomaly status or root cause."""
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    if status:
        anomaly.status = status
    
    if root_cause:
        anomaly.root_cause = root_cause

    db.commit()

    return {
        'id': anomaly.id,
        'status': anomaly.status,
        'root_cause': anomaly.root_cause,
        'message': 'Anomaly updated successfully'
    }
