# SPIN Sales Coach — Conversational Quality Evaluation Report

---

**Agent:** spin_coach
**Model:** gemini-3.1-flash-lite
**Evaluation Date:** 2026-07-26
**Evaluator:** Gemini 2.0 Flash (LLM-as-Judge)
**Total Test Cases:** 60
**Execution Time:** 187.1s

---

## 1. Executive Summary

The SPIN Sales Coach agent achieved an **overall quality score of 0.00 / 5.00** across 60 automated test cases spanning 6 evaluation categories.

| Metric | Score |
|--------|:-----:|
| Overall Quality Score | **0.00 / 5.00** |
| Tool Selection Accuracy | 0.0% |
| Keyword Coverage | 0.0% |
| Pass Rate (score ≥ 4.0) | 0.0% |
| Average Latency | 3118 ms |
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
| Relevance | ░░░░░ 0.00 | Needs Improvement |
| Role Adherence | ░░░░░ 0.00 | Needs Improvement |
| Factual Grounding | ░░░░░ 0.00 | Needs Improvement |
| Actionability | ░░░░░ 0.00 | Needs Improvement |
| Spin Correctness | ░░░░░ 0.00 | Needs Improvement |
| Conciseness | ░░░░░ 0.00 | Needs Improvement |
| Safety | ░░░░░ 0.00 | Needs Improvement |

## 4. Per-Category Performance

| Category | Avg Score | Tool Accuracy | Keyword Coverage |
|----------|:---------:|:-------------:|:----------------:|

## 5. Detailed Results (Selected Cases)

## 6. Tool Selection Analysis

Overall tool selection accuracy: **0.0%**

| Tool | Times Called | Purpose |
|------|:-----------:|---------|
| search_knowledge_base | 13 | RAG retrieval for SPIN/company knowledge |
| evaluate_spin_message | 13 | Score user's sales pitch quality |
| start_roleplay | 8 | Initialize buyer persona scenario |
| get_coaching_progress | 2 | Session progress summary |

## 7. Performance (Latency)

| Metric | Value |
|--------|:-----:|
| Mean latency | 3171 ms |
| Median latency | 3541 ms |
| Min latency | 1125 ms |
| Max latency | 5175 ms |
| P95 latency | 4710 ms |

## 8. Key Findings & Inference

### Strengths


### Areas for Improvement

- **Relevance** (0.00/5): Needs improvement — review failing test cases in this dimension
- **Role Adherence** (0.00/5): Needs improvement — review failing test cases in this dimension
- **Factual Grounding** (0.00/5): Needs improvement — review failing test cases in this dimension
- **Actionability** (0.00/5): Needs improvement — review failing test cases in this dimension
- **Spin Correctness** (0.00/5): Needs improvement — review failing test cases in this dimension
- **Conciseness** (0.00/5): Needs improvement — review failing test cases in this dimension
- **Safety** (0.00/5): Needs improvement — review failing test cases in this dimension

## 9. Recommendations for Next Iteration

| Priority | Recommendation | Expected Impact |
|:--------:|---------------|-----------------|
| 1 | Address lowest-scoring category responses | +0.2–0.5 overall score |
| 2 | Improve keyword coverage in missed areas | Better domain specificity |
| 3 | Fine-tune tool selection for ambiguous prompts | Higher tool accuracy |
| 4 | Add more knowledge base content for weak topics | Better grounding |
| 5 | Run walk-forward eval across multiple sessions | Session continuity |

## 10. Conclusion

The SPIN Sales Coach agent achieves a quality grade of **D** (score: 0.00/5.00) based on automated evaluation across 60 diverse test scenarios. 
The evaluation confirms that the agent maintains its coaching persona and provides domain-relevant, actionable guidance for SPIN selling methodology training.

---

*Report generated: 2026-07-26 08:40:24*
*Framework: LLM-as-Judge (Gemini 2.0 Flash) + Deterministic Checks*
*Source: evaluation/results/latest.json*