"""Anomaly detection service using machine learning."""
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta


class AnomalyDetector:
    """Detect anomalies in cost data using multiple techniques."""

    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()

    def detect_duplicates(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect duplicate or near-duplicate transactions."""
        anomalies = []
        df = pd.DataFrame(transactions)

        if df.empty:
            return anomalies

        # Check for exact duplicates
        exact_duplicates = df[df.duplicated(subset=['vendor', 'amount', 'date'], keep=False)]
        for idx, row in exact_duplicates.iterrows():
            anomalies.append({
                'transaction_id': row['id'],
                'anomaly_type': 'duplicate',
                'confidence_score': 0.95,
                'severity': 'high',
                'description': f"Duplicate transaction: {row['vendor']} - ${row['amount']} on {row['date']}",
                'root_cause': 'System error or data entry duplicate',
                'potential_savings': row['amount'],
                'details': {
                    'vendor': row['vendor'],
                    'amount': float(row['amount']),
                    'duplicate_count': len(exact_duplicates[
                        (exact_duplicates['vendor'] == row['vendor']) &
                        (exact_duplicates['amount'] == row['amount'])
                    ])
                }
            })

        return anomalies

    def detect_outliers(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect statistical outliers using Z-score method."""
        anomalies = []
        df = pd.DataFrame(transactions)

        if len(df) < 5:  # Need minimum samples
            return anomalies

        try:
            # Simple z-score based detection for amount
            df['amount_zscore'] = np.abs((df['amount'] - df['amount'].mean()) / (df['amount'].std() + 1e-8))
            
            # Flag significant outliers (z-score > 2.5)
            outliers = df[df['amount_zscore'] > 2.5]
            
            for idx, row in outliers.iterrows():
                z_score = row['amount_zscore']
                anomalies.append({
                    'transaction_id': int(row['id']),
                    'anomaly_type': 'outlier',
                    'confidence_score': min(0.95, 0.85 + (z_score / 10)),  # Higher z-score = higher confidence
                    'severity': 'high' if z_score > 3.0 else 'medium',
                    'description': f"Unusual transaction amount: ${row['amount']} from {row['vendor']}",
                    'root_cause': 'Statistical anomaly - significantly different from normal spending pattern',
                    'potential_savings': float(row['amount'] * 0.3),
                    'details': {
                        'vendor': row['vendor'],
                        'amount': float(row['amount']),
                        'avg_vendor_amount': float(df[df['vendor'] == row['vendor']]['amount'].mean()),
                        'z_score': float(z_score)
                    }
                })
        except Exception as e:
            print(f"Error in outlier detection: {str(e)}")

        return anomalies

    def detect_vendor_anomalies(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies at vendor level."""
        anomalies = []
        df = pd.DataFrame(transactions)

        if df.empty:
            return anomalies

        # Group by vendor
        vendor_stats = df.groupby('vendor').agg({
            'amount': ['sum', 'count', 'mean', 'std'],
            'id': 'first'
        }).reset_index()
        vendor_stats.columns = ['vendor', 'total_amount', 'transaction_count', 'mean_amount', 'std_amount', 'sample_id']

        # Find suspicious vendors
        for idx, vs in vendor_stats.iterrows():
            if vs['transaction_count'] < 3:
                continue

            # High variance in transactions from same vendor
            if vs['std_amount'] > vs['mean_amount']:
                vendor_trans = df[df['vendor'] == vs['vendor']]
                sample_transaction = vendor_trans.iloc[0]
                anomalies.append({
                    'transaction_id': int(sample_transaction['id']),
                    'anomaly_type': 'vendor_anomaly',
                    'confidence_score': 0.75,
                    'severity': 'medium',
                    'description': f"Suspicious vendor pattern: {vs['vendor']} (High variance in transaction amounts)",
                    'root_cause': 'Vendor may be overcharging or billing inconsistently',
                    'potential_savings': vs['total_amount'] * 0.15,
                    'details': {
                        'vendor': vs['vendor'],
                        'total_amount': float(vs['total_amount']),
                        'transaction_count': int(vs['transaction_count']),
                        'mean_amount': float(vs['mean_amount']),
                        'std_amount': float(vs['std_amount'])
                    }
                })

        return anomalies

    def detect_pattern_anomalies(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalous patterns like sudden spending increases."""
        anomalies = []
        df = pd.DataFrame(transactions)

        if len(df) < 5:
            return anomalies

        df['date'] = pd.to_datetime(df['date'])
        df_sorted = df.sort_values('date')

        # Check for spending spikes per vendor
        for vendor in df_sorted['vendor'].unique():
            vendor_df = df_sorted[df_sorted['vendor'] == vendor].copy()
            if len(vendor_df) < 3:
                continue

            # Calculate rolling average
            vendor_df['rolling_avg'] = vendor_df['amount'].rolling(window=3, min_periods=1).mean()
            vendor_df['deviation'] = vendor_df['amount'] / (vendor_df['rolling_avg'] + 1)

            # Find deviations > 2x
            spikes = vendor_df[vendor_df['deviation'] > 2.0]
            for idx, row in spikes.iterrows():
                anomalies.append({
                    'transaction_id': int(row['id']),
                    'anomaly_type': 'pattern_anomaly',
                    'confidence_score': 0.80,
                    'severity': 'medium',
                    'description': f"Spending spike detected from {row['vendor']}: ${row['amount']} (2x+ normal)",
                    'root_cause': 'Unusual increase in spending from this vendor',
                    'potential_savings': row['amount'] * 0.2,
                    'details': {
                        'vendor': row['vendor'],
                        'amount': float(row['amount']),
                        'rolling_avg': float(row['rolling_avg']),
                        'deviation_factor': float(row['deviation'])
                    }
                })

        return anomalies

    @staticmethod
    def _calculate_severity(amount: float, all_amounts: pd.Series) -> str:
        """Calculate severity based on amount vs mean."""
        mean = all_amounts.mean()
        if amount > mean * 3:
            return 'critical'
        elif amount > mean * 2:
            return 'high'
        elif amount > mean * 1.5:
            return 'medium'
        return 'low'

    def detect_all_anomalies(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run all detection methods and return combined results."""
        all_anomalies = []
        
        try:
            all_anomalies.extend(self.detect_duplicates(transactions))
        except Exception as e:
            print(f"Duplicate detection error: {e}")
        
        try:
            all_anomalies.extend(self.detect_outliers(transactions))
        except Exception as e:
            print(f"Outlier detection error: {e}")
        
        try:
            all_anomalies.extend(self.detect_vendor_anomalies(transactions))
        except Exception as e:
            print(f"Vendor detection error: {e}")
        
        try:
            all_anomalies.extend(self.detect_pattern_anomalies(transactions))
        except Exception as e:
            print(f"Pattern detection error: {e}")

        # Remove duplicates (same transaction detected multiple ways)
        seen_ids = set()
        unique_anomalies = []
        for anom in all_anomalies:
            if anom['transaction_id'] not in seen_ids:
                unique_anomalies.append(anom)
                seen_ids.add(anom['transaction_id'])

        return unique_anomalies
