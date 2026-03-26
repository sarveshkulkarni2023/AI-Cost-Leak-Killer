"""Root cause analysis service."""
import json
from typing import Dict, Any, Optional


class RootCauseAnalyzer:
    """Analyze root causes of detected anomalies."""

    RULES = {
        'duplicate': [
            'System error in billing system - automatic duplicate charge',
            'Manual data entry error resulted in duplicate transaction',
            'Billing service failure resulted in retry with duplicate charge',
            'Vendor sent duplicate invoice',
            'Business logic error in expense processing system'
        ],
        'outlier': [
            'Unauthorized or fraudulent transaction',
            'One-time unusual business expense',
            'Vendor price increase applied to single transaction',
            'Bulk order or rush fee added to normal Service',
            'Data entry error with incorrect amount'
        ],
        'vendor_anomaly': [
            'Vendor implemented dynamic pricing',
            'Vendor changed billing model or added fees',
            'Vendor overbilling or billing for unused services',
            'Multiple service tiers being charged concurrently',
            'Vendor contract modifications not updated in system'
        ],
        'pattern_anomaly': [
            'Subscription auto-renewal or usage-based increase',
            'Vendor migrated to tiered pricing model',
            'Service usage increased organically',
            'Vendor applied promotional pricing that expired',
            'Billing system configuration change or bug'
        ]
    }

    def analyze(self, anomaly: Dict[str, Any]) -> str:
        """Analyze anomaly and return root cause explanation."""
        anomaly_type = anomaly.get('anomaly_type', 'unknown')
        details = anomaly.get('details', {})

        # Get applicable rules
        rules = self.RULES.get(anomaly_type, ['Unknown cause'])

        # Select based on metadata clues
        root_cause = self._select_root_cause(anomaly_type, details, rules)
        return root_cause

    @staticmethod
    def _select_root_cause(anomaly_type: str, details: Dict[str, Any], rules: list) -> str:
        """Select most likely root cause based on details."""
        if anomaly_type == 'duplicate':
            # Duplicates are almost always system errors
            return 'Automatic duplicate charge - system error in billing processing'

        elif anomaly_type == 'outlier':
            z_score = details.get('z_score', 0)
            if abs(z_score) > 5:
                return 'Fraudulent or unauthorized transaction detected'
            else:
                return 'One-time unusual expense or data entry error'

        elif anomaly_type == 'vendor_anomaly':
            std_amount = details.get('std_amount', 0)
            mean_amount = details.get('mean_amount', 1)
            if std_amount > mean_amount * 2:
                return 'Vendor using dynamic pricing with high variance in charges'
            else:
                return 'Vendor billing inconsistency or service tier changes'

        elif anomaly_type == 'pattern_anomaly':
            deviation_factor = details.get('deviation_factor', 1)
            if deviation_factor > 3:
                return 'Sudden usage spike or subscription tier upgrade'
            else:
                return 'Gradual spending increase from vendor'

        return rules[0] if rules else 'Unknown root cause'


