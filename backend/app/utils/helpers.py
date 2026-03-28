"""Utility functions and helpers."""
import os
from datetime import datetime, timedelta
from typing import Optional


class FileHandler:
    """Handle file operations."""

    UPLOAD_DIR = os.getenv('UPLOAD_DIR', './uploads')

    @classmethod
    def ensure_upload_dir(cls):
        """Ensure upload directory exists."""
        if not os.path.exists(cls.UPLOAD_DIR):
            os.makedirs(cls.UPLOAD_DIR)

    @classmethod
    def save_upload(cls, filename: str, content: bytes) -> str:
        """Save uploaded file and return path."""
        cls.ensure_upload_dir()
        filepath = os.path.join(cls.UPLOAD_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(content)
        return filepath

    @classmethod
    def delete_file(cls, filepath: str):
        """Delete a file if it exists."""
        if os.path.exists(filepath):
            os.remove(filepath)


class DateHelper:
    """Date/time utility functions."""

    @staticmethod
    def get_period_start(days_back: int = 30) -> datetime:
        """Get start date for a period."""
        return datetime.utcnow() - timedelta(days=days_back)

    @staticmethod
    def get_period_end() -> datetime:
        """Get end date (now)."""
        return datetime.utcnow()

    @staticmethod
    def format_date(dt: datetime) -> str:
        """Format datetime for display."""
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def is_business_day(dt: datetime) -> bool:
        """Check if date is a business day."""
        return dt.weekday() < 5  # Monday = 0, Sunday = 6


class SeverityCalculator:
    """Calculate and determine severity levels."""

    SEVERITY_WEIGHTS = {
        'duplicate': 0.9,      # High priority
        'outlier': 0.7,         # Medium-high
        'vendor_anomaly': 0.6,  # Medium
        'pattern_anomaly': 0.5  # Medium-low
    }

    @staticmethod
    def calculate_priority_score(
        anomaly_type: str,
        confidence_score: float,
        potential_savings: float,
        recurring: bool = False
    ) -> float:
        """Calculate priority score (0-100)."""
        type_weight = SeverityCalculator.SEVERITY_WEIGHTS.get(anomaly_type, 0.5)
        
        # Base score from type and confidence
        base_score = type_weight * confidence_score * 100
        
        # Boost for recurring issues
        if recurring:
            base_score *= 1.5
        
        # Boost for high potential savings
        if potential_savings > 10000:
            base_score *= 1.3
        
        return min(base_score, 100)  # Cap at 100

    @staticmethod
    def get_action_priority(severity: str) -> str:
        """Map severity to action priority."""
        mapping = {
            'critical': 'critical',
            'high': 'high',
            'medium': 'medium',
            'low': 'low'
        }
        return mapping.get(severity, 'low')


class MetricsAggregator:
    """Aggregate metrics across datasets."""

    @staticmethod
    def aggregate_by_vendor(transactions) -> dict:
        """Aggregate spending metrics by vendor."""
        vendor_metrics = {}
        for trans in transactions:
            vendor = trans.get('vendor', 'unknown')
            if vendor not in vendor_metrics:
                vendor_metrics[vendor] = {
                    'count': 0,
                    'total': 0,
                    'min': float('inf'),
                    'max': 0
                }
            
            amount = trans.get('amount', 0)
            vendor_metrics[vendor]['count'] += 1
            vendor_metrics[vendor]['total'] += amount
            vendor_metrics[vendor]['min'] = min(vendor_metrics[vendor]['min'], amount)
            vendor_metrics[vendor]['max'] = max(vendor_metrics[vendor]['max'], amount)
        
        # Calculate averages
        for vendor in vendor_metrics:
            if vendor_metrics[vendor]['count'] > 0:
                vendor_metrics[vendor]['avg'] = vendor_metrics[vendor]['total'] / vendor_metrics[vendor]['count']
            else:
                vendor_metrics[vendor]['avg'] = 0
        
        return vendor_metrics

    @staticmethod
    def aggregate_by_category(transactions) -> dict:
        """Aggregate spending metrics by category."""
        category_metrics = {}
        for trans in transactions:
            category = trans.get('category', 'unknown')
            if category not in category_metrics:
                category_metrics[category] = {
                    'count': 0,
                    'total': 0
                }
            
            category_metrics[category]['count'] += 1
            category_metrics[category]['total'] += trans.get('amount', 0)
        
        return category_metrics

    @staticmethod
    def top_n_items(items_dict: dict, n: int = 5, key: str = 'total') -> list:
        """Get top N items from aggregated metrics."""
        sorted_items = sorted(
            items_dict.items(),
            key=lambda x: x[1].get(key, 0),
            reverse=True
        )
        return [{'name': name, **metrics} for name, metrics in sorted_items[:n]]
