"""SQLAlchemy database models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Transaction(Base):
    """Transaction model for cost data."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    vendor = Column(String(255), index=True)
    amount = Column(Float)
    category = Column(String(255))
    date = Column(DateTime, index=True)
    description = Column(Text)
    currency = Column(String(10), default="USD")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    anomalies = relationship("Anomaly", back_populates="transaction", cascade="all, delete-orphan")
    actions = relationship("Action", back_populates="transaction", cascade="all, delete-orphan")


class Anomaly(Base):
    """Detected anomalies in cost data."""
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), index=True)
    anomaly_type = Column(String(100))  # duplicate, outlier, vendor_anomaly, pattern
    confidence_score = Column(Float)
    severity = Column(String(50))  # low, medium, high, critical
    description = Column(Text)
    root_cause = Column(Text)
    potential_savings = Column(Float)
    status = Column(String(50), default="new")  # new, investigating, resolved, ignored
    details = Column(JSON)  # Additional metadata about the anomaly
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign key relationship
    transaction = relationship("Transaction", back_populates="anomalies")


class Action(Base):
    """Corrective actions triggered by anomalies."""
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), index=True)
    action_type = Column(String(100))  # email, flag, negotiate, cancel
    priority = Column(String(50))  # low, medium, high, critical
    status = Column(String(50), default="pending")  # pending, in_progress, completed, failed
    content = Column(Text)
    recipient = Column(String(255))
    estimated_savings = Column(Float)
    executed = Column(Boolean, default=False)
    execution_result = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign key relationship
    transaction = relationship("Transaction", back_populates="actions")


class AuditLog(Base):
    """Audit trail for all system decisions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100))  # detection, analysis, action, resolution
    event_description = Column(Text)
    entity_type = Column(String(100))  # anomaly, action, transaction
    entity_id = Column(Integer, index=True)
    user_action = Column(String(255))
    details = Column(JSON)  # Additional event information
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class FinancialMetrics(Base):
    """Financial impact metrics and projections."""
    __tablename__ = "financial_metrics"

    id = Column(Integer, primary_key=True, index=True)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    total_anomalies_detected = Column(Integer)
    total_potential_savings = Column(Float)
    realized_savings = Column(Float, default=0)
    monthly_projection = Column(Float)
    yearly_projection = Column(Float)
    top_vendor = Column(String(255))
    top_category = Column(String(255))
    details = Column(JSON)  # Additional metrics data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
