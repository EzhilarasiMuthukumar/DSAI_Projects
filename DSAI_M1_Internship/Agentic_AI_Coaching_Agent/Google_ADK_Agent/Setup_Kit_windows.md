# Setup Kit — Complete Google Cloud Configuration Guide (Windows)

A step-by-step guide to set up everything needed to run the SPIN Sales Coach agent
locally on Windows and (optionally) deploy to Google Cloud.

> **Cross-reference:** This guide mirrors [Setup_Kit.md](Setup_Kit.md) with Windows-specific
> commands. Sections that are platform-independent link back to the original document.

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
| Windows 10 (1903+) or 11 | `winver` | Version 1903+ or Windows 11 |
| Python 3.10+ | `python --version` | Python 3.10.x or higher |
| Internet access | `Test-NetConnection google.com -Port 443` | TcpTestSucceeded: True |
| Google account | — | Any Gmail or Google Workspace account |

### Install Python (if needed)

```powershell
# Option A: Via winget (built-in package manager on Win 11 / Win 10 updated)
winget install Python.Python.3.12

# Option B: Download installer from https://www.python.org/downloads/
#   IMPORTANT: Check "Add Python to PATH" during installation

# Verify
python --version
pip --version
```

---

## 2. Google Account and Project Setup

This section is platform-independent. Follow the instructions in
[Setup_Kit.md → Section 2](Setup_Kit.md#2-google-account-and-project-setup).

All steps (creating a Google account, accessing Cloud Console, creating a project) are done
in the browser and are identical on Windows.

---

## 3. Gemini API Key (Free Tier — Local Development)

### Getting the Key

The key generation process is done entirely in the browser and is identical across platforms.
Follow the detailed walkthrough in [Setup_Kit.md → Section 3](Setup_Kit.md#3-gemini-api-key-free-tier--local-development)
for Options A, B, and C including key management best practices and free tier limits.

### 3.1 Set the Environment Variable (Windows-specific)

**PowerShell (current session):**
```powershell
$env:GOOGLE_API_KEY = "AIza.........................your-key-here"
```

**Persist permanently (User level):**
```powershell
[System.Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", "AIza.........................your-key-here", "User")
```

**Via System Properties UI:**
1. Press `Win + R` → type `sysdm.cpl` → Enter
2. **Advanced** tab → **Environment Variables**
3. Under "User variables" → **New**
4. Name: `GOOGLE_API_KEY` | Value: your key
5. OK → OK → OK
6. **Restart your terminal** for changes to take effect

**Verify:**
```powershell
echo $env:GOOGLE_API_KEY
```

### 3.2 Test the Key

```powershell
# PowerShell
Invoke-RestMethod "https://generativelanguage.googleapis.com/v1beta/models?key=$env:GOOGLE_API_KEY" | ConvertTo-Json | Select-Object -First 20
```

**Or using curl (available on Win 10+):**
```powershell
curl "https://generativelanguage.googleapis.com/v1beta/models?key=$env:GOOGLE_API_KEY"
```

Expected: JSON response listing available models.

### 3.3 Free Tier Limits

Same as macOS — see [Setup_Kit.md → Section 3.4](Setup_Kit.md#34-free-tier-limits).

---

## 4. Google Cloud SDK Installation

### 4.1 Install

**Option A: Via winget (recommended):**
```powershell
winget install Google.CloudSDK
```

**Option B: Interactive installer:**
1. Download from https://cloud.google.com/sdk/docs/install#windows
2. Run `GoogleCloudSDKInstaller.exe`
3. Follow the wizard (keep all defaults)
4. At the end, check "Run gcloud init"

**Option C: PowerShell one-liner:**
```powershell
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:TEMP\GoogleCloudSDKInstaller.exe")
& "$env:TEMP\GoogleCloudSDKInstaller.exe"
```

### 4.2 Verify Installation

```powershell
gcloud --version
```

### 4.3 Authenticate

```powershell
# Browser-based login
gcloud auth login

# Application Default Credentials
gcloud auth application-default login
```

### 4.4 Set Default Project

```powershell
gcloud config set project spin-coach-agent
```

### 4.5 Set Default Region

```powershell
gcloud config set compute/region us-central1
```

### 4.6 Verify Configuration

```powershell
gcloud config list
```

Expected output is the same as in [Setup_Kit.md → Section 4.6](Setup_Kit.md#46-verify-configuration).

---

## 5. Google Cloud Project Configuration

### 5.1 Link a Billing Account

Same browser-based steps as in [Setup_Kit.md → Section 5](Setup_Kit.md#5-google-cloud-project-configuration).

**CLI commands work identically:**
```powershell
gcloud billing accounts list
gcloud billing projects link spin-coach-agent --billing-account=BILLING_ACCOUNT_ID
```

---

## 6. IAM and Service Accounts

All `gcloud` IAM commands work identically on Windows. Follow
[Setup_Kit.md → Section 6](Setup_Kit.md#6-iam-and-service-accounts).

**Windows-specific note for credentials file:**
```powershell
# Download key file
gcloud iam service-accounts keys create .\credentials.json `
    --iam-account=spin-coach-sa@spin-coach-agent.iam.gserviceaccount.com

# Set environment variable
$env:GOOGLE_APPLICATION_CREDENTIALS = "$PWD\credentials.json"

# Persist
[System.Environment]::SetEnvironmentVariable("GOOGLE_APPLICATION_CREDENTIALS", "$PWD\credentials.json", "User")
```

> **Security Warning:** Never commit `credentials.json` to Git. Add it to `.gitignore`.

---

## 7. Enable Required APIs

Commands are identical across platforms. Follow
[Setup_Kit.md → Section 7](Setup_Kit.md#7-enable-required-apis).

```powershell
gcloud services enable aiplatform.googleapis.com
gcloud services enable generativelanguage.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Verify
gcloud services list --enabled
```

---

## 8. Vertex AI Setup (Optional — Managed Deployment)

### 8.1 Set Environment Variables for Vertex AI

```powershell
$env:GOOGLE_CLOUD_PROJECT = "spin-coach-agent"
$env:GOOGLE_CLOUD_LOCATION = "us-central1"

# Persist
[System.Environment]::SetEnvironmentVariable("GOOGLE_CLOUD_PROJECT", "spin-coach-agent", "User")
[System.Environment]::SetEnvironmentVariable("GOOGLE_CLOUD_LOCATION", "us-central1", "User")
```

### 8.2 Deploy to Vertex AI Agent Engine

The Python deployment script and testing steps are identical to
[Setup_Kit.md → Section 8](Setup_Kit.md#8-vertex-ai-setup-optional--managed-deployment).

```powershell
python deploy_vertex.py
```

---

## 9. Cloud Run Setup (Optional — Remote Access)

### 9.1 Install Docker Desktop (Required for local testing)

1. Download from https://www.docker.com/products/docker-desktop/
2. Install and enable WSL 2 backend when prompted
3. Restart your machine
4. Verify: `docker --version`

### 9.2 Create Dockerfile and .dockerignore

The Dockerfile and .dockerignore content is identical to
[Setup_Kit.md → Section 9.1 and 9.2](Setup_Kit.md#91-create-dockerfile).

### 9.3 Deploy to Cloud Run

```powershell
gcloud run deploy spin-coach `
    --source . `
    --region us-central1 `
    --allow-unauthenticated `
    --set-env-vars "GOOGLE_API_KEY=$env:GOOGLE_API_KEY" `
    --memory 512Mi `
    --cpu 1 `
    --min-instances 0 `
    --max-instances 3 `
    --timeout 300
```

> **Note:** PowerShell uses backtick (`` ` ``) for line continuation, not backslash (`\`).

### 9.4 Access and Restrict Access

Same as [Setup_Kit.md → Sections 9.4 and 9.5](Setup_Kit.md#94-access-the-deployed-agent).

---

## 10. Secret Manager (Production Credentials)

### 10.1 Store the Gemini API Key

```powershell
# Create secret (pipe the key value)
echo $env:GOOGLE_API_KEY | gcloud secrets create gemini-api-key --data-file=-

# Verify
gcloud secrets versions access latest --secret=gemini-api-key
```

### 10.2 Use in Cloud Run and Python

Same as [Setup_Kit.md → Sections 10.2 and 10.3](Setup_Kit.md#102-use-secret-in-cloud-run).

---

## 11. Billing and Budget Alerts

This section is entirely platform-independent (browser-based + gcloud commands).
Follow [Setup_Kit.md → Section 11](Setup_Kit.md#11-billing-and-budget-alerts).

---

## 12. Verification Checklist

### Local Development (Required)
- [ ] `python --version` → 3.10+
- [ ] `echo $env:GOOGLE_API_KEY` → shows your key
- [ ] API test curl returns JSON model list
- [ ] `pip install google-adk` → installs without error
- [ ] `adk --help` → shows ADK commands
- [ ] `python scripts\prepare_data.py` → "DATA PREPARATION COMPLETE"
- [ ] `cd agent; adk web` → launches at localhost:8000
- [ ] Sending a message in the UI → agent responds

### Google Cloud (Optional)
Same checks as [Setup_Kit.md → Section 12](Setup_Kit.md#12-verification-checklist) — all
`gcloud` commands work identically on Windows.

---

## 13. Troubleshooting

### `'gcloud' is not recognized as an internal or external command`

The Google Cloud SDK is not on your PATH.
```powershell
# Add to PATH for current session
$env:Path += ";$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin"

# Or reinstall and ensure "Add to PATH" is checked in the installer
```

### `'python' is not recognized`

```powershell
# Check if Python is installed somewhere
where.exe python

# If installed via Microsoft Store, try:
python3 --version

# Otherwise, reinstall from python.org with "Add to PATH" checked
```

### Execution Policy blocks `.ps1` scripts

```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### `pip install` fails with SSL errors

```powershell
# Corporate proxy or antivirus may intercept. Try:
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### "Permission denied" when enabling APIs

Same resolution as [Setup_Kit.md → Section 13](Setup_Kit.md#13-troubleshooting).

### "Billing account not found"

Same resolution as [Setup_Kit.md → Section 13](Setup_Kit.md#13-troubleshooting).

### "Application Default Credentials not found"

```powershell
# Re-authenticate
gcloud auth application-default login

# Check credentials file exists
Test-Path "$env:APPDATA\gcloud\application_default_credentials.json"

# Set explicitly if needed
$env:GOOGLE_APPLICATION_CREDENTIALS = "$env:APPDATA\gcloud\application_default_credentials.json"
```

### Long file path issues

Windows has a 260-character path limit by default. Enable long paths:
```powershell
# Run as Administrator
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
    -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

---

## Quick Reference — All Environment Variables

```powershell
# Required (local development)
$env:GOOGLE_API_KEY = "AIza..."

# Optional (Google Cloud deployment)
$env:GOOGLE_CLOUD_PROJECT = "spin-coach-agent"
$env:GOOGLE_CLOUD_LOCATION = "us-central1"
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\credentials.json"
```

**Persist all permanently:**
```powershell
[System.Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", "your-key-here", "User")
[System.Environment]::SetEnvironmentVariable("GOOGLE_CLOUD_PROJECT", "spin-coach-agent", "User")
[System.Environment]::SetEnvironmentVariable("GOOGLE_CLOUD_LOCATION", "us-central1", "User")
```

---

## What's Next

Same as [Setup_Kit.md → What's Next](Setup_Kit.md#whats-next). After setup, run:

```powershell
cd agent
adk web
```

Then open http://localhost:8000 and start practicing SPIN conversations.
