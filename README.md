# AI Cost Leak Killer

A production-ready system that detects enterprise cost leakages, explains root causes, calculates financial impact, and automatically triggers corrective actions.

## Features

### 1. 📊 Data Ingestion
- Upload CSV files containing cost/transaction data
- Automatic schema validation
- Support for multiple currencies
- Bulk import with error handling

### 2. 🤖 Anomaly Detection
- **Duplicate Detection**: Identify exact duplicate transactions
- **Outlier Detection**: Statistical anomalies using Isolation Forest (scikit-learn)
- **Vendor Analysis**: Detect suspicious vendor patterns and pricing inconsistencies
- **Pattern Detection**: Identify spending spikes and unusual trends

### 3. 🔍 Root Cause Analysis
- Rule-based explanations tailored to each anomaly type
- Confidence scoring
- Metadata enrichment for deeper insights
- Optional LLM integration (mock if no API key)

### 4. 💰 Financial Impact Engine
- Calculate total potential savings
- Severity-based impact assessment
- Monthly and yearly projections
- Anomaly type and vendor breakdowns

### 5. ⚡ Decision Engine
- Intelligent action mapping (email, flag, negotiate, cancel)
- Multi-factor priority scoring
- Risk assessment
- Automated decision logic

### 6. 📋 Action Engine
- Generate email templates with corrective language
- Flag transactions for review
- Initiate vendor negotiations
- Service cancellation requests
- Action execution tracking

### 7. 📈 Dashboard & Analytics
- Real-time cost metrics
- Top spending vendors
- Anomaly distribution
- Financial projections
- Action status tracking

### 8. 🔐 Audit Logging
- Complete decision audit trail
- Timestamped events
- User action tracking
- Compliance-ready logs

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **ORM**: SQLAlchemy
- **Database**: SQLite (default) / PostgreSQL (configurable)
- **ML**: Scikit-learn (Isolation Forest)
- **Data**: Pandas, NumPy

### Frontend
- **Framework**: Streamlit (Python)
- **Visualization**: Plotly
- **HTTP Client**: Requests

### DevOps
- **Configuration**: Environment variables (.env)
- **Python**: Virtual environment isolation

## Project Structure

```
ET_GEN/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application
│   │   ├── database.py             # Database configuration
│   │   ├── models.py               # SQLAlchemy models
│   │   ├── schemas.py              # Pydantic schemas
│   │   ├── routes/                 # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── upload.py           # File upload endpoint
│   │   │   ├── anomalies.py        # Anomaly detection endpoints
│   │   │   ├── dashboard.py        # Dashboard/analytics endpoints
│   │   │   ├── actions.py          # Action management endpoints
│   │   │   └── logs.py             # Audit logging endpoints
│   │   ├── services/               # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── anomaly_detector.py # ML anomaly detection
│   │   │   ├── root_cause_analyzer.py # RCA & decision logic
│   │   │   ├── financial_impact.py # Financial calculations
│   │   │   ├── data_validator.py   # Data validation
│   │   │   └── audit_logger.py     # Audit logging
│   │   └── utils/                  # Utilities
│   │       ├── __init__.py
│   │       ├── helpers.py          # Helper functions
│   │       └── config.py           # Configuration
│   ├── requirements.txt
│   └── venv/                       # Python virtual environment
│
├── frontend/
│   ├── src/
│   │   ├── app.py                  # Main Streamlit app
│   │   ├── api/
│   │   │   └── client.py           # Backend API client
│   │   ├── pages/                  # Streamlit pages
│   │   │   ├── __init__.py
│   │   │   ├── dashboard.py        # Dashboard page
│   │   │   ├── upload.py           # Upload page
│   │   │   ├── anomalies.py        # Anomalies page
│   │   │   ├── actions.py          # Actions page
│   │   │   └── logs.py             # Audit logs page
│   │   └── components/             # Reusable components
│   ├── requirements.txt
│   └── venv/                       # Python virtual environment
│
├── .env                            # Environment configuration
├── .env.example                    # Environment template
├── .gitignore
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.11+ installed
- Git

### Setup & Run

**Terminal 1 - Backend:**
```bash
cd /home/shri/ET_GEN/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The backend starts at: **http://localhost:8000**

**Terminal 2 - Frontend (new terminal):**
```bash
cd /home/shri/ET_GEN/frontend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run src/app.py
```

The frontend starts at: **http://localhost:8501**

### Access the Application
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## API Endpoints

### Upload
- `POST /api/upload` - Upload CSV file

### Anomaly Detection
- `POST /api/detect-anomalies` - Run detection on all transactions
- `GET /api/anomalies` - Get detected anomalies
- `GET /api/anomalies/{id}` - Get specific anomaly
- `PATCH /api/anomalies/{id}` - Update anomaly status

### Dashboard & Analytics
- `GET /api/summary` - Dashboard summary
- `GET /api/metrics` - Financial metrics
- `GET /api/top-vendors` - Top spending vendors
- `GET /api/category-breakdown` - Spending by category

### Actions
- `POST /api/generate-actions` - Generate corrective actions
- `GET /api/actions` - Get all actions
- `GET /api/actions/{id}` - Get specific action
- `POST /api/actions/{id}/execute` - Execute action
- `PATCH /api/actions/{id}` - Update action

### Audit Logs
- `GET /api/logs` - Get audit logs
- `GET /api/logs/stats` - Log statistics

## Sample Dataset

The frontend includes a sample dataset loaded with intentional anomalies:

```csv
vendor,amount,category,date,description
AWS,1500.00,cloud,2024-03-01,Monthly cloud computing
AWS,1500.00,cloud,2024-03-01,Monthly cloud computing (DUPLICATE)
Microsoft,2000.00,software,2024-03-02,Office 365 licensing
AWS,15000.00,cloud,2024-03-05,Unusual spike - large deployment
```

