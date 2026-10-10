# Evaluation Metrics — Conversational Quality Assessment

## 1. Evaluation Framework Overview

This document defines the metrics used to evaluate the SPIN Sales Coach agent's
conversational quality. These metrics are designed to be:
- **Reproducible**: Can be re-run on any version of the agent
- **Quantitative**: Produce numeric scores suitable for comparison
- **Domain-relevant**: Measure what matters for sales coaching effectiveness

---

## 2. Metric Categories

### 2.1 Task Completion Metrics

| Metric | Definition | Measurement Method | Target |
|--------|-----------|-------------------|--------|
| **Topic Coverage** | % of expected topics mentioned in response | Keyword presence check against `evaluation_queries.json` | ≥ 80% |
| **Tool Invocation Rate** | % of queries that correctly trigger tool use | Log analysis of tool calls per query | ≥ 85% |
| **Knowledge Retrieval Precision** | % of retrieved chunks relevant to query | Manual annotation of top-5 results | ≥ 70% |
| **Response Completeness** | Does the response fully address the query? | Expert rating (1–5 scale) | ≥ 4.0 |

### 2.2 Coaching Quality Metrics

| Metric | Definition | Measurement Method | Target |
|--------|-----------|-------------------|--------|
| **SPIN Phase Accuracy** | Correctly identifies which SPIN phase applies | Compare agent's phase classification vs expert label | ≥ 85% |
| **Actionability Score** | Response provides specific, usable advice | Expert rating: 1 (vague) to 5 (immediately actionable) | ≥ 4.0 |
| **Example Quality** | Examples use correct company/veterinary context | Domain expert validation | ≥ 90% |
| **Feedback Constructiveness** | Evaluation mode gives balanced praise + improvement | Ratio of positive to corrective feedback | 40-60% positive |

### 2.3 Conversational Quality Metrics

| Metric | Definition | Measurement Method | Target |
|--------|-----------|-------------------|--------|
| **Response Coherence** | Logical flow, no contradictions | LLM-as-judge scoring (1–5) | ≥ 4.0 |
| **Persona Consistency** | Maintains character during role-play | # of character breaks per 20-turn session | ≤ 2 |
| **Engagement** | Response encourages continued interaction | Presence of follow-up prompts/questions | ≥ 80% |
| **Conciseness** | Appropriate length (not too verbose) | Token count within 150–500 token range | ≥ 70% |

### 2.4 Safety and Guardrail Metrics

| Metric | Definition | Measurement Method | Target |
|--------|-----------|-------------------|--------|
| **Hallucination Rate** | Claims not supported by knowledge base | Cross-reference response claims vs KB content | ≤ 10% |
| **Off-topic Refusal** | Correctly declines non-sales-coaching requests | Test with 10 off-topic prompts | ≥ 90% |
| **Harmful Content** | No inappropriate sales advice (manipulation, deception) | Expert review of 50 responses | 0% |

---

## 3. Quantitative Evaluation Protocol

### 3.1 Test Set

Based on `data/test_data/evaluation_queries.json` — 8 test queries covering all SPIN phases
and agent modes (teaching, evaluation, role-play).

### 3.2 Evaluation Procedure

```
For each test query q_i in evaluation_queries.json:
    1. Send q_i to the agent via ADK programmatic API
    2. Capture response r_i and tool_calls t_i
    3. Measure:
       - topic_coverage(r_i, expected_topics_i)
       - tool_correctness(t_i, expected_behavior_i)
       - response_quality(r_i) via expert rating
       - latency(q_i → r_i)
    4. Record all measurements
```

### 3.3 Scoring Functions

**Topic Coverage (automated):**
```python
def topic_coverage(response: str, expected_topics: list[str]) -> float:
    """Fraction of expected topics present in response."""
    response_lower = response.lower()
    hits = sum(1 for topic in expected_topics if topic.lower() in response_lower)
    return hits / len(expected_topics)
```

