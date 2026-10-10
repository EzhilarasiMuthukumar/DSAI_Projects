FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Prepare training data (build-time step)
RUN python scripts/prepare_data.py

# Set working directory to agent folder (ADK web expects this)
WORKDIR /app/agent

# Cloud Run sets PORT env var
ENV PORT=8080

# Run ADK web server
CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8080"]