**Intentional Anomalies:**
- Duplicate AWS charges
- Spending spike on AWS (outlier)
- Vendor pattern inconsistencies
- Unusual transaction amounts

## Features in Detail

### Anomaly Types

**Duplicate Detection**
- Identifies exact duplicate transactions
- Flags billing system errors
- High priority by default

**Outlier Detection**
- Statistical anomalies (>2σ variation)
- Uses Isolation Forest algorithm
- Detects fraudulent or unusual transactions

**Vendor Anomalies**
- Detects suspicious vendor patterns
- High variance in transaction amounts
- Pricing inconsistencies

**Pattern Anomalies**
- Spending spikes (2x+ rolling average)
- Trend changes
- Subscription increase patterns

### Root Cause Explanations

Each anomaly receives context-specific root cause analysis:
- **Duplicates**: "Automatic duplicate charge - system error in billing processing"
- **Outliers**: "Fraudulent or unauthorized transaction detected"
- **Vendor**: "Vendor using dynamic pricing with high variance in charges"
- **Patterns**: "Sudden usage spike or subscription tier upgrade"

### Corrective Actions

Actions are intelligently mapped to anomalies:
- **Email**: Send vendor notification or correction request
- **Flag**: Mark for manual review and investigation
- **Negotiate**: Initiate pricing or contract renegotiation
- **Cancel**: Request service cancellation

### Financial Impact

Automatically calculates:
- Total potential savings per anomaly
- Aggregated savings across all anomalies
- Monthly and yearly leakage projections
- Impact severity scoring

### Audit Trail

Every decision is logged:
- Detection events with confidence scores
- Root cause analysis results
- Action generation and execution
- User interactions and status updates
- Complete audit compliance trail

## Screenshots (Features Overview)

### Dashboard
- Key metrics display (transactions, anomalies, savings)
- Financial projections (monthly, yearly)
- Top vendors chart
- Anomaly type distribution pie chart

### Upload Page
- CSV file upload interface
- Sample data loader
- Validation error reporting
- Preview functionality

### Anomaly Detection
- One-click detection trigger
- Filter by status and severity
- Detailed anomaly review
- Root cause explanations

### Actions Management
- Automatic action generation
- Action review and approval interface
- Execution triggers
- Email content preview

### Audit Logs
- Complete event history
- Event type filtering
- Entity-based filtering
- Download capability

## Configuration

### Environment Variables

Create `.env` file from `.env.example`:

```env
# Database
DATABASE_URL=sqlite:///./cost_leak_killer.db

# API
API_HOST=0.0.0.0
API_PORT=8000

# ML
ISOLATION_FOREST_CONTAMINATION=0.1
MIN_SAMPLES_FOR_ML=10

# Financial
DEFAULT_CURRENCY=USD
SAVINGS_MULTIPLIER=0.3

# Logging
LOG_LEVEL=INFO
```

### Database

**SQLite (Default)**
```env
DATABASE_URL=sqlite:///./cost_leak_killer.db
```

**PostgreSQL**
```env
DATABASE_URL=postgresql://user:password@localhost/cost_leak_killer
```

## Usage Workflow

1. **Upload Data**
   - Navigate to "📤 Upload Data"
   - Upload CSV or load sample data
   - Verify upload success

2. **Detect Anomalies**
   - Go to "🔍 Detect Anomalies"
   - Click "Run Detection"
   - Review detected anomalies

3. **Analyze Results**
   - View anomaly details and root causes
   - Check severity and confidence scores
   - Assess potential savings

4. **Generate Actions**
   - Navigate to "⚡ Corrective Actions"
   - Click "Generate Actions"
   - Review proposed corrective actions

5. **Execute Actions**
   - Select actions for execution
   - Click "Execute"
   - Monitor execution status

6. **Review Audit Trail**
   - Check "📋 Audit Logs"
   - Verify all decisions are logged
   - Export audit report

## Performance

The system is optimized for:
- **Scalability**: Handles 10,000+ transactions efficiently
- **Speed**: Anomaly detection runs in seconds
- **Accuracy**: Multi-method detection with confidence scoring
- **Reliability**: Comprehensive error handling and logging

### Recommended Specifications
- CPU: 2+ cores
- Memory: 2+ GB
- Storage: 10+ GB (for database and uploads)

## Troubleshooting

### Backend not responding
```bash
# Verify the backend process is running
# Check if port 8000 is in use:
lsof -i :8000

# Kill process on port 8000 if needed:
pkill -f "uvicorn"
```

### Frontend connection errors
```bash
# Ensure backend is running first
curl http://localhost:8000/health

# Verify frontend can reach backend at localhost:8000
# Check frontend logs in the Streamlit terminal
```

### Port conflicts
```bash
# Change ports in the uvicorn command:
python -m uvicorn app.main:app --reload --port 9000

# For Streamlit, change port using CLI flag or config:
streamlit run src/app.py --server.port 9501
```

### Virtual environment issues
```bash
# Deactivate and reactivate venv
deactivate
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Future Enhancements

- [ ] LLM integration for enhanced root cause analysis
- [ ] Machine learning model training and improvement
- [ ] Advanced visualization dashboards
- [ ] Email notification system
- [ ] Webhook integration
- [ ] Custom anomaly rules
- [ ] Multi-tenant support
- [ ] Advanced authentication/authorization

## License

This project is provided as-is for enterprise use.

## Support

For issues and questions:
1. Check existing issues in logs
2. Review API documentation
3. Check audit logs for detailed event information

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Production Ready ✅
