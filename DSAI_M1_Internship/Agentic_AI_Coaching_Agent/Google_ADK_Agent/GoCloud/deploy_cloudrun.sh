#!/bin/bash
# Deploy SPIN Sales Coach to Cloud Run
# Usage: cd GoogleADKAgent && bash GoCloud/deploy_cloudrun.sh

set -e

# Configuration
SERVICE_NAME="spin-coach"
REGION="us-central1"
SECRET_NAME="gemini-api-key"

echo "=== Deploying SPIN Sales Coach to Cloud Run ==="
echo "Service: $SERVICE_NAME"
echo "Region:  $REGION"
echo ""

# Check prerequisites
echo "Checking prerequisites..."
gcloud --version > /dev/null 2>&1 || { echo "ERROR: gcloud not installed"; exit 1; }
echo "✓ gcloud installed"

PROJECT=$(gcloud config get-value project 2>/dev/null)
[ -z "$PROJECT" ] && { echo "ERROR: No project set. Run: gcloud config set project YOUR_PROJECT_ID"; exit 1; }
echo "✓ Project: $PROJECT"

# Check secret exists
gcloud secrets describe $SECRET_NAME > /dev/null 2>&1 || { echo "ERROR: Secret '$SECRET_NAME' not found. Create it first (see 01_Cloud_Run_Deployment.md Step 2)"; exit 1; }
echo "✓ Secret: $SECRET_NAME exists"

# Copy deployment files to project root (if not already there)
if [ ! -f "Dockerfile" ]; then
    echo "Copying Dockerfile from GoCloud/..."
    cp GoCloud/Dockerfile .
    cp GoCloud/.dockerignore .
fi

# Deploy
echo ""
echo "Deploying to Cloud Run (this takes 2-5 minutes)..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
    --allow-unauthenticated \
    --set-secrets "GOOGLE_API_KEY=${SECRET_NAME}:latest" \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 3 \
    --timeout 300

# Get URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")
echo ""
echo "=== Deployment Complete ==="
echo "Your agent is live at: $SERVICE_URL"
echo ""
echo "Open in browser to access the ADK Web UI."
