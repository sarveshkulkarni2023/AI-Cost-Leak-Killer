"""Pydantic request/response models."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


# Transaction schemas
class TransactionBase(BaseModel):
    vendor: str
    amount: float
    category: str
    date: datetime
    description: Optional[str] = None
    currency: str = "USD"


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Anomaly schemas
class AnomalyBase(BaseModel):
    anomaly_type: str
    confidence_score: float
    severity: str
    description: str
    root_cause: Optional[str] = None
    potential_savings: float
    details: Optional[Dict[str, Any]] = None


class AnomalyCreate(AnomalyBase):
    transaction_id: int


class AnomalyUpdate(BaseModel):
    status: Optional[str] = None
    root_cause: Optional[str] = None


class AnomalyResponse(AnomalyBase):
    id: int
    transaction_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Action schemas
class ActionBase(BaseModel):
    action_type: str
    priority: str
    content: str
    recipient: Optional[str] = None
    estimated_savings: float


class ActionCreate(ActionBase):
    transaction_id: int


class ActionUpdate(BaseModel):
    status: Optional[str] = None
    executed: Optional[bool] = None
    execution_result: Optional[str] = None


class ActionResponse(ActionBase):
    id: int
    transaction_id: int
    status: str
    executed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Audit log schemas
class AuditLogCreate(BaseModel):
    event_type: str
    event_description: str
    entity_type: str
    entity_id: int
    user_action: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class AuditLogResponse(AuditLogCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# Financial metrics schemas
class FinancialMetricsResponse(BaseModel):
    id: int
    period_start: datetime
    period_end: datetime
    total_anomalies_detected: int
    total_potential_savings: float
    realized_savings: float
    monthly_projection: float
    yearly_projection: float
    top_vendor: Optional[str]
    top_category: Optional[str]

    class Config:
        from_attributes = True


# Dashboard summary schemas
class DashboardSummary(BaseModel):
    total_transactions: int
    total_anomalies: int
    total_potential_savings: float
    critical_issues: int
    high_priority_issues: int
    actions_pending: int
    actions_completed: int
    monthly_projection: float
    yearly_projection: float
    top_vendors: List[Dict[str, Any]]
    anomaly_distribution: Dict[str, int]


# File upload schemas
class FileUploadResponse(BaseModel):
    filename: str
    records_uploaded: int
    records_rejected: int
    validation_errors: List[str]
    message: str
