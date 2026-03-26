"""API routes for actions and corrections."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Transaction, Anomaly, Action
from app.services.root_cause_analyzer import ActionDecisionEngine
from app.services.audit_logger import AuditLogger
from app.schemas import ActionResponse, ActionCreate, ActionUpdate
from typing import List

router = APIRouter(prefix="/api", tags=["actions"])

decision_engine = ActionDecisionEngine()


@router.post("/generate-actions")
async def generate_actions(db: Session = Depends(get_db)):
    """Generate corrective actions for all unhandled anomalies."""
    
    # Get anomalies without actions
    anomalies = db.query(Anomaly).filter(
        Anomaly.status.in_(['new', 'investigating'])
    ).all()

    if not anomalies:
        return {'actions_generated': 0, 'message': 'No new anomalies to process'}

    generated_count = 0
    all_actions = []

    for anomaly in anomalies:
        # Check if actions already exist
        existing_actions = db.query(Action).filter(
            Action.transaction_id == anomaly.transaction_id
        ).count()

        if existing_actions > 0:
            continue

        # Decide on actions
        actions_to_take = decision_engine.decide_actions(
            {
                'anomaly_type': anomaly.anomaly_type,
                'severity': anomaly.severity,
                'description': anomaly.description,
                'potential_savings': anomaly.potential_savings,
                'details': anomaly.details or {}
            },
            anomaly.root_cause
        )

        # Create action records
        for action_spec in actions_to_take:
            # Generate email content if applicable
            email_content = ""
            if action_spec['action_type'] == 'email':
                email_content = decision_engine.generate_email_content(
                    action_spec,
                    {
                        'anomaly_type': anomaly.anomaly_type,
                        'description': anomaly.description,
                        'potential_savings': anomaly.potential_savings,
                        'details': anomaly.details or {}
                    }
                )

            action = Action(
                transaction_id=anomaly.transaction_id,
                action_type=action_spec['action_type'],
                priority=action_spec['priority'],
                content=email_content if email_content else action_spec['description'],
                recipient=action_spec.get('recipient', 'procurement@company.local'),
                estimated_savings=action_spec['estimated_savings'],
                status='pending'
            )
            db.add(action)
            generated_count += 1
            all_actions.append(action)

        # Update anomaly status
        anomaly.status = 'investigating'
        db.commit()

        # Log action trigger
        for action in all_actions:
            AuditLogger.log_action_triggered(
                db, action.id, action.action_type,
                action.priority, {'anomaly_id': anomaly.id}
            )

    return {
        'actions_generated': generated_count,
        'total_estimated_savings': sum(a.estimated_savings for a in all_actions),
        'message': f'Generated {generated_count} corrective actions'
    }


@router.get("/actions", response_model=List[ActionResponse])
async def get_actions(
    status: str = None,
    priority: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get action items with optional filtering."""
    query = db.query(Action).order_by(Action.created_at.desc())

    if status:
        query = query.filter(Action.status == status)
    
    if priority:
        query = query.filter(Action.priority == priority)

    return query.limit(limit).all()


@router.get("/actions/{action_id}", response_model=ActionResponse)
async def get_action(action_id: int, db: Session = Depends(get_db)):
    """Get a specific action by ID."""
    action = db.query(Action).filter(Action.id == action_id).first()
    
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    return action


@router.patch("/actions/{action_id}", response_model=ActionResponse)
async def update_action(
    action_id: int,
    update_data: ActionUpdate,
    db: Session = Depends(get_db)
):
    """Update action status or execution result."""
    action = db.query(Action).filter(Action.id == action_id).first()
    
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    if update_data.status is not None:
        action.status = update_data.status
    
    if update_data.executed is not None:
        action.executed = update_data.executed
        action.status = 'completed' if update_data.executed else action.status
    
    if update_data.execution_result is not None:
        action.execution_result = update_data.execution_result

    db.commit()

    # Log execution
    if update_data.executed:
        AuditLogger.log_action_execution(
            db, action.id, action.status,
            update_data.execution_result or 'Successfully executed',
            {'estimated_savings': action.estimated_savings}
        )

    return action


@router.post("/actions/{action_id}/execute")
async def execute_action(action_id: int, db: Session = Depends(get_db)):
    """Simulate execution of an action (e.g., send email, flag transaction)."""
    action = db.query(Action).filter(Action.id == action_id).first()
    
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    # Simulate action execution
    result = _simulate_execute_action(action)

    action.executed = True
    action.status = 'completed'
    action.execution_result = result
    db.commit()

    # Log execution
    AuditLogger.log_action_execution(
        db, action.id, 'completed', result,
        {'action_type': action.action_type}
    )

    return {
        'action_id': action.id,
        'executed': True,
        'result': result,
        'message': 'Action executed successfully'
    }


def _simulate_execute_action(action: Action) -> str:
    """Simulate action execution."""
    if action.action_type == 'email':
        return f"Email sent to {action.recipient} regarding transaction correction"
    elif action.action_type == 'flag':
        return f"Transaction flagged for {action.priority} priority review"
    elif action.action_type == 'negotiate':
        return f"Negotiation initiated with vendor from transaction {action.transaction_id}"
    elif action.action_type == 'cancel':
        return f"Service cancellation request sent for transaction {action.transaction_id}"
    else:
        return f"Action {action.action_type} executed"