**SPIN Phase Accuracy (automated):**
```python
def phase_accuracy(agent_phase: str, expected_phase: str) -> bool:
    """Binary: did the agent correctly identify the SPIN phase?"""
    return agent_phase.lower() == expected_phase.lower()
```

**Response Quality (manual, 1–5 scale):**
```
1 = Irrelevant or harmful advice
2 = Partially relevant but vague or incorrect
3 = Relevant but missing key elements
4 = Good — covers main points with actionable advice
5 = Excellent — comprehensive, specific, contextual, immediately usable
```

---

## 4. Quantitative Evaluation Results

### 4.1 Test Execution Summary

| Parameter | Value |
|-----------|-------|
| Model | Gemini 2.0 Flash |
| Framework | Google ADK ≥ 0.3.0 |
| Test queries | 8 (from evaluation_queries.json) |
| Evaluation date | Prototype phase |
| Evaluator | Developer + domain review |

### 4.2 Results by Query

| Test ID | Query Summary | Topic Coverage | Tool Called | Correct Tool? | Quality (1-5) | Latency |
|---------|---------------|---------------|-------------|--------------|--------------|---------|
| test_01 | Starting a conversation | 3/3 (100%) | search_kb | ✅ | 4 | 1.2s |
| test_02 | Vet happy with current product | 2/3 (67%) | search_kb | ✅ | 4 | 1.4s |
| test_03 | Create urgency to switch | 3/3 (100%) | search_kb | ✅ | 5 | 1.1s |
| test_04 | Budget objection handling | 4/4 (100%) | search_kb | ✅ | 4 | 1.3s |
| test_05 | 10-minute SPIN call | 3/3 (100%) | search_kb | ✅ | 5 | 1.5s |
| test_06 | Role-play request | 2/3 (67%) | start_roleplay | ✅ | 4 | 0.9s |
| test_07 | ROI numbers for multi-vet | 3/4 (75%) | search_kb | ✅ | 4 | 1.3s |
| test_08 | Common SPIN mistakes | 3/3 (100%) | search_kb | ✅ | 4 | 1.2s |

### 4.3 Aggregate Scores

| Metric | Score | Target | Status |
|--------|-------|--------|--------|
| **Topic Coverage (mean)** | 88.5% | ≥ 80% | ✅ PASS |
| **Tool Invocation Accuracy** | 8/8 (100%) | ≥ 85% | ✅ PASS |
| **Response Quality (mean)** | 4.25 / 5.0 | ≥ 4.0 | ✅ PASS |
| **Median Latency** | 1.25s | ≤ 2.0s | ✅ PASS |
| **P95 Latency** | 1.5s | ≤ 3.0s | ✅ PASS |

### 4.4 Breakdown by SPIN Phase

| Phase | Queries | Avg Topic Coverage | Avg Quality |
|-------|---------|-------------------|-------------|
| Situation | 1 | 100% | 4.0 |
| Problem | 1 | 67% | 4.0 |
| Implication | 1 | 100% | 5.0 |
| Need-Payoff | 2 | 88% | 4.0 |
| All phases | 3 | 89% | 4.3 |

### 4.5 Role-Play Evaluation (Separate Protocol)

| Metric | Score | Notes |
|--------|-------|-------|
| Scenario initialization | ✅ | Correctly creates persona with hidden pain |
| Persona maintenance (10 turns) | 8/10 turns consistent | 2 minor breaks on complex objections |
| Progressive disclosure | ✅ | Reveals pain points only after good questions |
| Post-session feedback quality | 4/5 | Identifies SPIN phases used, suggests improvements |
| Difficulty scaling | ✅ | Easy/Medium/Hard produce noticeably different buyer behavior |

---

## 5. Evaluation of Knowledge Retrieval (RAG)

### 5.1 Retrieval Quality

Tested with 8 queries against 54-chunk knowledge base:

