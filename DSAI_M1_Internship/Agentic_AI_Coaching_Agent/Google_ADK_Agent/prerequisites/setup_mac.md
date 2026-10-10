# Local Setup — macOS (Intel + Apple Silicon)

## Prerequisites

- macOS 13+ (Ventura or later)
- Python 3.10+ (works on both Intel and Apple Silicon)
- A Gemini API key (free from aistudio.google.com)

---

## Step 1: Install Python (if needed)

```bash
# Check current version
python3 --version

# If below 3.10, install via Homebrew
brew install python@3.12
```

---

## Step 2: Clone and Setup

```bash
cd /path/to/LearnGoogleADK/GoogleADKAgent

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify ADK is installed
adk --help
```

---

## Step 3: Configure API Key

```bash
# Get a free key from https://aistudio.google.com
export GOOGLE_API_KEY="your-api-key-here"

# Persist it (add to your shell profile)
echo 'export GOOGLE_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

---

## Step 4: Prepare Data

```bash
python scripts/prepare_data.py
```

Expected output:
```
Processing: 01_spin_methodology.md
  → XX chunks extracted
Processing: 02_company_product_knowledge.md
  → XX chunks extracted
...
DATA PREPARATION COMPLETE
```

---

## Step 5: Run the Agent

```bash
cd agent
adk web
```

Open **http://localhost:8000** in your browser. Select `spin_coach` from the dropdown.

---

## Step 6: Test Conversations

Try these to verify everything works:

1. "What is SPIN selling?"
2. "Give me 3 good Problem questions for a small vet clinic"
3. "Evaluate my question: How many patients do you see each week?"
4. "Let's role-play — start a scenario with a small solo clinic"
5. "How should I handle a budget objection?"

---

## Troubleshooting

### `command not found: adk`
```bash
source .venv/bin/activate  # Ensure venv is active
pip install google-adk     # Reinstall if needed
```

### `GOOGLE_API_KEY not set`
```bash
export GOOGLE_API_KEY="your-key"
# Or check: echo $GOOGLE_API_KEY
```

### `Knowledge base not loaded`
```bash
cd /path/to/GoogleADKAgent  # Must be in project root
python scripts/prepare_data.py
```

### Slow on Intel Mac
The agent itself is lightweight (API calls to Gemini). If `pip install` is slow,
try: `pip install --prefer-binary google-adk`

---

## Architecture Notes

- **No GPU needed** — all LLM computation happens server-side (Gemini API)
- **No Docker needed** — pure Python, runs directly in venv
- **No database needed** — sessions are in-memory (fine for learning/dev)
- **Works offline?** — No, requires internet for Gemini API calls
- **Intel vs Apple Silicon** — identical setup, no architecture-specific steps
