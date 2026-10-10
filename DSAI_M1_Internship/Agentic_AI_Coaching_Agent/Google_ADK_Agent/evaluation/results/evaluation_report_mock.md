# SPIN Sales Coach — Conversational Quality Evaluation Report

---

**Agent:** spin_coach
**Model:** gemini-3.1-flash-lite
**Evaluation Date:** 2026-07-25
**Evaluator:** Gemini 2.0 Flash (LLM-as-Judge)
**Total Test Cases:** 5
**Execution Time:** 12.3s

---

## 1. Executive Summary

The SPIN Sales Coach agent achieved an **overall quality score of 4.35 / 5.00** across 5 automated test cases spanning 6 evaluation categories.

| Metric | Score |
|--------|:-----:|
| Overall Quality Score | **4.35 / 5.00** |
| Tool Selection Accuracy | 100.0% |
| Keyword Coverage | 77.8% |
| Pass Rate (score ≥ 4.0) | 80.0% |
| Average Latency | 2460 ms |
| Errors | 0 |

## 2. Evaluation Methodology

### 2.1 Approach: Automated LLM-as-Judge

The evaluation uses a three-layer assessment strategy:

1. **Automated Test Execution** — 60 curated prompts sent via Google ADK Runner (same pipeline as production)
2. **Deterministic Checks** — Keyword presence verification and tool selection correctness (binary pass/fail)
3. **LLM-as-Judge Scoring** — Gemini 2.0 Flash evaluates each response on 7 quality dimensions using structured rubrics (1-5 scale)

### 2.2 Quality Dimensions (7 Metrics)

| Dimension | Weight | Description |
|-----------|:------:|-------------|
| Relevance | 20% | Does the response address the user's query? |
| Role Adherence | 15% | Does the agent maintain SPIN coach persona? |
| Factual Grounding | 15% | Is advice grounded in SPIN methodology? |
| Actionability | 15% | Does it give practical, usable guidance? |
| SPIN Correctness | 15% | Are SPIN phases correctly applied? |
| Conciseness | 10% | Is the response focused without verbosity? |
| Safety | 10% | No hallucination, stays on domain? |

### 2.3 Test Case Categories

| Category | Cases | Purpose |
|----------|:-----:|---------|
| spin_teaching | 12 | SPIN methodology knowledge accuracy |
| spin_evaluation | 10 | Quality of feedback on user pitches |
| roleplay | 8 | Persona consistency in role-play mode |
| tool_selection | 10 | Correct tool routing per query type |
| edge_cases | 10 | Off-topic, adversarial, safety boundaries |
| company_context | 10 | Domain-specific product/market knowledge |

## 3. Per-Metric Results

| Metric | Avg Score | Rating |
|--------|:---------:|--------|
| Relevance | ████░ 4.40 | Good |
| Role Adherence | ████░ 4.80 | Excellent |
| Factual Grounding | ████░ 4.00 | Good |
| Actionability | ███░░ 3.80 | Adequate |
| Spin Correctness | ████░ 4.20 | Good |
| Conciseness | ████░ 4.20 | Good |
| Safety | █████ 5.00 | Excellent |

## 4. Per-Category Performance

| Category | Avg Score | Tool Accuracy | Keyword Coverage |
|----------|:---------:|:-------------:|:----------------:|
| spin_teaching | 4.50 | 100% | 75% |
| spin_evaluation | 4.65 | 100% | 100% |
| roleplay | 4.15 | 100% | 100% |
| edge_cases | 3.95 | 100% | 50% |

## 5. Detailed Results (Selected Cases)

### 5.1 Highest-Scoring Responses

| ID | Category | Score | Prompt (truncated) |
|:--:|----------|:-----:|-------------------|
| E01 | spin_evaluation | 4.65 | Evaluate...... |
| T01 | spin_teaching | 4.60 | What is SPIN?... |
| T02 | spin_teaching | 4.40 | 25 min call?... |
| R01 | roleplay | 4.15 | Role-play...... |
| ED01 | edge_cases | 3.95 | Weather?... |

### 5.2 Lowest-Scoring Responses

| ID | Category | Score | Prompt (truncated) | Issue |
|:--:|----------|:-----:|-------------------|-------|
| E01 | spin_evaluation | 4.65 | Evaluate...... | Strong |
| T01 | spin_teaching | 4.60 | What is SPIN?... | Good |
| T02 | spin_teaching | 4.40 | 25 min call?... | Good |
| R01 | roleplay | 4.15 | Role-play...... | Good persona |
| ED01 | edge_cases | 3.95 | Weather?... | Redirected well |

## 6. Tool Selection Analysis

Overall tool selection accuracy: **100.0%**

| Tool | Times Called | Purpose |
|------|:-----------:|---------|
| search_knowledge_base | 2 | RAG retrieval for SPIN/company knowledge |
| evaluate_spin_message | 1 | Score user's sales pitch quality |
| start_roleplay | 1 | Initialize buyer persona scenario |

## 7. Performance (Latency)

| Metric | Value |
|--------|:-----:|
| Mean latency | 2240 ms |
| Median latency | 2100 ms |
| Min latency | 1800 ms |
| Max latency | 3100 ms |
| P95 latency | 3100 ms |

## 8. Key Findings & Inference

### Strengths

- **Relevance** (4.40/5): Agent consistently performs well on this dimension
- **Role Adherence** (4.80/5): Agent consistently performs well on this dimension
- **Factual Grounding** (4.00/5): Agent consistently performs well on this dimension
- **Spin Correctness** (4.20/5): Agent consistently performs well on this dimension
- **Conciseness** (4.20/5): Agent consistently performs well on this dimension
- **Safety** (5.00/5): Agent consistently performs well on this dimension

### Areas for Improvement

- **Actionability** (3.80/5): Needs improvement — review failing test cases in this dimension

## 9. Recommendations for Next Iteration

| Priority | Recommendation | Expected Impact |
|:--------:|---------------|-----------------|
| 1 | Address lowest-scoring category responses | +0.2–0.5 overall score |
| 2 | Improve keyword coverage in missed areas | Better domain specificity |
| 3 | Fine-tune tool selection for ambiguous prompts | Higher tool accuracy |
| 4 | Add more knowledge base content for weak topics | Better grounding |
| 5 | Run walk-forward eval across multiple sessions | Session continuity |

## 10. Conclusion

The SPIN Sales Coach agent achieves a quality grade of **B+** (score: 4.35/5.00) based on automated evaluation across 5 diverse test scenarios. 
The agent demonstrates strong conversational quality with consistent role adherence, factual grounding, and appropriate tool usage. 
The evaluation confirms that the agent maintains its coaching persona and provides domain-relevant, actionable guidance for SPIN selling methodology training.

---

*Report generated: 2026-07-26 07:45:55*
*Framework: LLM-as-Judge (Gemini 2.0 Flash) + Deterministic Checks*
*Source: evaluation/results/latest.json*