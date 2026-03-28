"""Data validation and processing service."""
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple, Any


class DataValidator:
    """Validate and process incoming cost data."""

    REQUIRED_COLUMNS = {'vendor', 'amount', 'category', 'date', 'description'}
    
    VALID_CATEGORIES = {
        'cloud', 'software', 'consulting', 'infrastructure', 'support',
        'maintenance', 'licensing', 'security', 'monitoring', 'database',
        'networking', 'storage', 'compute', 'other'
    }

    @staticmethod
    def validate_csv(filepath: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Validate CSV file and return parsed data.
        Returns: (valid_records, error_messages)
        """
        errors = []
        valid_records = []

        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            return [], [f"Error reading CSV: {str(e)}"]

        # Check required columns
        missing_columns = DataValidator.REQUIRED_COLUMNS - set(df.columns)
        if missing_columns:
            return [], [f"Missing required columns: {missing_columns}"]

        # Validate each row
        for idx, row in df.iterrows():
            row_errors = []

            # Validate vendor
            if pd.isna(row['vendor']) or str(row['vendor']).strip() == '':
                row_errors.append(f"Row {idx + 1}: Vendor is required")
            
            # Validate amount
            try:
                amount = float(row['amount'])
                if amount <= 0:
                    row_errors.append(f"Row {idx + 1}: Amount must be positive")
            except (ValueError, TypeError):
                row_errors.append(f"Row {idx + 1}: Invalid amount format")
            
            # Validate category
            category = str(row['category']).lower().strip()
            if category not in DataValidator.VALID_CATEGORIES:
                row_errors.append(f"Row {idx + 1}: Invalid category (valid: {', '.join(DataValidator.VALID_CATEGORIES)})")
            
            # Validate date
            try:
                parsed_date = pd.to_datetime(row['date'])
                if parsed_date > datetime.utcnow():
                    row_errors.append(f"Row {idx + 1}: Date cannot be in the future")
            except:
                row_errors.append(f"Row {idx + 1}: Invalid date format (use YYYY-MM-DD)")
            
            # Validate description
            if pd.isna(row['description']):
                row_errors.append(f"Row {idx + 1}: Description is required")

            if row_errors:
                errors.extend(row_errors)
            else:
                # Build valid record
                try:
                    valid_records.append({
                        'vendor': str(row['vendor']).strip(),
                        'amount': float(row['amount']),
                        'category': str(row['category']).lower().strip(),
                        'date': pd.to_datetime(row['date']),
                        'description': str(row['description']).strip(),
                        'currency': str(row.get('currency', 'USD')).upper()
                    })
                except Exception as e:
                    errors.append(f"Row {idx + 1}: Error processing record - {str(e)}")

        return valid_records, errors

    @staticmethod
    def standardize_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize a single record."""
        return {
            'vendor': str(record.get('vendor', '')).strip().title(),
            'amount': float(record.get('amount', 0)),
            'category': str(record.get('category', 'other')).lower().strip(),
            'date': pd.to_datetime(record.get('date')),
            'description': str(record.get('description', '')).strip(),
            'currency': str(record.get('currency', 'USD')).upper()
        }
