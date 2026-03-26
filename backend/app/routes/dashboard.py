"""API routes for dashboard and analytics."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Transaction, Anomaly, Action, FinancialMetrics
from app.schemas import DashboardSummary
from app.utils.helpers import MetricsAggregator, DateHelper
from app.services.financial_impact import FinancialImpactCalculator
from datetime import datetime

router = APIRouter(prefix="/api", tags=["dashboard"])

calculator = FinancialImpactCalculator()
aggregator = MetricsAggregator()


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard summary with key metrics."""
    
    # Count metrics
    total_transactions = db.query(Transaction).count()
    total_anomalies = db.query(Anomaly).count()
    critical_issues = db.query(Anomaly).filter(Anomaly.severity == 'critical').count()
    high_priority = db.query(Anomaly).filter(Anomaly.severity == 'high').count()
    actions_pending = db.query(Action).filter(Action.status == 'pending').count()
    actions_completed = db.query(Action).filter(Action.executed == True).count()

    # Calculate financial metrics
    transactions = db.query(Transaction).all()
    anomalies = db.query(Anomaly).all()

    trans_dicts = [
        {
            'vendor': t.vendor,
            'amount': t.amount,
            'category': t.category,
            'date': t.date,
            'id': t.id
        }
        for t in transactions
    ]

    anom_dicts = [
        {
            'potential_savings': a.potential_savings,
            'anomaly_type': a.anomaly_type,
            'severity': a.severity
        }
        for a in anomalies
    ]

    impact = calculator.calculate_impact(anom_dicts)
    projections = calculator.calculate_projections(trans_dicts, anom_dicts, 30)

    # Top vendors
    vendor_metrics = aggregator.aggregate_by_vendor(trans_dicts)
    top_vendors = aggregator.top_n_items(vendor_metrics, n=5)

    # Anomaly distribution
    anomaly_dist = {}
    for anom in anomalies:
        anomaly_dist[anom.anomaly_type] = anomaly_dist.get(anom.anomaly_type, 0) + 1

    return DashboardSummary(
        total_transactions=total_transactions,
        total_anomalies=total_anomalies,
        total_potential_savings=impact['total_potential_savings'],
        critical_issues=critical_issues,
        high_priority_issues=high_priority,
        actions_pending=actions_pending,
        actions_completed=actions_completed,
        monthly_projection=projections['monthly'],
        yearly_projection=projections['yearly'],
        top_vendors=top_vendors,
        anomaly_distribution=anomaly_dist
    )


@router.get("/metrics")
async def get_metrics(days_back: int = 30, db: Session = Depends(get_db)):
    """Get detailed metrics for a time period."""
    start_date = DateHelper.get_period_start(days_back)
    end_date = DateHelper.get_period_end()

    transactions = db.query(Transaction).filter(
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).all()

    anomalies = db.query(Anomaly).filter(
        Anomaly.created_at >= start_date,
        Anomaly.created_at <= end_date
    ).all()

    trans_dicts = [
        {
            'vendor': t.vendor,
            'amount': t.amount,
            'category': t.category,
            'date': t.date
        }
        for t in transactions
    ]

    anom_dicts = [
        {
            'potential_savings': a.potential_savings,
            'anomaly_type': a.anomaly_type
        }
        for a in anomalies
    ]

    metrics = calculator.calculate_metrics_for_period(
        trans_dicts, anom_dicts, start_date, end_date
    )

    return metrics


@router.get("/top-vendors")
async def get_top_vendors(n: int = 10, db: Session = Depends(get_db)):
    """Get top vendor spending."""
    transactions = db.query(Transaction).all()
    
    trans_dicts = [
        {
            'vendor': t.vendor,
            'amount': t.amount,
            'category': t.category
        }
        for t in transactions
    ]

    vendor_metrics = aggregator.aggregate_by_vendor(trans_dicts)
    return aggregator.top_n_items(vendor_metrics, n=n)


@router.get("/category-breakdown")
async def get_category_breakdown(db: Session = Depends(get_db)):
    """Get spending breakdown by category."""
    transactions = db.query(Transaction).all()
    
    trans_dicts = [
        {
            'category': t.category,
            'amount': t.amount,
            'vendor': t.vendor
        }
        for t in transactions
    ]

    category_metrics = aggregator.aggregate_by_category(trans_dicts)
    return aggregator.top_n_items(category_metrics, n=100)
