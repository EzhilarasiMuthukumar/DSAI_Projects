# Deploy SPIN Sales Coach to Vertex AI Agent Engine

## Overview

Vertex AI Agent Engine is Google's **managed hosting** for ADK agents. You deploy
the agent code, and Google handles scaling, session management, conversation history,
and monitoring. This is the simplest deployment path but offers less customization.

```
User → Vertex AI Agent Engine API → ADK Agent → Gemini API → Response
```

**Key benefits:**
- Zero infrastructure management
- Built-in session/conversation persistence
- Automatic scaling
- Integrated monitoring via Cloud Console

---

## Step 1: Enable APIs

```bash
gcloud services enable \
    aiplatform.googleapis.com \
    generativelanguage.googleapis.com
```

---

## Step 2: Set Environment Variables

```bash
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="us-central1"

# Verify
echo "Project: $GOOGLE_CLOUD_PROJECT"
echo "Location: $GOOGLE_CLOUD_LOCATION"
```

---

## Step 3: Authenticate

```bash
# Application Default Credentials (required for SDK)
gcloud auth application-default login

# Set quota project
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
```

---

## Step 4: Prepare Data Locally

The knowledge base must exist before deployment:

```bash
cd GoogleADKAgent
python scripts/prepare_data.py
```

Verify: `data/training_data/knowledge_base.json` should exist with 54 chunks.

---

## Step 5: Deploy to Agent Engine

Create `GoogleADKAgent/deploy_vertex.py`:

```python
"""Deploy SPIN Sales Coach to Vertex AI Agent Engine."""
import sys
import vertexai
from vertexai import agent_engines

# Add agent to path
sys.path.insert(0, "agent")
from spin_coach import root_agent

# Initialize Vertex AI
vertexai.init(
    project="YOUR_PROJECT_ID",
    location="us-central1",
)

# Deploy
print("Deploying SPIN Sales Coach to Vertex AI Agent Engine...")
engine = agent_engines.create(
    agent=root_agent,
    display_name="SPIN Sales Coach",
    description="SPIN methodology trainer for company sales representatives",
)

print(f"✅ Deployed successfully!")
print(f"Resource name: {engine.resource_name}")
print(f"\nTo interact with the agent:")
print(f"  session = engine.create_session(user_id='test_user')")
print(f"  response = session.send_message('What is SPIN selling?')")
print(f"  print(response.text)")
```

Run the deployment:
```bash
cd GoogleADKAgent
python deploy_vertex.py
```

This takes 2-5 minutes. It uploads your agent code, tools, and knowledge base to
Vertex AI's managed infrastructure.

---

## Step 6: Test the Deployed Agent

Create `GoogleADKAgent/test_vertex.py`:

```python
"""Test the deployed Vertex AI agent."""
import vertexai
from vertexai import agent_engines

vertexai.init(project="YOUR_PROJECT_ID", location="us-central1")

# List deployed agents
agents = agent_engines.list()
for a in agents:
    print(f"  {a.display_name}: {a.resource_name}")

# Get the SPIN Coach
engine = agent_engines.get("RESOURCE_NAME_FROM_DEPLOY")

# Create a session
session = engine.create_session(user_id="test_user_001")

# Send messages
print("\n--- Testing SPIN Coach ---")
response = session.send_message("What is the SPIN methodology?")
print(f"Agent: {response.text[:500]}")

response = session.send_message("Give me an example of a Problem question for a vet clinic")
print(f"\nAgent: {response.text[:500]}")

# Session maintains context
response = session.send_message("Now evaluate: 'What challenges do you face with flea compliance?'")
print(f"\nAgent: {response.text[:500]}")

print("\n✅ Agent is working correctly on Vertex AI!")
```

Run:
```bash
python test_vertex.py
```

---

## Step 7: Monitor in Cloud Console

1. Go to: https://console.cloud.google.com/vertex-ai/agents
2. Find "SPIN Sales Coach"
3. View:
   - Request count and latency
   - Token usage
   - Error rates
   - Session history

---

## Step 8: Integrate with Applications

### Python SDK (backend integration)

```python
import vertexai
from vertexai import agent_engines

vertexai.init(project="YOUR_PROJECT_ID", location="us-central1")
engine = agent_engines.get("RESOURCE_NAME")

# Per-user sessions (persistent)
session = engine.create_session(user_id="rep_alice@example.com")
response = session.send_message("Let's practice SPIN selling")
print(response.text)
```

### REST API (any language)

```bash
curl -X POST \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/us-central1/agents/AGENT_ID/sessions" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user"}'
```

---

## Limitations vs Cloud Run

| Feature | Vertex AI Agent Engine | Cloud Run |
|---------|:---:|:---:|
| Custom UI | ❌ API only | ✅ ADK Web UI |
| Webhook integration | ❌ Need proxy | ✅ Direct |
| Session persistence | ✅ Built-in | ❌ Need Firestore |
| Scaling | ✅ Automatic | ✅ Automatic |
| Monitoring | ✅ Built-in | ✅ Cloud Logging |
| Custom middleware | ❌ | ✅ Full control |
| Cost | Per-request | Per-second |

**Recommendation:** Use Vertex AI Agent Engine for simple API-based deployments.
Use Cloud Run for custom UI, webhook integrations, or Google Chat bots.

---

## Cost Estimate

| Resource | Approximate Cost |
|----------|-----------------|
| Agent Engine hosting | Pay per request (varies) |
| Gemini 2.0 Flash (input) | $0.075 / 1M tokens |
| Gemini 2.0 Flash (output) | $0.30 / 1M tokens |

For ~50 sessions/day with average conversation: **$5–15/month**.

---

## Cleanup

```bash
# Delete the deployed agent
python -c "
import vertexai
from vertexai import agent_engines
vertexai.init(project='YOUR_PROJECT_ID', location='us-central1')
agent_engines.delete('RESOURCE_NAME')
print('Deleted.')
"
```
