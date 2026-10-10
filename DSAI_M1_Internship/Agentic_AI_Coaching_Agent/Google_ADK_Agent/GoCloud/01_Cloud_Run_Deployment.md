# Deploy SPIN Sales Coach to Cloud Run

## Overview

Cloud Run hosts your ADK agent as a serverless container. It scales to zero when
idle (no cost) and auto-scales when traffic arrives. This is the recommended path
for custom deployments with full control.

```
User → Cloud Run URL → ADK Web UI → Gemini API → Response
```

---

## Step 1: Enable Required APIs

```bash
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com
```

Verify:
```bash
gcloud services list --enabled | grep -E "run|build|artifact|secret|aiplatform"
```

---

## Step 2: Store API Key in Secret Manager

Never put secrets in plain text. Use Secret Manager:

```bash
# Create the secret (paste your Gemini API key when prompted)
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-

# Verify
gcloud secrets versions access latest --secret=gemini-api-key
```

Grant Cloud Run access to the secret:
```bash
# Get the Cloud Run service account
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")

gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

---

## Step 3: Create Dockerfile

Create `GoogleADKAgent/Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Prepare training data (build-time)
RUN python scripts/prepare_data.py

# Set working directory to agent folder (ADK expects this)
WORKDIR /app/agent

# Cloud Run sets PORT env var
ENV PORT=8080

# Run ADK web server
CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8080"]
```

---

## Step 4: Create .dockerignore

Create `GoogleADKAgent/.dockerignore`:

```
.git
.venv
__pycache__
*.pyc
.env
.DS_Store
GoCloud/
prerequisites/
comparative_study/
```

---

## Step 5: Deploy to Cloud Run

### Option A: Source Deploy (simplest — Cloud Build handles everything)

```bash
cd GoogleADKAgent

gcloud run deploy spin-coach \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --set-secrets "GOOGLE_API_KEY=gemini-api-key:latest" \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 3 \
    --timeout 300
```

This will:
1. Build a Docker image using Cloud Build
2. Push to Artifact Registry
3. Deploy to Cloud Run
4. Print a public HTTPS URL

### Option B: Build locally, push, deploy

```bash
# Build
docker build -t gcr.io/YOUR_PROJECT_ID/spin-coach .
docker push gcr.io/YOUR_PROJECT_ID/spin-coach

# Deploy
gcloud run deploy spin-coach \
    --image gcr.io/YOUR_PROJECT_ID/spin-coach \
    --region us-central1 \
    --allow-unauthenticated \
    --set-secrets "GOOGLE_API_KEY=gemini-api-key:latest" \
    --memory 512Mi --cpu 1
```

---

## Step 6: Verify Deployment

```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe spin-coach --region us-central1 --format="value(status.url)")
echo "Your agent is live at: $SERVICE_URL"

# Test health
curl -s $SERVICE_URL | head -5
```

Open the URL in a browser — you should see the ADK Web UI.
Select `spin_coach` from the agent dropdown and start chatting.

---

## Step 7: Monitor & Logs

```bash
# View real-time logs
gcloud run services logs tail spin-coach --region us-central1

# View in Cloud Console
# https://console.cloud.google.com/run → select spin-coach → Logs
```

---

## Step 8: Restrict Access (Optional — Production)

Remove public access and require authentication:

```bash
gcloud run services update spin-coach \
    --region us-central1 \
    --no-allow-unauthenticated
```

Then only authenticated users/services can access it.
To grant access to specific users:

```bash
gcloud run services add-iam-policy-binding spin-coach \
    --region us-central1 \
    --member="user:someone@gmail.com" \
    --role="roles/run.invoker"
```

---

## Step 9: Custom Domain (Optional)

```bash
gcloud run domain-mappings create \
    --service spin-coach \
    --domain coach.yourdomain.com \
    --region us-central1
```

Follow the DNS instructions printed by the command.

---

## Cost Estimate

| Resource | Free Tier | Beyond Free |
|----------|-----------|-------------|
| Cloud Run | 2M requests/month | $0.40/million requests |
| Cloud Build | 120 min/day | $0.003/min |
| Secret Manager | 6 active versions | $0.06/10K access |
| Gemini API | 15 RPM free | Pay-per-token |

For a low-traffic coaching agent: **$0/month** within free tier.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check `requirements.txt` — ensure `google-adk>=0.3.0` |
| Container crashes | Check logs: `gcloud run services logs read spin-coach` |
| "GOOGLE_API_KEY not set" | Verify secret binding: `gcloud secrets list` |
| Timeout errors | Increase `--timeout 600` |
| High latency on first request | Cold start — set `--min-instances 1` (costs money) |

---

## Cleanup (Delete Everything)

```bash
gcloud run services delete spin-coach --region us-central1
gcloud secrets delete gemini-api-key
```
