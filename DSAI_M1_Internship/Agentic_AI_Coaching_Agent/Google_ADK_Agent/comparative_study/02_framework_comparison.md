# Comparative Study — Agent Orchestration Frameworks

## 1. Frameworks Evaluated

| Framework | Version (2026) | Primary Use Case | License |
|-----------|---------------|------------------|---------|
| **Google ADK** | ≥ 0.3.0 | Gemini-native agent development | Apache 2.0 |
| **LangChain / LangGraph** | 0.3.x / 0.2.x | General-purpose LLM orchestration | MIT |
| **CrewAI** | 0.8.x | Multi-agent role-based collaboration | MIT |
| **Microsoft AutoGen** | 0.4.x | Multi-agent conversation patterns | MIT |
| **Semantic Kernel** | 1.x | Enterprise LLM orchestration (.NET/Python) | MIT |

---

## 2. Detailed Comparison Matrix

### 2.1 Core Capabilities

| Capability | Google ADK | LangChain/LangGraph | CrewAI | AutoGen | Semantic Kernel |
|-----------|-----------|--------------------|---------|---------|-----------------| 
| Single-agent orchestration | ✅ | ✅ | ✅ | ✅ | ✅ |
| Multi-agent orchestration | ✅ (Agent trees) | ✅ (StateGraph) | ✅ (Crew) | ✅ (GroupChat) | ⚠️ (Plugins) |
| Tool/function calling | ✅ Native | ✅ @tool | ✅ @tool | ✅ register | ✅ Plugins |
| Streaming responses | ✅ | ✅ | ⚠️ Limited | ⚠️ Limited | ✅ |
| Session memory | ✅ ToolContext.state | ✅ Memory classes | ⚠️ Basic | ✅ Chat history | ✅ Chat memory |
| Built-in UI | ✅ `adk web` | ❌ | ❌ | ❌ | ❌ |
| Async support | ✅ | ✅ | ⚠️ Partial | ✅ | ✅ |

### 2.2 Model Support

| Model Provider | Google ADK | LangChain | CrewAI | AutoGen | Semantic Kernel |
|---------------|-----------|-----------|---------|---------|-----------------|
| Gemini (native) | ✅ First-class | ⚠️ Via wrapper | ⚠️ Via LiteLLM | ⚠️ Via config | ⚠️ Via connector |
| OpenAI GPT-4o | ⚠️ Via LiteLLM | ✅ First-class | ✅ Default | ✅ Default | ✅ First-class |
| Anthropic Claude | ⚠️ Via LiteLLM | ✅ First-class | ✅ Via LiteLLM | ✅ Via config | ✅ Via connector |
| Open-source (Ollama) | ⚠️ Limited | ✅ | ✅ | ✅ | ⚠️ |
| Model hot-swap | ✅ Config change | ✅ | ✅ | ✅ | ✅ |

### 2.3 Development Experience

| Criterion | Google ADK | LangChain | CrewAI | AutoGen | Semantic Kernel |
|-----------|-----------|-----------|---------|---------|-----------------|
| Lines of code to "Hello Agent" | ~15 | ~25 | ~30 | ~40 | ~35 |
| Documentation quality | Good (growing) | Excellent | Good | Good | Excellent |
| Boilerplate required | Low | Medium | Medium | High | Medium |
| Debugging tools | ADK Web UI | LangSmith | ❌ | ❌ | ❌ |
| Testing utilities | Basic | ✅ LangSmith eval | ❌ | ❌ | ❌ |
| Type safety | Python annotations | Pydantic models | Pydantic | Pydantic | Strong typing |

### 2.4 Production Readiness

| Criterion | Google ADK | LangChain | CrewAI | AutoGen | Semantic Kernel |
|-----------|-----------|-----------|---------|---------|-----------------|
| Cloud deployment | ✅ Vertex AI native | ⚠️ Custom container | ⚠️ Custom container | ⚠️ Custom container | ✅ Azure native |
| Scalability | ✅ (via GCP) | ✅ (manual) | ⚠️ | ⚠️ | ✅ (via Azure) |
| Observability | ✅ Cloud Trace | ✅ LangSmith | ⚠️ Logs only | ⚠️ Logs only | ✅ App Insights |
| Auth/security | ✅ IAM | ⚠️ Manual | ⚠️ Manual | ⚠️ Manual | ✅ Azure AD |
| Cost at scale | Pay-per-request | Token costs + infra | Token costs + infra | Token costs + infra | Pay-per-request |

