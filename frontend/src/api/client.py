"""API client for frontend."""
import requests
import streamlit as st
from typing import Dict, List, Any
import json
import os

API_BASE_URL = "http://localhost:8000/api"


class APIClient:
    """Client for interacting with the backend API."""

    @staticmethod
    def get_base_url() -> str:
        """Get API base URL from environment or default."""
        # Try environment variable first, then secrets, then default
        if "API_BASE_URL" in os.environ:
            return os.environ["API_BASE_URL"]
        
        # Check if secrets are available and configured
        try:
            if hasattr(st, 'secrets') and st.secrets:
                return st.secrets.get("API_BASE_URL", API_BASE_URL)
        except (AttributeError, FileNotFoundError):
            pass
        
        return API_BASE_URL

    @staticmethod
    def upload_csv(file) -> Dict[str, Any]:
        """Upload CSV file to backend."""
        try:
            files = {'file': (file.name, file, 'text/csv')}
            response = requests.post(
                f"{APIClient.get_base_url()}/upload",
                files=files,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            return {'error': 'Cannot connect to backend API'}
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def detect_anomalies() -> Dict[str, Any]:
        """Trigger anomaly detection."""
        try:
            response = requests.post(
                f"{APIClient.get_base_url()}/detect-anomalies",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def get_anomalies(status: str = None, severity: str = None) -> List[Dict[str, Any]]:
        """Get detected anomalies."""
        try:
            params = {}
            if status:
                params['status'] = status
            if severity:
                params['severity'] = severity
            
            response = requests.get(
                f"{APIClient.get_base_url()}/anomalies",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error fetching anomalies: {str(e)}")
            return []

    @staticmethod
    def get_dashboard_summary() -> Dict[str, Any]:
        """Get dashboard summary."""
        try:
            response = requests.get(
                f"{APIClient.get_base_url()}/summary",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error fetching summary: {str(e)}")
            return {}

    @staticmethod
    def get_actions(status: str = None) -> List[Dict[str, Any]]:
        """Get action items."""
        try:
            params = {}
            if status:
                params['status'] = status
            
            response = requests.get(
                f"{APIClient.get_base_url()}/actions",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error fetching actions: {str(e)}")
            return []

    @staticmethod
    def generate_actions() -> Dict[str, Any]:
        """Generate corrective actions."""
        try:
            response = requests.post(
                f"{APIClient.get_base_url()}/generate-actions",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def execute_action(action_id: int) -> Dict[str, Any]:
        """Execute a specific action."""
        try:
            response = requests.post(
                f"{APIClient.get_base_url()}/actions/{action_id}/execute",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def update_anomaly(anomaly_id: int, status: str = None) -> Dict[str, Any]:
        """Update anomaly status."""
        try:
            params = {}
            if status:
                params['status'] = status
            
            response = requests.patch(
                f"{APIClient.get_base_url()}/anomalies/{anomaly_id}",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def get_logs(limit: int = 50) -> List[Dict[str, Any]]:
        """Get audit logs."""
        try:
            response = requests.get(
                f"{APIClient.get_base_url()}/logs",
                params={'limit': limit},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error fetching logs: {str(e)}")
            return []

    @staticmethod
    def get_metrics(days_back: int = 30) -> Dict[str, Any]:
        """Get financial metrics."""
        try:
            response = requests.get(
                f"{APIClient.get_base_url()}/metrics",
                params={'days_back': days_back},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error fetching metrics: {str(e)}")
            return {}
