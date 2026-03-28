"""Anomalies page component."""
import streamlit as st
import pandas as pd
from api.client import APIClient


def render_anomalies_page():
    """Render the anomalies detection and review page."""
    st.title("🔍 Detect & Review Anomalies")
    st.markdown("Find and analyze cost anomalies in your transaction data")

    tab1, tab2, tab3 = st.tabs(["Detect Anomalies", "Review Anomalies", "Details"])

    with tab1:
        render_detect_tab()

    with tab2:
        render_review_tab()

    with tab3:
        render_details_tab()


def render_detect_tab():
    """Render anomaly detection tab."""
    st.subheader("Run Anomaly Detection")
    st.write("Analyze your transaction data using multiple detection methods:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Detection Methods:**
        - 🔄 **Duplicate Detection**: Identify exact duplicate transactions
        - 📊 **Outlier Detection**: Statistical anomalies (Isolation Forest)
        - 🏢 **Vendor Analysis**: Suspicious vendor patterns
        - 📈 **Pattern Detection**: Spending spike and trend anomalies
        """)

    with col2:
        st.markdown("""
        **What Gets Detected:**
        - Charging errors and duplicates
        - Unusual transaction amounts
        - Inconsistent vendor pricing
        - Spending spikes and patterns
        - Service overages
        """)

    st.divider()

    if st.button("▶️ Run Detection", type="primary", use_container_width=True):
        with st.spinner("Running anomaly detection... This may take a moment"):
            result = APIClient.detect_anomalies()

            if 'error' in result:
                st.error(f"Error: {result['error']}")
            else:
                detected = result.get('anomalies_detected', 0)
                savings = result.get('total_potential_savings', 0)

                if detected > 0:
                    st.success(f"✅ Detection Complete!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Anomalies Found", detected)
                    with col2:
                        st.metric("Potential Savings", f"${savings:,.2f}")

                    st.subheader("Detected Anomalies")
                    anomalies = result.get('anomalies', [])

                    if anomalies:
                        anom_df = pd.DataFrame(anomalies)
                        anom_df = anom_df.rename(columns={
                            'type': 'Anomaly Type',
                            'severity': 'Severity',
                            'confidence': 'Confidence',
                            'description': 'Description',
                            'savings': 'Potential Savings'
                        })
                        
                        st.dataframe(
                            anom_df.drop(['id', 'transaction_id'], axis=1, errors='ignore'),
                            use_container_width=True
                        )
                else:
                    st.info("✅ No anomalies detected - your spending looks healthy!")


def render_review_tab():
    """Render anomaly review tab."""
    st.subheader("Review Detected Anomalies")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "new", "investigating", "resolved", "ignored"],
            key="status_filter"
        )

    with col2:
        severity_filter = st.selectbox(
            "Filter by Severity",
            ["All", "critical", "high", "medium", "low"],
            key="severity_filter"
        )

    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    st.divider()

    # Get anomalies
    anomalies = APIClient.get_anomalies(
        status=None if status_filter == "All" else status_filter,
        severity=None if severity_filter == "All" else severity_filter
    )

    if not anomalies:
        st.info("No anomalies found with selected filters.")
        return

    # Display anomalies
    st.subheader(f"Found {len(anomalies)} Anomalies")

    for anomaly in anomalies:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown(f"### {anomaly.get('description', 'Unknown')}")
                st.caption(f"ID: {anomaly.get('id')} • Type: {anomaly.get('anomaly_type')} • Status: {anomaly.get('status')}")

            with col2:
                severity = anomaly.get('severity', 'low').upper()
                severity_color = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡',
                    'LOW': '🟢'
                }
                st.write(f"{severity_color.get(severity, '⚪')} {severity}")

            with col3:
                confidence = anomaly.get('confidence_score', 0)
                st.metric("Confidence", f"{confidence:.0%}")

            # Details
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Root Cause**: {anomaly.get('root_cause', 'Unknown')}")
                st.write(f"**Status**: {anomaly.get('status', 'Unknown')}")

            with col2:
                st.write(f"**Potential Savings**: ${anomaly.get('potential_savings', 0):,.2f}")
                st.write(f"**Created**: {anomaly.get('created_at', 'Unknown')[:10]}")

            # Action buttons
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("✅ Resolve", key=f"resolve_{anomaly.get('id')}"):
                    APIClient.update_anomaly(anomaly['id'], 'resolved')
                    st.success("Anomaly marked as resolved")
                    st.rerun()

            with col2:
                if st.button("🔍 Investigating", key=f"investigate_{anomaly.get('id')}"):
                    APIClient.update_anomaly(anomaly['id'], 'investigating')
                    st.info("Anomaly marked as investigating")
                    st.rerun()

            with col3:
                if st.button("❌ Ignore", key=f"ignore_{anomaly.get('id')}"):
                    APIClient.update_anomaly(anomaly['id'], 'ignored')
                    st.info("Anomaly marked as ignored")
                    st.rerun()


def render_details_tab():
    """Render detailed anomaly information."""
    st.subheader("Detailed Analysis")

    # Get all anomalies
    anomalies = APIClient.get_anomalies()

    if not anomalies:
        st.info("No anomalies to display.")
        return

    # Create detailed dataframe
    details_data = []
    for a in anomalies:
        details_data.append({
            'ID': a.get('id'),
            'Type': a.get('anomaly_type'),
            'Severity': a.get('severity'),
            'Confidence': f"{a.get('confidence_score', 0):.1%}",
            'Description': a.get('description'),
            'Root Cause': a.get('root_cause'),
            'Potential Savings': f"${a.get('potential_savings', 0):,.2f}",
            'Status': a.get('status'),
            'Created': a.get('created_at', '')[:10]
        })

    df = pd.DataFrame(details_data)
    st.dataframe(df, use_container_width=True, height=600)

    # Summary statistics
    st.divider()
    st.subheader("Summary Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        total_savings = sum(a.get('potential_savings', 0) for a in anomalies)
        st.metric("Total Potential Savings", f"${total_savings:,.2f}")

    with col2:
        avg_savings = total_savings / len(anomalies) if anomalies else 0
        st.metric("Average per Anomaly", f"${avg_savings:,.2f}")

    with col3:
        critical_count = len([a for a in anomalies if a.get('severity') == 'critical'])
        st.metric("Critical Issues", critical_count)
