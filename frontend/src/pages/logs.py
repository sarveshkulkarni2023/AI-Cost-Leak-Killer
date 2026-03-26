"""Audit logs page component."""
import streamlit as st
import pandas as pd
from api.client import APIClient


def render_logs_page():
    """Render the audit logs page."""
    st.title("📋 Audit Logs")
    st.markdown("Complete audit trail of all system decisions and actions")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        event_type_filter = st.selectbox(
            "Filter by Event Type",
            ["All", "detection", "analysis", "action", "resolution", "user_action"],
            key="event_type_filter"
        )

    with col2:
        entity_type_filter = st.selectbox(
            "Filter by Entity Type",
            ["All", "anomaly", "action", "transaction"],
            key="entity_type_filter"
        )

    with col3:
        limit = st.slider("Show last N records", 10, 500, 100, key="log_limit")

    st.divider()

    # Get logs
    logs = APIClient.get_logs(limit=limit)

    if not logs:
        st.info("No audit logs found.")
        return

    # Display logs
    st.subheader(f"Showing {len(logs)} Recent Audit Events")

    for log in logs:
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

            with col1:
                st.markdown(f"**{log.get('event_description', 'Unknown Event')}**")

            with col2:
                event_type = log.get('event_type', 'unknown').upper()
                st.caption(f"Event: {event_type}")

            with col3:
                entity_type = log.get('entity_type', 'unknown')
                entity_id = log.get('entity_id', '?')
                st.caption(f"Entity: {entity_type} #{entity_id}")

            with col4:
                timestamp = log.get('timestamp', 'Unknown')
                if timestamp:
                    timestamp = timestamp[:19]
                st.caption(f"Time: {timestamp}")

            # Additional details
            if log.get('metadata'):
                with st.expander("View Details"):
                    st.json(log.get('metadata', {}))

    st.divider()

    # Log statistics
    st.subheader("Audit Log Statistics")

    stats = APIClient.get_logs(limit=1000)  # Get more logs for stats
    if stats:
        event_counts = {}
        for log in stats:
            event_type = log.get('event_type', 'unknown')
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Audit Events", len(stats))

        with col2:
            st.metric("Unique Event Types", len(event_counts))

        st.markdown("**Event Type Distribution:**")
        for event_type, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True):
            st.write(f"  • {event_type}: {count}")

    # Export audit logs
    st.divider()
    st.subheader("Export Audit Trail")

    if logs:
        export_data = []
        for log in logs:
            export_data.append({
                'ID': log.get('id'),
                'Event Type': log.get('event_type'),
                'Description': log.get('event_description'),
                'Entity Type': log.get('entity_type'),
                'Entity ID': log.get('entity_id'),
                'User Action': log.get('user_action'),
                'Timestamp': log.get('timestamp')
            })

        df = pd.DataFrame(export_data)
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Audit Logs (CSV)",
            data=csv,
            file_name="audit_logs.csv",
            mime="text/csv"
        )
