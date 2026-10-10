# Technical Architecture — SPIN Sales Coach Multi-Agent System

## 1. System Overview

The SPIN Sales Coach is a conversational AI agent built on **Google ADK** (Agent Development Kit)
that trains pharmaceutical sales representatives using the SPIN Selling methodology.
It combines LLM-powered conversational coaching with a domain-specific knowledge retrieval system.

```
┌─────────────────────────────────────────────────────────────────┐
│                     ADK Web UI (localhost:8000)                  │
├─────────────────────────────────────────────────────────────────┤
│                  Google ADK Orchestration Layer                  │
│                  ┌─────────────────────────────┐                │
│                  │      spin_coach (Agent)      │                │
│                  │   model: gemini-2.0-flash    │                │
│                  │   mode: Teaching / Eval / RP │                │
│                  └────────────┬────────────────┘                │
│                               │                                  │
│              ┌────────────────┼────────────────┐                │
│              ▼                ▼                ▼                  │
│   ┌──────────────┐  ┌──────────────┐  ┌───────────────┐        │
│   │search_kb     │  │evaluate_spin │  │start_roleplay │        │
│   │(RAG Tool)    │  │(Scoring Tool)│  │(Scenario Tool)│        │
│   └──────┬───────┘  └──────────────┘  └───────────────┘        │
│          │                                                       │
│          ▼                                                       │
│   ┌──────────────────┐                                          │
│   │knowledge_base.json│  (54 chunks from 4 source documents)    │
│   └──────────────────┘                                          │
├─────────────────────────────────────────────────────────────────┤
│            Gemini API (generativelanguage.googleapis.com)        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. LLM Model Selection

### Chosen Model: Gemini 2.0 Flash

| Attribute | Value |
|-----------|-------|
| Model ID | `gemini-2.0-flash` |
| Provider | Google DeepMind |
| Context Window | 1M tokens |
| Tool Calling | Native function-calling support |
| Latency | ~0.5–1.5s per response (typical) |
| Cost (Free Tier) | 15 RPM / 1,500 RPD / 1M TPM |

### Rationale for Model Choice

| Criterion | Gemini 2.0 Flash | GPT-4o | Claude 3.5 Sonnet |
|-----------|-----------------|--------|-------------------|
| Native ADK integration | ✅ First-class | ❌ Requires adapter | ❌ Requires adapter |
| Function/tool calling | ✅ Native | ✅ Native | ✅ Native |
| Latency for coaching | ✅ Fast (~1s) | ⚠️ Medium (~2s) | ⚠️ Medium (~2s) |
| Free tier for prototyping | ✅ 15 RPM free | ❌ Pay-per-token | ❌ Pay-per-token |
| Multilingual (French/English) | ✅ Strong | ✅ Strong | ✅ Strong |
| Role-play persona consistency | ✅ Good | ✅ Very good | ✅ Excellent |
| Instruction following | ✅ Good | ✅ Very good | ✅ Excellent |

**Decision**: Gemini 2.0 Flash was selected because:
1. It is the native model for Google ADK — zero integration friction
2. Free tier is sufficient for development and evaluation (15 RPM)
3. Latency is optimal for real-time coaching conversations
4. Function calling is seamless (no schema translation needed)
5. 1M context window accommodates large knowledge base retrieval

### Model Alternatives Considered

| Model | Rejected Because |
|-------|-----------------|
| Gemini 2.5 Pro | Lower free tier (5 RPM), unnecessary for coaching use case |
| Gemini 2.0 Flash-Lite | Weaker instruction following for complex role-play |
| GPT-4o (via LiteLLM) | Adds dependency, no ADK native support, cost |
| Claude 3.5 Sonnet | No ADK integration, requires custom orchestration |
| Open-source (Llama 3, Mistral) | Requires GPU hosting, weaker tool calling |

---

## 3. Orchestration Framework

### Chosen Framework: Google ADK (Agent Development Kit)

| Attribute | Value |
|-----------|-------|
| Version | ≥ 0.3.0 |
| Architecture | Single-agent with tool augmentation |
| Session Management | In-memory (stateful within session) |
| Tool Protocol | Python functions with type annotations |
| UI | Built-in ADK Web UI |
| Deployment Options | Local / Cloud Run / Vertex AI Agent Engine |

### ADK vs Alternative Frameworks

| Criterion | Google ADK | LangChain/LangGraph | CrewAI | AutoGen |
|-----------|-----------|--------------------|---------|---------| 
| Gemini-native | ✅ Zero config | ⚠️ Via ChatGoogleGenerativeAI | ⚠️ Via LiteLLM | ⚠️ Via config |
| Tool definition | ✅ Plain Python functions | ⚠️ @tool decorator + schema | ⚠️ @tool decorator | ⚠️ Custom format |
| Multi-agent orchestration | ✅ Built-in (Agent trees) | ✅ LangGraph StateGraph | ✅ Crew + Tasks | ✅ GroupChat |
| State management | ✅ ToolContext.state | ⚠️ Manual (memory classes) | ⚠️ Limited | ⚠️ Manual |
| Built-in UI | ✅ `adk web` | ❌ Requires custom | ❌ Requires custom | ❌ Requires custom |
| Deployment to GCP | ✅ Native Vertex AI | ⚠️ Manual containerize | ⚠️ Manual containerize | ⚠️ Manual containerize |
| Learning curve | Low | Medium | Low | High |
| Maturity (as of 2026) | Medium | High | Medium | Medium |
| Community/ecosystem | Growing | Large | Growing | Growing |

**Decision**: Google ADK was selected because:
1. Native Gemini integration eliminates model-framework impedance mismatch
2. Built-in web UI eliminates frontend development for prototyping
3. `ToolContext.state` provides session state without external databases
4. Direct deployment path to Vertex AI Agent Engine for production
5. Agent tree architecture supports future multi-agent expansion

### Current Architecture: Single Agent with Tools

```python
root_agent = Agent(
    name="spin_coach",
    model="gemini-2.0-flash",
    tools=[search_knowledge_base, evaluate_spin_message, get_coaching_progress, start_roleplay],
)
```

### Future Multi-Agent Extension (Planned)

```
root_agent (Router)
├── teaching_agent       → Knowledge retrieval + explanation
├── evaluation_agent     → SPIN scoring + feedback generation
├── roleplay_agent       → Persona simulation + scenario management
└── analytics_agent      → Progress tracking + adaptive difficulty
```

The ADK agent tree model supports this directly via sub-agents with delegation.

---

## 4. Knowledge Retrieval Architecture (RAG)

### Implementation

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Chunking | Custom Python script | Domain-specific markdown sections |
| Storage | JSON file (54 chunks) | Sufficient for prototype scale |
| Retrieval | Keyword scoring + SPIN phase boosting | Lightweight, no vector DB dependency |
| Embedding | None (keyword-based) | Avoids additional API calls, fast |

### Retrieval Scoring Algorithm

```
score = Σ(word_frequency_in_content) + 5×(word_in_section_title) + 20×(exact_phrase_match) + 10×(SPIN_phase_keyword_boost)
```

### Data Sources (4 documents → 54 chunks)

| Document | Content | Chunks |
|----------|---------|--------|
| 01_spin_methodology.md | SPIN theory, phases, time/budget frameworks | ~20 |
| 02_company_product_knowledge.md | Products, positioning, competitive landscape | ~15 |
| 03_sales_scenarios.md | Objection handling, clinic types, practice scripts | ~12 |
| 04_time_budget_coaching.md | Efficiency tips, ROI calculation, call structure | ~7 |

### Limitations of Current Approach

| Limitation | Impact | Mitigation Path |
|-----------|--------|-----------------|
| No semantic similarity | Misses paraphrased queries | Add text-embedding-004 |
| No chunk ranking by recency | All content equal weight | Add timestamp metadata |
| No user-specific adaptation | Same content for all reps | Add user profile state |
| 54 chunks only | Limited domain coverage | Expand corpus, add vector DB |

---

## 5. Session State Architecture

Google ADK's `ToolContext.state` provides in-memory session persistence:

```python
# State schema (per session)
{
    "evaluation_history": [
        {"phase": "problem", "score": "3/4", "rating": "Good"},
        {"phase": "implication", "score": "4/4", "rating": "Excellent"}
    ],
    "roleplay_count": 2,
    "active_roleplay": {
        "scenario": {...},
        "difficulty": "medium",
        "started": True
    }
}
```

**Trade-offs:**
- ✅ No database required for development
- ✅ Fast access (in-memory dict)
- ❌ Lost on server restart
- ❌ No cross-session learning

---

## 6. Contribution to Multi-Agent System

### This Prototype Contributes

| Contribution | Description |
|-------------|-------------|
| Domain-specific coaching agent | Proof that LLM + SPIN rules can effectively train sales reps |
| Role-play simulation | Demonstrates persona-based conversation with progressive disclosure |
| SPIN evaluation framework | Rule-based scoring that complements LLM judgment |
| RAG pipeline for training content | Reusable pattern for knowledge-grounded coaching |
| Session-based progress tracking | Foundation for adaptive learning difficulty |

### Integration Points with Broader Multi-Agent System

| System Component | Integration Method |
|-----------------|-------------------|
| User Management | Session ID → user profile mapping |
| Analytics Dashboard | Export `evaluation_history` via API |
| Content Management | Add chunks to `knowledge_base.json` |
| Manager Oversight | Read coaching progress per rep |
| A/B Testing | Swap model or instructions without code changes |

---

## 7. Deployment Architecture Options

| Environment | Stack | Use Case |
|-------------|-------|----------|
| Local dev | `adk web` → localhost:8000 | Development, testing |
| Cloud Run | Docker + `adk web` | Team access, demo |
| Vertex AI Agent Engine | Managed agent hosting | Production, scaling |

All three paths are documented in [Setup_Kit.md](../Setup_Kit.md) and
[Setup_Kit_windows.md](../Setup_Kit_windows.md).
