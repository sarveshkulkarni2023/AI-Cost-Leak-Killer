"""Actions page component."""
import streamlit as st
import pandas as pd
from api.client import APIClient


def render_actions_page():
    """Render the actions management page."""
    st.title("⚡ Corrective Actions")
    st.markdown("Generate and execute corrective actions for detected anomalies")

    tab1, tab2, tab3 = st.tabs(["Generate Actions", "Review Actions", "Execute"])

    with tab1:
        render_generate_tab()

    with tab2:
        render_review_tab()

    with tab3:
        render_execute_tab()


def render_generate_tab():
    """Render action generation tab."""
    st.subheader("Generate Corrective Actions")
    st.write("""
    The system will automatically generate appropriate corrective actions based on:
    - Anomaly type and severity
    - Root cause analysis
    - Potential savings estimation
    - Risk level and priority
    """)

    action_types = {
        '📧 Email': 'Send notification/correction request to vendor',
        '🚩 Flag': 'Flag transaction for manual review',
        '💬 Negotiate': 'Initiate pricing negotiation with vendor',
        '❌ Cancel': 'Request service cancellation'
    }

    st.markdown("**Potential Actions:**")
    for action, desc in action_types.items():
        st.write(f"  • {action}: {desc}")

    st.divider()

    if st.button("📋 Generate Actions", type="primary", use_container_width=True):
        with st.spinner("Generating corrective actions..."):
            result = APIClient.generate_actions()

            if 'error' in result:
                st.error(f"Error: {result['error']}")
            else:
                generated = result.get('actions_generated', 0)
                savings = result.get('total_estimated_savings', 0)

                if generated > 0:
                    st.success(f"✅ Actions Generated!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Actions Created", generated)
                    with col2:
                        st.metric("Est. Total Savings", f"${savings:,.2f}")
                    
                    st.info("Review and execute actions in the **Review Actions** tab")
                else:
                    st.info("No new actions needed at this time.")


def render_review_tab():
    """Render action review tab."""
    st.subheader("Review & Manage Actions")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "pending", "in_progress", "completed", "failed"],
            key="action_status_filter"
        )

    with col2:
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["All", "critical", "high", "medium", "low"],
            key="action_priority_filter"
        )

    with col3:
        if st.button("🔄 Refresh", use_container_width=True, key="actions_refresh"):
            st.rerun()

    st.divider()

    # Get actions
    actions = APIClient.get_actions(
        status=None if status_filter == "All" else status_filter
    )

    if not actions:
        st.info("No actions found with selected filters.")
        return

    st.subheader(f"Found {len(actions)} Actions")

    for action in actions:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                action_type = action.get('action_type', 'unknown').upper()
                st.markdown(f"### {action_type} to {action.get('recipient', 'System')}")
                st.caption(f"Action ID: {action.get('id')} • Status: {action.get('status')}")

            with col2:
                priority = action.get('priority', 'low').upper()
                priority_color = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡',
                    'LOW': '🟢'
                }
                st.write(f"{priority_color.get(priority, '⚪')} {priority}")

            with col3:
                executed = "✅ Done" if action.get('executed') else "⏳ Pending"
                st.write(f"**{executed}**")

            # Content preview
            content = action.get('content', '')
            if content:
                with st.expander("View Content"):
                    st.text(content[:500])

            # Details
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Est. Savings**: ${action.get('estimated_savings', 0):,.2f}")

            with col2:
                st.write(f"**Created**: {action.get('created_at', 'Unknown')[:10]}")

            # Action buttons
            col1, col2, col3 = st.columns(3)

            with col1:
                if not action.get('executed'):
                    if st.button("✅ Execute", key=f"execute_{action.get('id')}"):
                        with st.spinner("Executing action..."):
                            result = APIClient.execute_action(action['id'])
                            if 'error' not in result:
                                st.success(f"Action executed: {result.get('result', 'Done')}")
                                st.rerun()
                            else:
                                st.error(f"Error: {result['error']}")

            with col2:
                if action.get('status') != 'completed':
                    if st.button("⏳ In Progress", key=f"inprogress_{action.get('id')}"):
                        st.info("Action marked as in progress")

            with col3:
                if st.button("📝 Edit", key=f"edit_{action.get('id')}"):
                    st.write("Edit functionality would be implemented here")


def render_execute_tab():
    """Render execution summary tab."""
    st.subheader("Execution Summary & History")

    # Get completed actions
    completed_actions = APIClient.get_actions(status='completed')

    if not completed_actions:
        st.info("No completed actions yet.")
        return

    st.metric("Completed Actions", len(completed_actions))

    # Summary table
    exec_data = []
    total_savings = 0

    for action in completed_actions:
        exec_data.append({
            'ID': action.get('id'),
            'Type': action.get('action_type'),
            'Priority': action.get('priority'),
            'Est. Savings': f"${action.get('estimated_savings', 0):,.2f}",
            'Status': action.get('status'),
            'Result': action.get('execution_result', 'N/A')[:50],
            'Executed': action.get('created_at', '')[:10]
        })
        total_savings += action.get('estimated_savings', 0)

    st.divider()
    st.metric("Total Potential Savings from Completed Actions", f"${total_savings:,.2f}")

    df = pd.DataFrame(exec_data)
    st.dataframe(df, use_container_width=True, height=400)

    # Export data
    st.divider()
    st.subheader("Export Data")

    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Actions Report (CSV)",
        data=csv,
        file_name="actions_report.csv",
        mime="text/csv"
    )