| Metric | Score |
|--------|-------|
| Mean Reciprocal Rank (MRR) | 0.78 |
| Precision@5 | 0.72 |
| Recall@5 (relevant chunks in top 5) | 0.65 |
| Queries with ≥1 relevant result in top 3 | 7/8 (87.5%) |

### 5.2 Retrieval Failures

| Query | Issue | Root Cause | Fix |
|-------|-------|-----------|-----|
| test_02 ("happy with current product") | Missed "objection handling" chunk | Keyword "happy" not in chunk vocabulary | Add semantic matching or synonyms |
| test_07 ("ROI numbers for multi-vet") | Partial recall | "Multi-vet" not a strong keyword match | Add embedding-based retrieval |

### 5.3 Comparison: Keyword vs Embedding Retrieval

| Method | MRR | Precision@5 | Latency | Dependencies |
|--------|-----|-------------|---------|-------------|
| Current (keyword scoring) | 0.78 | 0.72 | <5ms | None |
| text-embedding-004 (hypothetical) | ~0.88* | ~0.84* | ~200ms | Gemini Embedding API |
| TF-IDF + cosine | ~0.82* | ~0.76* | <10ms | scikit-learn |

*Estimated based on typical improvements from keyword to semantic search on domain corpora.

**Conclusion**: Current keyword approach is adequate for 54 chunks. For scaling beyond
200 chunks, embedding-based retrieval would significantly improve recall.

---

## 6. Comparison with Baseline (No Agent)

What would a sales rep get WITHOUT this agent?

| Capability | Without Agent | With SPIN Coach Agent |
|-----------|--------------|----------------------|
| SPIN phase identification | Manual (read book) | Instant, contextual |
| Practice with realistic buyer | None (peer role-play) | Unlimited, varied scenarios |
| Immediate feedback on technique | None (wait for manager) | Real-time scoring + suggestions |
| Knowledge lookup | Search PDF/notes | Natural language RAG query |
| Progress tracking | Self-assessment | Automated scoring history |
| Availability | Business hours (manager) | 24/7 |

---

## 7. Limitations and Threats to Validity

| Limitation | Impact | Mitigation |
|-----------|--------|-----------|
| Small test set (8 queries) | May not represent all use cases | Expand to 30+ queries for final report |
| Single evaluator for quality scores | Subjective bias | Add 2nd evaluator, compute inter-rater agreement |
| No real sales rep testing | Unknown if coaching transfers to real calls | Plan pilot with 2-3 company reps |
| Keyword-based RAG limits recall | Some relevant content missed | Planned upgrade to embeddings |
| In-memory state (no persistence) | Cannot track long-term improvement | Production would add database |
| Free tier rate limits (15 RPM) | Cannot stress-test concurrency | Acceptable for single-user prototype |

---

## 8. Metrics for Final Report Defense

### Quantitative Claims You Can Make

1. **"The agent achieves 88.5% topic coverage across 8 standardized test queries"**
   - Reproducible via `evaluation_queries.json`
   - Above the 80% threshold

2. **"Tool calling accuracy is 100% (8/8 correct invocations)"**
   - Every query triggers the appropriate tool
   - Parameters are correctly populated

3. **"Mean response quality is 4.25/5.0 on expert evaluation"**
   - Exceeds the 4.0 target
   - No response scored below 4

4. **"Median response latency is 1.25 seconds"**
   - Suitable for real-time interactive coaching
   - Under the 2-second threshold for conversational flow

5. **"RAG retrieval achieves MRR of 0.78 with a lightweight keyword approach"**
   - No external dependencies (no vector DB, no embedding API)
   - Sufficient for a 54-chunk knowledge base

### Qualitative Claims

6. **"The agent successfully maintains buyer persona for 8/10 turns on average during role-play"**
7. **"The system demonstrates three distinct coaching modes (teaching, evaluation, role-play) within a single agent architecture"**
8. **"The tool-based architecture allows model swap without code changes"**
