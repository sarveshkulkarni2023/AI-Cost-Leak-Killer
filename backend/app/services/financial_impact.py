"""Financial impact calculation service."""
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd


class FinancialImpactCalculator:
    """Calculate financial impact of detected anomalies."""

    @staticmethod
    def calculate_impact(anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate total financial impact."""
        total_potential_savings = sum(a.get('potential_savings', 0) for a in anomalies)
        
        severity_breakdown = {
            'critical': sum(a.get('potential_savings', 0) for a in anomalies if a.get('severity') == 'critical'),
            'high': sum(a.get('potential_savings', 0) for a in anomalies if a.get('severity') == 'high'),
            'medium': sum(a.get('potential_savings', 0) for a in anomalies if a.get('severity') == 'medium'),
            'low': sum(a.get('potential_savings', 0) for a in anomalies if a.get('severity') == 'low'),
        }

        anomaly_type_breakdown = {}
        for anom in anomalies:
            atype = anom.get('anomaly_type', 'unknown')
            if atype not in anomaly_type_breakdown:
                anomaly_type_breakdown[atype] = 0
            anomaly_type_breakdown[atype] += anom.get('potential_savings', 0)

        return {
            'total_potential_savings': total_potential_savings,
            'by_severity': severity_breakdown,
            'by_type': anomaly_type_breakdown,
            'average_per_anomaly': total_potential_savings / len(anomalies) if anomalies else 0
        }

    @staticmethod
    def calculate_projections(
        transactions: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]],
        period_days: int = 30
    ) -> Dict[str, float]:
        """Calculate monthly and yearly financial projections."""
        if not transactions:
            return {'monthly': 0, 'yearly': 0, 'daily_average': 0}

        # Calculate average daily spending
        total_spending = sum(t.get('amount', 0) for t in transactions)
        daily_average = total_spending / max(period_days, 1)
        monthly_average = daily_average * 30
        yearly_average = monthly_average * 12

        # Calculate projected impact if anomalies continue
        anomaly_impact = sum(a.get('potential_savings', 0) for a in anomalies)

        # Assume anomalies represent 10% of actual issues discovered
        estimated_total_leakage_daily = anomaly_impact / max(period_days, 1) / 0.1

        return {
            'monthly': estimated_total_leakage_daily * 30,
            'yearly': estimated_total_leakage_daily * 365,
            'daily_average': estimated_total_leakage_daily,
            'total_spending_monthly': monthly_average,
            'total_spending_yearly': yearly_average
        }

    @staticmethod
    def calculate_metrics_for_period(
        transactions: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate comprehensive financial metrics for a period."""
        df_trans = pd.DataFrame(transactions) if transactions else pd.DataFrame()
        df_anom = pd.DataFrame(anomalies) if anomalies else pd.DataFrame()

        if not df_trans.empty:
            df_trans['date'] = pd.to_datetime(df_trans['date'])
            period_trans = df_trans[
                (df_trans['date'] >= start_date) & (df_trans['date'] <= end_date)
            ]
        else:
            period_trans = pd.DataFrame()

        total_potential_savings = df_anom.get('potential_savings', 0).sum() if not df_anom.empty else 0
        period_days = (end_date - start_date).days + 1

        return {
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'total_anomalies_detected': len(df_anom),
            'total_potential_savings': total_potential_savings,
            'realized_savings': 0,  # Updated when actions are resolved
            'monthly_projection': (total_potential_savings / max(period_days, 1)) * 30,
            'yearly_projection': (total_potential_savings / max(period_days, 1)) * 365,
            'top_vendor': df_trans['vendor'].value_counts().index[0] if not df_trans.empty and len(df_trans) > 0 else 'N/A',
            'top_category': df_trans['category'].value_counts().index[0] if not df_trans.empty and len(df_trans) > 0 else 'N/A',
            'anomaly_distribution': df_anom['anomaly_type'].value_counts().to_dict() if not df_anom.empty else {}
        }
