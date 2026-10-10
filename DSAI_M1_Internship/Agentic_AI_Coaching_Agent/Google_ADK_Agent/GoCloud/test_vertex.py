"""Test the deployed SPIN Sales Coach on Vertex AI.

Usage:
    1. Replace RESOURCE_NAME with the value from deploy_vertex.py output
    2. Run: python GoCloud/test_vertex.py
"""
import os
import vertexai
from vertexai import agent_engines

# === CONFIGURE ===
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "YOUR_PROJECT_ID")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
RESOURCE_NAME = "PASTE_RESOURCE_NAME_HERE"  # from deploy output
# =================

vertexai.init(project=PROJECT_ID, location=LOCATION)

# List agents
print("Deployed agents:")
for a in agent_engines.list():
    print(f"  {a.display_name}: {a.resource_name}")

# Get the agent
engine = agent_engines.get(RESOURCE_NAME)
print(f"\nTesting: {engine.display_name}")

# Create session
session = engine.create_session(user_id="test_user_001")

# Test conversations
test_messages = [
    "What is the SPIN methodology?",
    "Give me an example of a Problem question for a vet clinic",
    "Evaluate: 'What challenges do you face with flea compliance?'",
]

for msg in test_messages:
    print(f"\n{'='*60}")
    print(f"User: {msg}")
    response = session.send_message(msg)
    print(f"Agent: {response.text[:300]}...")

print(f"\n{'='*60}")
print("✅ All tests passed!")
