# GoCloud — Deploy SPIN Sales Coach to Google Cloud

Step-by-step guides to deploy the locally-validated SPIN Sales Coach agent to Google Cloud.

## Deployment Options

| # | Guide | Target | Cost | Complexity |
|---|-------|--------|------|:---:|
| 1 | [01_Cloud_Run_Deployment.md](01_Cloud_Run_Deployment.md) | Cloud Run (serverless containers) | Free tier / Pay-per-use | Medium |
| 2 | [02_Vertex_AI_Agent_Engine.md](02_Vertex_AI_Agent_Engine.md) | Vertex AI Agent Engine (managed) | Pay-per-request | Low |
| 3 | [03_Cloud_Run_With_Chat.md](03_Cloud_Run_With_Chat.md) | Cloud Run + Google Chat integration | Free tier / Pay-per-use | High |

## Prerequisites

Before any deployment, ensure:
- [x] Agent runs locally (`cd agent && adk web` → works at localhost:8000)
- [x] Google Cloud SDK installed (`gcloud --version`)
- [x] Authenticated (`gcloud auth login`)
- [x] Project set (`gcloud config set project YOUR_PROJECT_ID`)
- [x] Billing enabled on the project
- [x] Required APIs enabled (see guides)

## Quick Start (Fastest Path)

If you just want to get the agent running in the cloud quickly:

```bash
# 1. Navigate to the project
cd GoogleADKAgent

# 2. Deploy to Cloud Run (one command)
gcloud run deploy spin-coach \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --set-secrets "GOOGLE_API_KEY=gemini-api-key:latest" \
    --memory 512Mi --cpu 1 \
    --min-instances 0 --max-instances 3

# 3. Access at the URL printed by gcloud
```

For detailed step-by-step instructions, see the individual guides.
