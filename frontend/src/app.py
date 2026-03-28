"""Main Streamlit application."""
import streamlit as st
import sys
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="AI Cost Leak Killer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main { padding: 0 2rem; }
    .stMetric { background: #f5f5f5; padding: 1rem; border-radius: 0.5rem; }
    [data-testid="stTabs"] { margin-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("💰 Cost Leak Killer")
    st.markdown("---")
    
    st.markdown("""
    **AI-Powered Cost Anomaly Detection**
    
    Detect, analyze, and correct enterprise cost leakages.
    """)
    
    st.markdown("---")
    st.subheader("Navigation")
    
    page = st.radio(
        "Select a page:",
        options=[
            "📊 Dashboard",
            "📤 Upload Data",
            "🔍 Detect Anomalies",
            "⚡ Corrective Actions",
            "📋 Audit Logs"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.subheader("System Info")
    st.info("""
    **Backend Status**: ✅ Connected
    
    **Database**: SQLite
    
    **ML Engine**: Scikit-learn
    """)

# Route pages
if page == "📊 Dashboard":
    from pages.dashboard import render_dashboard_page
    render_dashboard_page()

elif page == "📤 Upload Data":
    from pages.upload import render_upload_page
    render_upload_page()

elif page == "🔍 Detect Anomalies":
    from pages.anomalies import render_anomalies_page
    render_anomalies_page()

elif page == "⚡ Corrective Actions":
    from pages.actions import render_actions_page
    render_actions_page()

elif page == "📋 Audit Logs":
    from pages.logs import render_logs_page
    render_logs_page()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem; color: #888;">
    <p>AI Cost Leak Killer v1.0 | Enterprise Cost Anomaly Detection</p>
    <p>© 2024 All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
