# Google Cloud Setup (Optional)

Only needed if you want to:
- Deploy the agent to Vertex AI Agent Engine
- Use Vertex AI session management
- Deploy via Cloud Run for team access

---

## Step 1: Install Google Cloud CLI

```bash
brew install google-cloud-sdk
```

---

## Step 2: Authenticate

```bash
gcloud auth login
gcloud auth application-default login
```

---

## Step 3: Create/Select Project

```bash
# Create new project (or use existing)
gcloud projects create spin-coach-project --name="SPIN Coach"

# Set as active project
gcloud config set project spin-coach-project

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable run.googleapis.com
```

---

## Step 4: Set Environment Variables

```bash
export GOOGLE_CLOUD_PROJECT="spin-coach-project"
export GOOGLE_CLOUD_LOCATION="us-central1"
```

---

## Deploy to Cloud Run (Simple Remote Access)

If you want the agent accessible from any device:

### Create Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python scripts/prepare_data.py
WORKDIR /app/agent
EXPOSE 8000
CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8000"]
```

### Deploy

```bash
gcloud run deploy spin-coach \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_API_KEY=$GOOGLE_API_KEY" \
    --memory 1Gi \
    --cpu 1
```

### Access

After deployment, Cloud Run provides a URL like:
`https://spin-coach-xxxxx.run.app`

Open it in any browser to use the SPIN Coach.

---

## Deploy to Vertex AI Agent Engine (Managed)

```python
# deploy_vertex.py
import vertexai
from vertexai import agent_engines
from spin_coach import root_agent

vertexai.init(project="spin-coach-project", location="us-central1")

engine = agent_engines.create(
    agent=root_agent,
    display_name="SPIN Sales Coach",
    description="SPIN methodology trainer for company sales reps",
)

print(f"Deployed: {engine.resource_name}")
```

---

## Cost Estimate

| Component | Cost | Notes |
|-----------|------|-------|
| Gemini API (local dev) | Free tier: 15 RPM | Sufficient for learning |
| Cloud Run (optional) | ~$5-10/month | Only when deployed |
| Vertex AI Agent Engine | Pay per request | Only when deployed |

For learning purposes, local development with the free Gemini API tier is sufficient.
