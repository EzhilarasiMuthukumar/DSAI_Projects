# Comparative Study — Technology Choices

This folder contains detailed comparative analyses of the technology decisions
made for the SPIN Sales Coach multi-agent system. Each document provides
rigorous technical justification suitable for defending in a final report.

---

## Documents

| # | Document | Purpose |
|---|----------|---------|
| 01 | [Technical Architecture](01_technical_architecture.md) | Full system architecture diagram, component descriptions, contribution to multi-agent system |
| 02 | [Framework Comparison](02_framework_comparison.md) | Google ADK vs LangChain vs CrewAI vs AutoGen vs Semantic Kernel |
| 03 | [LLM Model Comparison](03_llm_model_comparison.md) | Gemini 2.0 Flash vs GPT-4o vs Claude 3.5 Sonnet — quantitative scoring |
| 04 | [Evaluation Metrics](04_evaluation_metrics.md) | Conversational quality metrics, quantitative evaluation results, claims for defense |
| 05 | [RAG Strategies](05_rag_strategies_comparison.md) | Keyword vs TF-IDF vs Embeddings vs Vector DB — trade-off analysis |

---

## How to Use These Documents

### For Final Report Defense

- **Document 01** establishes what was built and how it contributes to the multi-agent system
- **Documents 02–03** justify WHY specific technologies were chosen (with quantitative comparison)
- **Document 04** provides the quantitative evaluation evidence (metrics, scores, reproducible protocol)
- **Document 05** defends the RAG approach with a clear upgrade path

### Key Quantitative Claims (from Document 04)

| Metric | Value | Evidence |
|--------|-------|----------|
| Topic Coverage | 88.5% | 8 standardized test queries |
| Tool Calling Accuracy | 100% | 8/8 correct invocations |
| Response Quality | 4.25/5.0 | Expert evaluation |
| Median Latency | 1.25s | Real-time capable |
| RAG MRR | 0.78 | Keyword approach, 54-chunk corpus |
| Weighted Model Score | 86.3/100 | 7-criteria weighted evaluation |

### Mentor Feedback Addressed

| Feedback Point | Where Addressed |
|----------------|-----------------|
| Clarify contribution to multi-agent system | Document 01, Section 6 |
| Describe technical architecture rigorously | Document 01, Sections 1–5 |
| Specify which LLM models | Document 03, full comparison |
| Specify orchestration framework | Document 02, full comparison |
| Define metrics for evaluating conversational quality | Document 04, Sections 2–3 |
| Produce quantitative evaluation | Document 04, Sections 4–5 |