---

## 3. Architecture Patterns Comparison

### 3.1 Tool Definition

**Google ADK** — Plain Python functions with docstrings:
```python
def search_knowledge_base(query: str, max_results: int = 5) -> dict:
    """Search the SPIN selling knowledge base.
    
    Args:
        query: The topic to search for.
        max_results: Maximum results (1-10).
    Returns:
        Relevant training content sections.
    """
    # implementation
```

**LangChain** — Decorator with Pydantic schema:
```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(description="The topic to search for")
    max_results: int = Field(default=5, ge=1, le=10)

@tool(args_schema=SearchInput)
def search_knowledge_base(query: str, max_results: int = 5) -> str:
    """Search the SPIN selling knowledge base."""
    # implementation
```

**CrewAI** — Similar decorator pattern:
```python
from crewai_tools import tool

@tool("Knowledge Base Search")
def search_knowledge_base(query: str) -> str:
    """Search the SPIN selling knowledge base."""
    # implementation
```

**Verdict**: ADK has the lowest ceremony — function signature IS the schema.

### 3.2 Multi-Agent Communication

**Google ADK** — Hierarchical agent tree with delegation:
```python
root_agent = Agent(
    name="router",
    sub_agents=[teaching_agent, evaluation_agent, roleplay_agent],
    instruction="Route to the appropriate specialist agent..."
)
```

**LangGraph** — Explicit state machine with edges:
```python
graph = StateGraph(AgentState)
graph.add_node("teaching", teaching_node)
graph.add_node("evaluation", evaluation_node)
graph.add_edge("teaching", "evaluation")
graph.add_conditional_edges("router", route_function)
```

**CrewAI** — Task-based sequential/parallel execution:
```python
crew = Crew(
    agents=[teaching_agent, evaluation_agent],
    tasks=[teach_task, evaluate_task],
    process=Process.sequential
)
```

**AutoGen** — Conversation-based with group chat:
```python
groupchat = GroupChat(agents=[teacher, evaluator, user_proxy])
manager = GroupChatManager(groupchat=groupchat)
```

**Verdict**: ADK's agent tree is most natural for a coaching system where one coordinator
delegates to specialists. LangGraph offers more control for complex workflows.

---

## 4. Fitness for SPIN Coach Use Case

### Requirements vs Framework Fit

| Requirement | Best Fit | Why |
|------------|----------|-----|
| Real-time coaching conversation | ADK, LangChain | Low latency, streaming |
| Role-play persona management | ADK, AutoGen | State persistence per session |
| SPIN phase scoring | Any (tool-based) | Logic is in the tool, not framework |
| Knowledge retrieval (RAG) | LangChain, ADK | Both have strong RAG support |
| Session progress tracking | ADK | `ToolContext.state` is purpose-built |
| Built-in demo UI | ADK only | `adk web` requires zero frontend code |
| Future multi-agent expansion | ADK, LangGraph | Both support agent coordination |
| GCP deployment (Vertex AI) | ADK | Native integration |
| Rapid prototyping | ADK, CrewAI | Minimal boilerplate |

### Final Framework Selection: Google ADK

**Primary reasons:**
1. Zero-friction Gemini integration (our chosen LLM)
2. Built-in web UI eliminates frontend development time
3. `ToolContext.state` handles coaching session state naturally
4. Direct path to production via Vertex AI Agent Engine
5. Agent tree supports planned multi-agent expansion

**Trade-offs accepted:**
- Smaller community than LangChain (less Stack Overflow answers)
- Tighter vendor coupling (Google ecosystem)
- Less mature testing/evaluation tooling

---

## 5. Migration Paths

If requirements change, migration is feasible:

| From ADK To | Effort | What Changes |
|-------------|--------|-------------|
| LangChain | Medium | Rewrite agent definition, add ChatGoogleGenerativeAI, tools need @tool decorator |
| LangGraph | Medium | Define state schema, convert agent tree to graph, tools stay similar |
| CrewAI | Low-Medium | Define agents as CrewAI agents, tools use @tool, add task definitions |
| AutoGen | High | Fundamentally different conversation model, significant rework |

The tool implementations (`search_knowledge_base`, `evaluate_spin_message`, etc.) are
framework-agnostic Python functions — they can be reused across any framework with minimal
adaptation (just wrapping in the target framework's tool decorator).
