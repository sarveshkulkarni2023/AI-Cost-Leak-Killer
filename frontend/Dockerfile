# Frontend Dockerfile - Streamlit app
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ .

# Create streamlit config directory
RUN mkdir -p ~/.streamlit

# Create streamlit configuration
RUN echo "[server]" > ~/.streamlit/config.toml && \
    echo "headless = true" >> ~/.streamlit/config.toml && \
    echo "port = 8501" >> ~/.streamlit/config.toml && \
    echo "address = \"0.0.0.0\"" >> ~/.streamlit/config.toml && \
    echo "logger.level = \"warning\"" >> ~/.streamlit/config.toml && \
    echo "[client]" >> ~/.streamlit/config.toml && \
    echo "showErrorDetails = false" >> ~/.streamlit/config.toml

# Expose port - Railway will override this with PORT environment variable
EXPOSE 8501

# Health check (basic)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8501').status_code == 200" || exit 1

# Run Streamlit app - always listen on 0.0.0.0
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]

