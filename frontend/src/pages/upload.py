"""Upload page component."""
import streamlit as st
import pandas as pd
from api.client import APIClient
import io


def render_upload_page():
    """Render the data upload page."""
    st.title("📤 Data Upload")
    st.markdown("Upload your cost/transaction CSV files for anomaly detection")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("CSV Requirements")
        st.markdown("""
        Your CSV file must contain the following columns:
        - **vendor**: Name of the vendor/service provider
        - **amount**: Transaction amount (numeric)
        - **category**: Cost category (cloud, software, consulting, infrastructure, etc.)
        - **date**: Transaction date (YYYY-MM-DD format)
        - **description**: Transaction description
        - **currency**: (Optional) Currency code (default: USD)
        """)

    with col2:
        st.subheader("Sample Data")
        sample_data = {
            'vendor': ['AWS', 'Microsoft', 'Slack'],
            'amount': [1500.00, 2000.00, 500.00],
            'category': ['cloud', 'software', 'software'],
            'date': ['2024-03-01', '2024-03-02', '2024-03-03'],
            'description': ['Cloud computing', 'Office 365', 'Team communication']
        }
        st.dataframe(pd.DataFrame(sample_data), use_container_width=True)

    st.divider()

    # Create two tabs: File Upload and Sample Data
    tab1, tab2 = st.tabs(["Upload CSV", "Load Sample Data"])

    with tab1:
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

        if uploaded_file is not None:
            st.info(f"File selected: {uploaded_file.name}")
            
            # Show preview
            try:
                df_preview = pd.read_csv(uploaded_file)
                st.subheader("Preview")
                st.dataframe(df_preview.head(10), use_container_width=True)
                
                if st.button("Upload to System", type="primary", key="upload_real"):
                    with st.spinner("Uploading and validating..."):
                        uploaded_file.seek(0)
                        result = APIClient.upload_csv(uploaded_file)
                        
                        if 'error' in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            st.success(f"✅ Upload Successful!")
                            st.metric("Records Uploaded", result.get('records_uploaded', 0))
                            st.metric("Records Rejected", result.get('records_rejected', 0))
                            
                            if result.get('validation_errors'):
                                st.warning("Validation Errors:")
                                for error in result['validation_errors'][:10]:
                                    st.write(f"  • {error}")
                                if len(result['validation_errors']) > 10:
                                    st.write(f"  ... and {len(result['validation_errors']) - 10} more")
                            
                            st.info("Next: Go to **Detect Anomalies** to analyze the data")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

    with tab2:
        st.subheader("Load Sample Dataset")
        st.write("Click below to load a sample dataset for demonstration")
        
        if st.button("Load Sample Data", type="secondary", key="load_sample"):
            # Create sample data
            sample_csv = create_sample_csv()
            
            # Upload sample data
            with st.spinner("Uploading sample data..."):
                # Create a file-like object
                sample_file = io.BytesIO(sample_csv.encode())
                sample_file.name = "sample_data.csv"
                
                result = APIClient.upload_csv(sample_file)
                
                if 'error' in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success(f"✅ Sample Data Loaded!")
                    st.metric("Records Uploaded", result.get('records_uploaded', 0))
                    st.info("Sample data includes intentional anomalies for demonstration")
                    st.info("Next: Go to **Detect Anomalies** to analyze the data")


def create_sample_csv() -> str:
    """Create sample CSV data with intentional anomalies."""
    csv_data = """vendor,amount,category,date,description
AWS,1500.00,cloud,2024-03-01,Monthly cloud computing
AWS,1500.00,cloud,2024-03-01,Monthly cloud computing
Microsoft,2000.00,software,2024-03-02,Office 365 licensing
Slack,500.00,software,2024-03-03,Team communication platform
AWS,15000.00,cloud,2024-03-05,Unusual spike - large deployment
Zoom,300.00,software,2024-03-06,Video conferencing
GitHub,50.00,software,2024-03-07,Repository hosting
AWS,1600.00,cloud,2024-03-08,Monthly cloud computing
DataDog,1200.00,monitoring,2024-03-09,Application monitoring
Salesforce,3000.00,software,2024-03-10,CRM platform
AWS,1500.00,cloud,2024-03-11,Monthly cloud computing
Stripe,500.00,infrastructure,2024-03-12,Payment processing
New Relic,800.00,monitoring,2024-03-13,Application performance monitoring
AWS,1500.00,cloud,2024-03-14,Monthly cloud computing
Google Cloud,2000.00,cloud,2024-03-15,GCP charges
Twilio,400.00,infrastructure,2024-03-16,Communication APIs
PagerDuty,600.00,infrastructure,2024-03-17,Incident management
AWS,1500.00,cloud,2024-03-18,Monthly cloud computing
Jira,800.00,software,2024-03-19,Project management
ServiceNow,2500.00,software,2024-03-20,ITSM platform
AWS,1500.00,cloud,2024-03-21,Monthly cloud computing
Okta,1500.00,security,2024-03-22,Identity and access management
Crowdstrike,1200.00,security,2024-03-23,Endpoint protection
AWS,1500.00,cloud,2024-03-24,Monthly cloud computing
Figma,400.00,software,2024-03-25,Design tool
Asana,600.00,software,2024-03-26,Work management
AWS,1500.00,cloud,2024-03-27,Monthly cloud computing
Heroku,700.00,cloud,2024-03-28,PaaS platform
Datadog,1200.00,monitoring,2024-03-29,Monitoring and analytics
AWS,15000.00,cloud,2024-03-30,Unusual spike - large deployment"""
    
    return csv_data
