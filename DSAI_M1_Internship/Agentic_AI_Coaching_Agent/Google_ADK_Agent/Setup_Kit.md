# Setup Kit — Complete Google Cloud Configuration Guide

A step-by-step guide to set up everything needed to run the SPIN Sales Coach agent
locally and (optionally) deploy to Google Cloud. Covers both Intel and Apple Silicon Macs.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Google Account and Project Setup](#2-google-account-and-project-setup)
3. [Gemini API Key (Free Tier — Local Development)](#3-gemini-api-key-free-tier--local-development)
4. [Google Cloud SDK Installation](#4-google-cloud-sdk-installation)
5. [Google Cloud Project Configuration](#5-google-cloud-project-configuration)
6. [IAM and Service Accounts](#6-iam-and-service-accounts)
7. [Enable Required APIs](#7-enable-required-apis)
8. [Vertex AI Setup (Optional — Managed Deployment)](#8-vertex-ai-setup-optional--managed-deployment)
9. [Cloud Run Setup (Optional — Remote Access)](#9-cloud-run-setup-optional--remote-access)
10. [Secret Manager (Production Credentials)](#10-secret-manager-production-credentials)
11. [Billing and Budget Alerts](#11-billing-and-budget-alerts)
12. [Verification Checklist](#12-verification-checklist)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Prerequisites

Before starting, ensure you have:

| Requirement | Check Command | Expected |
|-------------|---------------|----------|
| macOS 13+ | `sw_vers` | ProductVersion: 13.x+ |
| Python 3.10+ | `python3 --version` | Python 3.10.x or higher |
| Homebrew | `brew --version` | Homebrew 4.x |
| Internet access | `curl -s https://google.com` | HTML response |
| Google account | — | Any Gmail or Google Workspace account |

### Install Python (if needed)

```bash
# Install via Homebrew (works on both Intel and Apple Silicon)
brew install python@3.12

# Verify
python3 --version
```

### Install Homebrew (if needed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

## 2. Google Account and Project Setup

### 2.1 Create a Google Account (skip if you already have one)

1. Go to https://accounts.google.com/signup
2. Complete the registration
3. Verify your email address

### 2.2 Access Google Cloud Console

1. Go to https://console.cloud.google.com
2. Sign in with your Google account
3. Accept the Terms of Service if prompted
4. You'll land on the Cloud Console dashboard

### 2.3 Create a New Project

**Via Console UI:**
1. Click the project dropdown (top-left, next to "Google Cloud")
2. Click "New Project"
3. Enter:
   - Project name: `spin-coach` (or your preferred name)
   - Organization: Leave as "No organization" for personal accounts
   - Location: Leave default
4. Click "Create"
5. Wait for the notification that the project is ready
6. Select the new project from the dropdown

**Via CLI (after Step 4 below):**
```bash
gcloud projects create spin-coach-agent --name="SPIN Coach Agent"
gcloud config set project spin-coach-agent
```

> **Note:** Project IDs must be globally unique. If `spin-coach-agent` is taken,
> append a random suffix: `spin-coach-agent-42xyz`

---

## 3. Gemini API Key (Free Tier — Local Development)

This is the simplest path — sufficient for local development and learning.
No billing account required for the free tier.

### 3.1 Get Your API Key — Detailed Walkthrough

There are two ways to generate a Gemini API key: **Google AI Studio** (simplest, no billing)
or **Google Cloud Console** (ties to a GCP project). Use AI Studio for learning.

---

#### Option A: Via Google AI Studio (Recommended for Local Development)

**Step 1 — Open AI Studio**

- Navigate to: https://aistudio.google.com
- Sign in with your Google account (any Gmail works)
- If prompted, accept the Terms of Service

**Step 2 — Access the API Keys Page**

- In the left sidebar, click **"Get API Key"**
  (If you don't see the sidebar, click the hamburger menu ☰ at top-left)
- You'll be taken to the API Keys management page

**Step 3 — Create a New Key**

- Click the **"Create API Key"** button
- A dialog appears asking you to select a Google Cloud project:
  - **If you have an existing project**: Select it from the dropdown
  - **If you don't have a project**: Select "Create API key in new project"
    (AI Studio will auto-create a project called "Generative Language Client")
- Click **"Create API Key in existing project"** (or the new project option)

**Step 4 — Copy the Key**

- Your API key appears in a dialog box
- It looks like: `AIzaSyD...............................abc`
- Click the **copy icon** 📋 to copy it to your clipboard
- **IMPORTANT:** Save this somewhere safe immediately. You can view it again later
  from the same page, but it's easier to save it now.

**Step 5 — Verify on the Keys Page**

- After creation, you'll see your key listed in a table with:
  - Key name (auto-generated)
  - Creation date
  - Associated project
  - A "Copy" button and "Delete" button
- You can create multiple keys if needed (e.g., separate keys for dev/test)

---

#### Option B: Via Google Cloud Console (For GCP Project Integration)

Use this method if you want the key tied to a specific GCP project with billing.

**Step 1 — Open the Credentials Page**

- Go to: https://console.cloud.google.com/apis/credentials
- Select your project from the top dropdown

**Step 2 — Enable the Gemini API**

- Go to: https://console.cloud.google.com/apis/library
- Search for "Generative Language API" (or "Gemini API")
- Click on it and click **"Enable"**

**Step 3 — Create API Key**

- Return to: https://console.cloud.google.com/apis/credentials
- Click **"+ CREATE CREDENTIALS"** at the top
- Select **"API key"**
- A new key is generated immediately
- Copy the key from the dialog

**Step 4 — Restrict the Key (Recommended for Security)**

- Click **"Edit API key"** (or click the key name in the list)
- Under "API restrictions":
  - Select "Restrict key"
  - Check only "Generative Language API"
- Under "Application restrictions" (optional):
  - For local dev, leave as "None"
  - For production, restrict by IP address
- Click **"Save"**

---

#### Option C: Via gcloud CLI

```bash
# Ensure the API is enabled
gcloud services enable generativelanguage.googleapis.com

# Create an API key via CLI
gcloud services api-keys create \
    --display-name="SPIN Coach Gemini Key" \
    --api-target=service=generativelanguage.googleapis.com

# The command outputs the key string — copy it
# If it only shows the key ID, retrieve the key string:
gcloud services api-keys get-key-string KEY_ID
```

---

#### Key Management Best Practices

| Practice | Why |
|----------|-----|
| Never commit keys to Git | Use `.gitignore` and env variables |
| Use separate keys for dev/prod | Easier to rotate and audit |
| Restrict keys to specific APIs | Limits damage if key is leaked |
| Rotate keys periodically | Reduce exposure window |
| Monitor usage in Console | Detect unauthorized usage early |

**If your key is compromised:**
1. Go to https://aistudio.google.com → Get API Key
2. Click the trash icon 🗑️ next to the compromised key
3. Create a new key
4. Update your `GOOGLE_API_KEY` environment variable

---

#### What the Key Gives You Access To

| Model | Capability | Free Tier |
|-------|-----------|-----------|
| gemini-2.0-flash | Fast responses, tool calling | ✅ 15 RPM |
| gemini-2.5-pro | Advanced reasoning | ✅ 5 RPM |
| gemini-2.0-flash-lite | Fastest, cheapest | ✅ 30 RPM |
| text-embedding-004 | Text embeddings for RAG | ✅ 1500 RPD |

### 3.2 Set the Environment Variable

```bash
# Set for current terminal session
export GOOGLE_API_KEY="AIza.........................your-key-here"

# Persist across terminal sessions (add to shell profile)
echo 'export GOOGLE_API_KEY="AIza.........................your-key-here"' >> ~/.zshrc

# Reload profile
source ~/.zshrc

# Verify it's set
echo $GOOGLE_API_KEY
```

### 3.3 Test the Key

```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_API_KEY" | python3 -m json.tool | head -20
```

Expected: JSON response listing available models (gemini-2.0-flash, etc.)

### 3.4 Free Tier Limits

| Limit | Value |
|-------|-------|
| Requests per minute (RPM) | 15 |
| Tokens per minute (TPM) | 1,000,000 |
| Requests per day (RPD) | 1,500 |
| Cost | Free |

This is more than enough for learning and development.

---

## 4. Google Cloud SDK Installation

The `gcloud` CLI is needed for cloud deployment features.

### 4.1 Install

```bash
# Via Homebrew (recommended — handles both Intel and Apple Silicon)
brew install google-cloud-sdk
```

**Alternative (manual install):**
```bash
# Download installer
curl https://sdk.cloud.google.com | bash

# Restart shell
exec -l $SHELL

# Initialize
gcloud init
```

### 4.2 Verify Installation

```bash
gcloud --version
```

Expected output:
```
Google Cloud SDK 4xx.0.0
bq 2.x.x
core 2024.xx.xx
gsutil 5.x
```

### 4.3 Authenticate

```bash
# Browser-based login (opens browser for OAuth)
gcloud auth login

# Application Default Credentials (needed for SDK/library access)
gcloud auth application-default login
```

Both commands open a browser window. Sign in and grant permissions.

### 4.4 Set Default Project

```bash
gcloud config set project spin-coach-agent
```

### 4.5 Set Default Region

```bash
gcloud config set compute/region us-central1
```

### 4.6 Verify Configuration

```bash
gcloud config list
```

Expected:
```
[core]
project = spin-coach-agent
account = your-email@gmail.com

[compute]
region = us-central1
```

---

## 5. Google Cloud Project Configuration

### 5.1 Link a Billing Account

Required for any paid services (Cloud Run, Vertex AI). NOT required for Gemini API free tier.

1. Go to https://console.cloud.google.com/billing
2. Click "Link a billing account"
3. If you don't have one, click "Create Account"
4. Enter payment method (credit card required, but free tier won't charge)
5. Link to your project

**Via CLI:**
```bash
# List billing accounts
gcloud billing accounts list

# Link to project
gcloud billing projects link spin-coach-agent --billing-account=BILLING_ACCOUNT_ID
```

### 5.2 Free Tier Overview

Google Cloud offers:
- $300 free credits for new accounts (valid 90 days)
- Always-free tier for many services
- Cloud Run: 2 million requests/month free
- Cloud Build: 120 build-minutes/day free

---

## 6. IAM and Service Accounts

### 6.1 Create a Service Account (for deployments)

```bash
# Create service account
gcloud iam service-accounts create spin-coach-sa \
    --display-name="SPIN Coach Agent Service Account" \
    --description="Service account for the SPIN Coach ADK agent"

# Verify
gcloud iam service-accounts list
```

### 6.2 Grant Roles

```bash
PROJECT_ID="spin-coach-agent"

# Vertex AI access (for model calls and Agent Engine)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:spin-coach-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Cloud Run deployment
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:spin-coach-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# Secret Manager access (for API keys in production)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:spin-coach-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Cloud Storage (for artifacts if needed)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:spin-coach-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"
```

### 6.3 Download Key File (for local testing with service account)

```bash
gcloud iam service-accounts keys create ./credentials.json \
    --iam-account=spin-coach-sa@${PROJECT_ID}.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials.json"
```

> **Security Warning:** Never commit `credentials.json` to Git. Add it to `.gitignore`.

```bash
echo "credentials.json" >> .gitignore
```

---

## 7. Enable Required APIs

```bash
# Core APIs needed
gcloud services enable aiplatform.googleapis.com          # Vertex AI
gcloud services enable generativelanguage.googleapis.com  # Gemini API
gcloud services enable run.googleapis.com                 # Cloud Run
gcloud services enable cloudbuild.googleapis.com          # Cloud Build (for deployments)
gcloud services enable secretmanager.googleapis.com       # Secret Manager
gcloud services enable artifactregistry.googleapis.com    # Container Registry

# Verify enabled APIs
gcloud services list --enabled --filter="config.name:(aiplatform OR run OR cloudbuild OR secretmanager)"
```

**Expected output:**
```
NAME                                 TITLE
aiplatform.googleapis.com            Vertex AI API
run.googleapis.com                   Cloud Run Admin API
cloudbuild.googleapis.com            Cloud Build API
secretmanager.googleapis.com         Secret Manager API
```

---

## 8. Vertex AI Setup (Optional — Managed Deployment)

### 8.1 Verify Vertex AI Access

```bash
# Test that you can list models
gcloud ai models list --region=us-central1 2>&1 | head -5
```

### 8.2 Set Environment Variables for Vertex AI

```bash
export GOOGLE_CLOUD_PROJECT="spin-coach-agent"
export GOOGLE_CLOUD_LOCATION="us-central1"

# Persist
echo 'export GOOGLE_CLOUD_PROJECT="spin-coach-agent"' >> ~/.zshrc
echo 'export GOOGLE_CLOUD_LOCATION="us-central1"' >> ~/.zshrc
source ~/.zshrc
```

### 8.3 Deploy to Vertex AI Agent Engine

```python
# deploy_vertex.py (run from project root)
import vertexai
from vertexai import agent_engines
import sys
sys.path.insert(0, "agent")
from spin_coach import root_agent

vertexai.init(project="spin-coach-agent", location="us-central1")

engine = agent_engines.create(
    agent=root_agent,
    display_name="SPIN Sales Coach",
    description="SPIN methodology trainer for company sales reps",
)

print(f"✅ Deployed: {engine.resource_name}")
print(f"   Use this resource name to interact programmatically.")
```

```bash
python deploy_vertex.py
```

### 8.4 Test Deployed Agent

```python
# Query the deployed agent
session = engine.create_session(user_id="test_user")
response = session.send_message("What is the SPIN methodology?")
print(response.text)
```

---

## 9. Cloud Run Setup (Optional — Remote Access)

Cloud Run gives you a public URL to access the agent from any device.

### 9.1 Create Dockerfile

```bash
cat > Dockerfile << 'EOF'
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Prepare RAG data
RUN python scripts/prepare_data.py

# Set working directory to agent folder
WORKDIR /app/agent

# Expose port and run
EXPOSE 8080
CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8080"]
EOF
```

### 9.2 Create .dockerignore

```bash
cat > .dockerignore << 'EOF'
.venv/
__pycache__/
*.pyc
.git/
credentials.json
.env
EOF
```

### 9.3 Deploy to Cloud Run

```bash
# Deploy (builds container automatically via Cloud Build)
gcloud run deploy spin-coach \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_API_KEY=$GOOGLE_API_KEY" \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 3 \
    --timeout 300
```

### 9.4 Access the Deployed Agent

After deployment completes, you'll see:
```
Service URL: https://spin-coach-xxxxx-uc.a.run.app
```

Open that URL in any browser to access the ADK Web UI remotely.

### 9.5 Restrict Access (Optional)

For team-only access:
```bash
# Remove public access
gcloud run services update spin-coach \
    --region us-central1 \
    --no-allow-unauthenticated

# Grant access to specific users
gcloud run services add-iam-policy-binding spin-coach \
    --region us-central1 \
    --member="user:colleague@company.com" \
    --role="roles/run.invoker"
```

Users access via Identity-Aware Proxy or with a token:
```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
    https://spin-coach-xxxxx-uc.a.run.app
```

---

## 10. Secret Manager (Production Credentials)

Never put API keys in environment variables for production. Use Secret Manager.

### 10.1 Store the Gemini API Key

```bash
# Create secret
echo -n "$GOOGLE_API_KEY" | gcloud secrets create gemini-api-key --data-file=-

# Verify
gcloud secrets versions access latest --secret=gemini-api-key
```

### 10.2 Use Secret in Cloud Run

```bash
# Update Cloud Run to use secret
gcloud run services update spin-coach \
    --region us-central1 \
    --set-secrets "GOOGLE_API_KEY=gemini-api-key:latest"
```

### 10.3 Access Secret from Python (if needed)

```python
from google.cloud import secretmanager

def get_secret(secret_id: str, project_id: str = "spin-coach-agent") -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Usage
api_key = get_secret("gemini-api-key")
```

---

## 11. Billing and Budget Alerts

Protect yourself from unexpected charges.

### 11.1 Set a Budget Alert

1. Go to https://console.cloud.google.com/billing/budgets
2. Click "Create Budget"
3. Select your billing account and project
4. Set budget amount: **$25** (very generous for learning)
5. Set alert thresholds: 50%, 80%, 100%
6. Add email notification
7. Click "Finish"

**Via CLI:**
```bash
# Create budget (simplified)
gcloud billing budgets create \
    --billing-account=BILLING_ACCOUNT_ID \
    --display-name="SPIN Coach Monthly Budget" \
    --budget-amount=25.00USD \
    --threshold-rule=percent=0.5 \
    --threshold-rule=percent=0.8 \
    --threshold-rule=percent=1.0
```

### 11.2 Monitor Costs

```bash
# Check current month's cost estimate
gcloud billing projects describe spin-coach-agent
```

Or visit: https://console.cloud.google.com/billing/reports

### 11.3 Expected Costs for This Project

| Activity | Estimated Monthly Cost |
|----------|----------------------|
| Local development only (Gemini free tier) | $0 |
| Cloud Run (low traffic, scale-to-zero) | $0-5 |
| Vertex AI Agent Engine (light usage) | $5-15 |
| Secret Manager (1 secret) | $0.06 |
| Cloud Build (deploys) | $0 (free tier) |
| **Total for learning** | **$0-20** |

---

## 12. Verification Checklist

Run through this after completing setup:

### Local Development (Required)
- [ ] `python3 --version` → 3.10+
- [ ] `echo $GOOGLE_API_KEY` → shows your key
- [ ] `curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_API_KEY"` → JSON response
- [ ] `pip install google-adk` → installs without error
- [ ] `adk --help` → shows ADK commands
- [ ] `python scripts/prepare_data.py` → "DATA PREPARATION COMPLETE"
- [ ] `cd agent && adk web` → launches at localhost:8000
- [ ] Sending a message in the UI → agent responds

### Google Cloud (Optional)
- [ ] `gcloud --version` → SDK version shown
- [ ] `gcloud auth list` → your account listed as ACTIVE
- [ ] `gcloud config get project` → your project ID
- [ ] `gcloud services list --enabled` → shows required APIs
- [ ] `gcloud iam service-accounts list` → shows spin-coach-sa
- [ ] Cloud Run deployment URL accessible (if deployed)
- [ ] Budget alert configured (if billing enabled)

---

## 13. Troubleshooting

### "gcloud: command not found"

```bash
# If installed via Homebrew
source "$(brew --prefix)/share/google-cloud-sdk/path.zsh.inc"

# Add to profile permanently
echo 'source "$(brew --prefix)/share/google-cloud-sdk/path.zsh.inc"' >> ~/.zshrc
source ~/.zshrc
```

### "Permission denied" when enabling APIs

```bash
# You need Owner or Editor role on the project
gcloud projects get-iam-policy spin-coach-agent \
    --flatten="bindings[].members" \
    --filter="bindings.members:$(gcloud config get account)"

# If missing, ask project owner to grant:
gcloud projects add-iam-policy-binding spin-coach-agent \
    --member="user:your-email@gmail.com" \
    --role="roles/editor"
```

### "Billing account not found" or "Billing must be enabled"

1. Go to https://console.cloud.google.com/billing
2. Create a billing account if you don't have one
3. Link it to your project:
```bash
gcloud billing projects link spin-coach-agent \
    --billing-account=$(gcloud billing accounts list --format="value(name)" | head -1)
```

### "Cloud Run deployment fails with build error"

```bash
# Check build logs
gcloud builds list --limit=3
gcloud builds log BUILD_ID  # Replace with actual ID

# Common fix: ensure Dockerfile and requirements.txt are correct
# Test locally first:
docker build -t spin-coach .
docker run -p 8080:8080 -e GOOGLE_API_KEY=$GOOGLE_API_KEY spin-coach
```

### "Quota exceeded" for Gemini API

```bash
# Check your current quotas
# Visit: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas

# If hitting free tier limits (15 RPM), either:
# 1. Wait and retry
# 2. Upgrade to paid tier (minimal cost)
# 3. Add a sleep/backoff in your code
```

### "Application Default Credentials not found"

```bash
# Re-authenticate
gcloud auth application-default login

# Verify credentials file exists
ls ~/.config/gcloud/application_default_credentials.json

# Set explicitly if needed
export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcloud/application_default_credentials.json
```

### "Region not available for Vertex AI"

```bash
# Not all regions support all Vertex AI features
# Use us-central1 (most complete)
gcloud config set compute/region us-central1
export GOOGLE_CLOUD_LOCATION="us-central1"
```

---

## Quick Reference — All Environment Variables

```bash
# Required (local development)
export GOOGLE_API_KEY="AIza..."

# Optional (Google Cloud deployment)
export GOOGLE_CLOUD_PROJECT="spin-coach-agent"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

Add all to your `~/.zshrc` for persistence:
```bash
cat >> ~/.zshrc << 'EOF'

# Google ADK / SPIN Coach Agent
export GOOGLE_API_KEY="your-key-here"
export GOOGLE_CLOUD_PROJECT="spin-coach-agent"
export GOOGLE_CLOUD_LOCATION="us-central1"
EOF

source ~/.zshrc
```

---

## What's Next

After completing this setup:

1. **Run locally** → `cd agent && adk web` (start here!)
2. **Explore the agent** → Practice SPIN conversations, try role-play
3. **Deploy to Cloud Run** → Share with team members
4. **Iterate** → Add more training data, improve tools, refine agent instructions
