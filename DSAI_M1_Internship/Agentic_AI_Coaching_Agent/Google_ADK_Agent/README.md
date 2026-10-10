# SPIN Sales Coach — Google ADK Agent

> **Proof-of-concept project** built as part of an MSc Data Science & AI internship,
> exploring agentic AI with Google ADK. All data is synthetic and not tied to any
> real company.

An AI-powered Sales Training Agent built with Google ADK + Gemini that coaches
Sales Representatives using the **SPIN Selling** methodology (Situation, Problem,
Implication, Need-Payoff). Focused on training reps at an **animal pharma company**
to be time-focused and budget-focused in their sales conversations.

---

## Project Structure

```
GoogleADKAgent/
├── README.md                          # This file
├── data/
│   ├── raw_data/                      # Raw training content (SPIN methodology + company context)
│   ├── training_data/                 # Processed data for RAG (chunked, formatted)
│   └── test_data/                     # Test queries and expected responses
├── learnings/
│   └── SPIN_methodology.md           # Reference doc on SPIN selling
├── prerequisites/
│   ├── setup_mac.md                   # Local setup instructions (Intel + Apple Silicon)
│   └── setup_gcloud.md               # Google Cloud setup (optional)
├── agent/
│   ├── spin_coach/                    # ADK Agent package
│   │   ├── __init__.py
│   │   ├── agent.py                   # Agent definition
│   │   └── tools.py                   # RAG tools + coaching tools
│   └── run_agent.py                   # Programmatic runner (optional)
├── scripts/
│   ├── prepare_data.py                # Converts raw_data -> training_data + test_data
│   └── test_agent.py                  # Quick smoke test
├── requirements.txt                   # Python dependencies
└── Makefile                           # Convenience commands
```

---

## Quick Start

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set Gemini API key
export GOOGLE_API_KEY="your-key-from-aistudio.google.com"

# 4. Prepare RAG data
python scripts/prepare_data.py

# 5. Launch the agent (ADK Web UI)
cd agent
adk web

# 6. Open http://localhost:8000, select spin_coach, start training!
```

---

## How It Works

1. **RAG Knowledge Base**: The agent has access to SPIN methodology training material,
   company product knowledge, and sales scenario examples via a retrieval tool.
2. **Coaching Mode**: The agent role-plays as a veterinarian/clinic buyer and the
   sales rep practices SPIN conversations.
3. **Feedback Mode**: The agent analyzes a rep's sales pitch and provides structured
   feedback on SPIN technique, time-focus, and budget-focus.

---

## SPIN Methodology Quick Reference

| Phase | Purpose | Example Question |
|-------|---------|-----------------|
| **S**ituation | Understand current state | "How many pets does your clinic treat monthly?" |
| **P**roblem | Identify pain points | "What challenges do you face with current parasite treatments?" |
| **I**mplication | Amplify the impact | "How does treatment failure affect client retention?" |
| **N**eed-Payoff | Show the value | "If you could reduce retreatment by 40%, what would that mean for your practice?" |

---

## Tech Stack

- **Google ADK** — Agent framework
- **Gemini 2.0 Flash** — LLM for reasoning
- **ADK Web UI** — Built-in chat interface (no custom UI needed)
- **Python** — All code
- **Works on**: macOS Intel, macOS Apple Silicon, Linux
