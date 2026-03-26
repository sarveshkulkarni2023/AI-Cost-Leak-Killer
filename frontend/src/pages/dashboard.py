"""Dashboard page component."""
import streamlit as st
import pandas as pd
from api.client import APIClient
import plotly.express as px
import plotly.graph_objects as go


def render_dashboard_page():
    """Render the main dashboard page."""
    st.title("📊 Dashboard")
    st.markdown("Overview of cost leakages and financial impact")

    # Refresh button
    col1, col2 = st.columns([0.9, 0.1])
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    # Get summary data
    summary = APIClient.get_dashboard_summary()

    if not summary:
        st.warning("No data available. Please upload transaction data first.")
        return

    # Key metrics
    st.subheader("Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total Transactions",
            f"{summary.get('total_transactions', 0):,}"
        )

    with col2:
        anomalies = summary.get('total_anomalies', 0)
        st.metric(
            "Anomalies Detected",
            f"{anomalies:,}",
            delta=f"{anomalies} issues"
        )

    with col3:
        savings = summary.get('total_potential_savings', 0)
        st.metric(
            "Potential Savings",
            f"${savings:,.2f}",
            delta=f"Recoverable"
        )

    with col4:
        urgent = summary.get('critical_issues', 0)
        st.metric(
            "🔴 Critical Issues",
            f"{urgent}",
            delta="Requires immediate action" if urgent > 0 else "None"
        )

    with col5:
        high = summary.get('high_priority_issues', 0)
        st.metric(
            "🟠 High Priority",
            f"{high}",
            delta="Review needed" if high > 0 else "None"
        )

    st.divider()

    # Financial Projections
    col1, col2, col3 = st.columns(3)

    with col1:
        monthly = summary.get('monthly_projection', 0)
        st.metric(
            "📅 Monthly Leakage Projection",
            f"${monthly:,.2f}",
            help="Projected monthly cost leakage based on detected anomalies"
        )

    with col2:
        yearly = summary.get('yearly_projection', 0)
        st.metric(
            "📆 Yearly Leakage Projection",
            f"${yearly:,.2f}",
            help="Projected yearly cost leakage based on detected anomalies"
        )

    with col3:
        actions_pending = summary.get('actions_pending', 0)
        st.metric(
            "⏳ Actions Pending",
            f"{actions_pending}",
            help="Corrective actions awaiting execution"
        )

    st.divider()

    # Visualizations
    col1, col2 = st.columns(2)

    # Top Vendors
    with col1:
        st.subheader("💰 Top Spending Vendors")
        top_vendors = summary.get('top_vendors', [])
        if top_vendors:
            vendors_df = pd.DataFrame(top_vendors).head(10)
            vendors_df['total'] = vendors_df['total'].astype(float)
            
            fig = px.bar(
                vendors_df,
                x='total',
                y='name',
                orientation='h',
                title='Top 10 Vendors by Spending'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No vendor data available")

    # Anomaly Distribution
    with col2:
        st.subheader("🎯 Anomaly Distribution")
        anom_dist = summary.get('anomaly_distribution', {})
        if anom_dist:
            fig = px.pie(
                values=list(anom_dist.values()),
                names=list(anom_dist.keys()),
                title='Anomalies by Type'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No anomalies detected yet")

    st.divider()

    # Action Items Summary
    st.subheader("📋 Action Items Summary")
    col1, col2, col3 = st.columns(3)

    with col1:
        pending = summary.get('actions_pending', 0)
        st.info(f"⏳ **Pending**: {pending} actions")

    with col2:
        completed = summary.get('actions_completed', 0)
        st.success(f"✅ **Completed**: {completed} actions")

    with col3:
        total_actions = pending + completed
        st.metric("Total Actions", total_actions)

    st.divider()

    # Next Steps
    st.subheader("🚀 Next Steps")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔍 Detect Anomalies", use_container_width=True, type="primary"):
            st.switch_page("pages/anomalies.py")

    with col2:
        if st.button("⚡ Generate Actions", use_container_width=True):
            st.switch_page("pages/actions.py")

    with col3:
        if st.button("📤 Upload More Data", use_container_width=True):
            st.switch_page("pages/upload.py")
