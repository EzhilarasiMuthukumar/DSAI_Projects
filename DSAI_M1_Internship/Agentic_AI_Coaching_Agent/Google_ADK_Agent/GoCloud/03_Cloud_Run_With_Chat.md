# Deploy SPIN Sales Coach to Cloud Run + Google Chat

## Overview

This guide deploys the agent on Cloud Run with a **Google Chat integration**,
allowing sales reps to interact with the coach directly from Google Workspace.

```
Sales Rep → Google Chat → Webhook → Cloud Run (FastAPI) → ADK Runner → Gemini → Reply
```

This is the production-grade architecture described in the project summary.

---

## Architecture

```
┌─────────────────────────────────┐
│       Google Chat (Workspace)    │
│   User types message to bot      │
└──────────────┬──────────────────┘
               │ Webhook POST
               ▼
┌─────────────────────────────────┐
│        Cloud Run (FastAPI)       │
│  1. Receive event                │
│  2. Acknowledge immediately      │
│  3. Run ADK agent                │
│  4. Send reply via Chat API      │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│         Gemini API               │
│   (via google-adk)               │
└─────────────────────────────────┘
```

---

## Step 1: Prerequisites

Complete Steps 1-2 from [01_Cloud_Run_Deployment.md](01_Cloud_Run_Deployment.md):
- APIs enabled
- API key stored in Secret Manager

Additional API:
```bash
gcloud services enable chat.googleapis.com
```

---

## Step 2: Update requirements.txt

Add FastAPI dependencies:

```
google-adk>=0.3.0
fastapi>=0.100.0
uvicorn>=0.20.0
httpx>=0.24.0
google-auth>=2.0.0
```

---

## Step 3: Create FastAPI Webhook Server

Create `GoogleADKAgent/main.py`:

```python
"""FastAPI webhook server for Google Chat + ADK Agent."""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agent"))
from spin_coach import root_agent

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.session_service = InMemorySessionService()
    app.state.runner = Runner(
        agent=root_agent,
        app_name="spin_coach",
        session_service=app.state.session_service,
    )
    logger.info("Agent runner initialized")
    yield

app = FastAPI(title="SPIN Sales Coach", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "agent": "spin_coach"}


@app.post("/webhook")
async def google_chat_webhook(request: Request):
    """Handle Google Chat webhook events."""
    event = await request.json()
    event_type = event.get("type", "")

    if event_type == "ADDED_TO_SPACE":
        return {"text": "👋 Hi! I'm your SPIN Sales Coach. Ask me about SPIN selling, or say 'role-play' to practice!"}

    if event_type == "MESSAGE":
        user_message = event.get("message", {}).get("text", "")
        user_name = event.get("user", {}).get("name", "anonymous")

        try:
            # Get or create session for this user
            sessions = app.state.session_service.list_sessions(
                app_name="spin_coach", user_id=user_name
            )
            if sessions:
                session = sessions[0]
            else:
                session = app.state.session_service.create_session(
                    app_name="spin_coach", user_id=user_name
                )

            # Run agent
            response = await app.state.runner.run_async(
                user_id=user_name,
                session_id=session.id,
                new_message=user_message,
            )

            return {"text": response.text}
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {"text": "⚠️ Sorry, I encountered an error. Please try again."}

    return {}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

---

## Step 4: Update Dockerfile

Replace the CMD to run FastAPI instead of `adk web`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python scripts/prepare_data.py

ENV PORT=8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## Step 5: Deploy to Cloud Run

```bash
cd GoogleADKAgent

gcloud run deploy spin-coach-chat \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --set-secrets "GOOGLE_API_KEY=gemini-api-key:latest" \
    --memory 512Mi --cpu 1 \
    --min-instances 0 --max-instances 5 \
    --timeout 300
```

Note the service URL printed (e.g., `https://spin-coach-chat-xxxxx.run.app`).

---

## Step 6: Configure Google Chat App

1. Go to: https://console.cloud.google.com/apis/api/chat.googleapis.com/hangouts-chat
2. Click **"Configuration"**
3. Fill in:
   - **App name:** SPIN Sales Coach
   - **Avatar URL:** (optional)
   - **Description:** Sales training coach using SPIN methodology
   - **Functionality:** ✅ Receive 1:1 messages, ✅ Join spaces
   - **Connection settings:** HTTP endpoint URL
   - **HTTP endpoint URL:** `https://spin-coach-chat-xxxxx.run.app/webhook`
   - **Visibility:** Specific people in your domain (or make available to everyone)

4. Click **Save**

---

## Step 7: Test in Google Chat

1. Open Google Chat (chat.google.com or in Gmail sidebar)
2. Click "+" → "Find apps"
3. Search for "SPIN Sales Coach"
4. Start a conversation:
   - "What is SPIN selling?"
   - "Evaluate: 'How many patients do you see per month?'"
   - "Let's role-play — you be a vet and I'll practice"

---

## Step 8: Production Hardening

### Add authentication verification

The webhook should verify requests come from Google:

```python
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

def verify_google_chat_request(request):
    """Verify the request comes from Google Chat."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    token = auth_header.split(" ")[1]
    try:
        claims = id_token.verify_token(token, google_requests.Request())
        return claims.get("iss") == "chat@system.gserviceaccount.com"
    except Exception:
        return False
```

### Add Firestore for persistent sessions

Replace `InMemorySessionService` with Firestore for sessions that survive restarts:

```python
from google.adk.sessions import FirestoreSessionService

session_service = FirestoreSessionService(
    project_id="YOUR_PROJECT_ID",
    collection="spin_coach_sessions",
)
```

Enable Firestore API:
```bash
gcloud services enable firestore.googleapis.com
```

---

## Cost Estimate

Same as Cloud Run deployment in [01_Cloud_Run_Deployment.md](01_Cloud_Run_Deployment.md).
Google Chat API has no additional cost for Workspace users.

---

## Cleanup

```bash
gcloud run services delete spin-coach-chat --region us-central1
```

Remove the Chat app from the API console.
