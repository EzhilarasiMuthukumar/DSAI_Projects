# Local Setup — Windows 10/11

## Prerequisites

- Windows 10 (1903+) or Windows 11
- Python 3.10+ (from python.org or Microsoft Store)
- A Gemini API key (free from aistudio.google.com)

> **Note:** For Gemini API key generation and Google Account setup, refer to
> [Setup_Kit_windows.md](../Setup_Kit_windows.md#3-gemini-api-key-free-tier--local-development)
> — the steps are identical across platforms.

---

## Step 1: Install Python (if needed)

```powershell
# Check current version
python --version

# If not installed or below 3.10:
# Option A: Download from https://www.python.org/downloads/
#   - IMPORTANT: Check "Add Python to PATH" during installation

# Option B: Install via winget
winget install Python.Python.3.12

# Option C: Install from Microsoft Store
# Search "Python 3.12" in Microsoft Store
```

**Verify pip:**
```powershell
pip --version
```

---

## Step 2: Clone and Setup

```powershell
cd C:\path\to\LearnGoogleADK\GoogleADKAgent

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify ADK is installed
adk --help
```

> **Note:** On Windows, use `.venv\Scripts\activate` (not `source .venv/bin/activate`).

---

## Step 3: Configure API Key

```powershell
# Set for current terminal session
$env:GOOGLE_API_KEY = "your-api-key-here"

# Persist permanently (User level)
[System.Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", "your-api-key-here", "User")

# Verify
echo $env:GOOGLE_API_KEY
```

**Alternative — using System Properties UI:**
1. Press `Win + R` → type `sysdm.cpl` → Enter
2. Go to **Advanced** tab → **Environment Variables**
3. Under "User variables", click **New**
4. Variable name: `GOOGLE_API_KEY`
5. Variable value: your key
6. Click OK → OK → OK
7. Restart your terminal

---

## Step 4: Prepare Data

```powershell
python scripts\prepare_data.py
```

Expected output is the same as described in [setup_mac.md](setup_mac.md#step-4-prepare-data).

---

## Step 5: Run the Agent

```powershell
cd agent
adk web
```

Open **http://localhost:8000** in your browser. Select `spin_coach` from the dropdown.

---

## Step 6: Test Conversations

Same test prompts apply — see [setup_mac.md → Step 6](setup_mac.md#step-6-test-conversations).

---

## Troubleshooting

### `'python' is not recognized as an internal or external command`

Python is not on your PATH.
- Reinstall Python from python.org and check **"Add Python to PATH"**
- Or add manually: `Settings → System → About → Advanced system settings → Environment Variables → Path → Edit → Add C:\Users\<you>\AppData\Local\Programs\Python\Python312\`

### `'adk' is not recognized`

```powershell
# Ensure venv is active (you should see (.venv) in your prompt)
.venv\Scripts\activate

# Reinstall if needed
pip install google-adk
```

### `GOOGLE_API_KEY not set`

```powershell
# Check if it's set
echo $env:GOOGLE_API_KEY

# Set it again if empty
$env:GOOGLE_API_KEY = "your-key"
```

### Execution Policy Error (`.ps1 cannot be loaded`)

```powershell
# Run as Administrator:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Long path issues

```powershell
# Enable long paths (Run as Administrator):
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
    -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

---

## Architecture Notes

Same architecture applies as on macOS — see [setup_mac.md → Architecture Notes](setup_mac.md#architecture-notes).

Key difference: All shell commands use PowerShell syntax instead of bash/zsh.
