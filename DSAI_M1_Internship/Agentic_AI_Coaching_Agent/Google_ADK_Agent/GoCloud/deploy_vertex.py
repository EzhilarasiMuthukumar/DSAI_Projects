"""Deploy SPIN Sales Coach to Vertex AI Agent Engine.

Usage:
    1. Set your project ID below
    2. Ensure you have run: gcloud auth application-default login
    3. Ensure data is prepared: python scripts/prepare_data.py
    4. Run: python GoCloud/deploy_vertex.py
"""
import sys
import os

# Add agent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agent'))

import vertexai
from vertexai import agent_engines
from spin_coach import root_agent

# === CONFIGURE THESE ===
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "YOUR_PROJECT_ID")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
# =======================

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

print(f"Deploying SPIN Sales Coach to Vertex AI Agent Engine...")
print(f"  Project:  {PROJECT_ID}")
print(f"  Location: {LOCATION}")
print()

# Deploy
engine = agent_engines.create(
    agent=root_agent,
    display_name="SPIN Sales Coach",
    description="SPIN methodology trainer for company sales representatives",
)

print(f"\n✅ Deployed successfully!")
print(f"Resource name: {engine.resource_name}")
print(f"\nTo test:")
print(f"  python GoCloud/test_vertex.py")