class ActionDecisionEngine:
    """Decide on corrective actions based on anomalies."""

    ACTION_RULES = {
        'duplicate': {
            'critical': [
                ('email', 'Send billing correction request to vendor'),
                ('flag', 'Flag transaction for immediate review'),
            ],
            'high': [
                ('email', 'Request credit for duplicate charge'),
                ('flag', 'Flag for investigation'),
            ],
            'medium': [
                ('email', 'Notify vendor of duplicate'),
            ],
            'low': [
                ('flag', 'Monitor for resolution'),
            ]
        },
        'outlier': {
            'critical': [
                ('flag', 'Flag for fraud investigation'),
                ('email', 'Alert finance team of suspicious transaction'),
            ],
            'high': [
                ('flag', 'Review transaction for authorization'),
                ('email', 'Verify transaction with requestor'),
            ],
            'medium': [
                ('flag', 'Review and approve if legitimate'),
            ],
            'low': [
                ('flag', 'Monitor for patterns'),
            ]
        },
        'vendor_anomaly': {
            'critical': [
                ('email', 'Request rate review and pricing audit'),
                ('negotiate', 'Initiate contract renegotiation'),
            ],
            'high': [
                ('email', 'Request pricing breakdown'),
            ],
            'medium': [
                ('email', 'Query vendor on pricing changes'),
            ],
            'low': []
        },
        'pattern_anomaly': {
            'critical': [
                ('email', 'Review vendor contract for scope changes'),
                ('negotiate', 'Initiate service review'),
            ],
            'high': [
                ('email', 'Review usage metrics with vendor'),
            ],
            'medium': [
                ('flag', 'Monitor for continued pattern'),
            ],
            'low': []
        }
    }

    def decide_actions(self, anomaly: Dict[str, Any], root_cause: str) -> list:
        """Decide what actions to take based on anomaly."""
        anomaly_type = anomaly.get('anomaly_type', 'unknown')
        severity = anomaly.get('severity', 'low')

        action_list = self.ACTION_RULES.get(anomaly_type, {}).get(severity, [])

        actions = []
        for action_type, description in action_list:
            actions.append({
                'action_type': action_type,
                'priority': severity,
                'description': description,
                'root_cause': root_cause,
                'estimated_savings': anomaly.get('potential_savings', 0)
            })

        return actions

    def generate_email_content(self, action: Dict[str, Any], anomaly: Dict[str, Any]) -> str:
        """Generate email content for actionable emails."""
        anomaly_type = anomaly.get('anomaly_type', 'unknown')
        description = anomaly.get('description', '')
        root_cause = action.get('root_cause', '')
        savings = anomaly.get('potential_savings', 0)

        templates = {
            'duplicate': f"""Subject: Duplicate Charge Resolution - Immediate Action Required

Dear Team,

We have detected a duplicate transaction in our billing records:

{description}

Root Cause: {root_cause}

Potential Savings: ${savings:,.2f}

Action Required:
1. Verify the duplicate charge with our billing system
2. Contact the vendor to confirm and request credit
3. Update the billing record once credit is applied

This charge should not have been applied. Please escalate to the vendor immediately.

Best regards,
AI Cost Leak Killer""",

            'outlier': f"""Subject: Unusual Transaction Detected - Review Required

Dear Finance Team,

An unusual transaction has been flagged for your review:

{description}

Analysis: The transaction amount is significantly higher than normal spending patterns.

Root Cause: {root_cause}

Potential Recovery: ${savings:,.2f}

Please verify:
1. Was this transaction properly authorized?
2. Was this a one-time expense or recurring?
3. If unauthorized or erroneous, please initiate chargeback/credit

Regards,
AI Cost Leak Killer""",

            'vendor_anomaly': f"""Subject: Vendor Pricing Review - Inconsistency Detected

Dear Procurement Team,

We've detected pricing inconsistencies in our {anomaly.get('details', {}).get('vendor', 'vendor')} account:

{description}

Root Cause: {root_cause}

Potential Savings: ${savings:,.2f}

Recommended Actions:
1. Request detailed pricing breakdown from vendor
2. Compare against market rates
3. Initiate contract renegotiation if rates are above market

Please schedule a review call with the vendor this week.

Best regards,
AI Cost Leak Killer""",

            'pattern_anomaly': f"""Subject: Spending Pattern Alert - Review with Vendor

Dear Team,

A spending pattern anomaly has been detected:

{description}

Root Cause Analysis: {root_cause}

Potential Savings: ${savings:,.2f}

Please review:
1. Recent changes to service usage or scope
2. Contract terms to verify pricing alignment
3. Discuss with vendor if charges are appropriate

Take action to prevent continued unexpected increases.

Best regards,
AI Cost Leak Killer"""
        }

        return templates.get(anomaly_type, f"Action Required: {description}\n\nRoot Cause: {root_cause}\n\nPotential Savings: ${savings:,.2f}")
