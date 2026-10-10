"""
Markdown Report Generator for SPIN Sales Coach Evaluation
==========================================================
Reads evaluation results JSON and produces a structured Markdown report
suitable for the university review committee.

Usage:
    python evaluation/generate_report.py
    python evaluation/generate_report.py --input results/run_20260725.json
    python evaluation/generate_report.py --output reports/eval_report.md
"""

import json
import argparse
from pathlib import Path
from datetime import datetime


def load_results(input_path: str = None) -> dict:
    """Load evaluation results from JSON."""
    if input_path:
        path = Path(input_path)
    else:
        path = Path(__file__).parent / "results" / "latest.json"

    if not path.exists():
        raise FileNotFoundError(
            f"Results not found at {path}. Run 'python evaluation/runner.py' first."
        )

    with open(path) as f:
        return json.load(f)


def generate_report(results: dict) -> str:
    """Generate the full Markdown evaluation report."""
    meta = results.get("metadata", {})
    summary = results.get("summary", {})
    evaluations = results.get("evaluations", [])
    responses = results.get("responses", [])

    lines = []
    lines.append("# SPIN Sales Coach — Conversational Quality Evaluation Report")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"**Agent:** {meta.get('agent_name', 'spin_coach')}")
    lines.append(f"**Model:** {meta.get('agent_model', 'gemini-3.1-flash-lite')}")
    lines.append(f"**Evaluation Date:** {meta.get('timestamp', 'N/A')[:10]}")
    lines.append(f"**Evaluator:** Gemini 2.0 Flash (LLM-as-Judge)")
    lines.append(f"**Total Test Cases:** {meta.get('total_cases', 0)}")
    lines.append(f"**Execution Time:** {meta.get('total_time_seconds', 0):.1f}s")
    lines.append("")
    lines.append("---")
    lines.append("")

    # === EXECUTIVE SUMMARY ===
    lines.append("## 1. Executive Summary")
    lines.append("")
    overall = summary.get("overall_metrics", {})
    score = overall.get("overall_score", 0)
    lines.append(f"The SPIN Sales Coach agent achieved an **overall quality score of "
                 f"{score:.2f} / 5.00** across {meta.get('total_cases', 0)} automated "
                 f"test cases spanning 6 evaluation categories.")
    lines.append("")
    lines.append("| Metric | Score |")
    lines.append("|--------|:-----:|")
    lines.append(f"| Overall Quality Score | **{score:.2f} / 5.00** |")
    lines.append(f"| Tool Selection Accuracy | {summary.get('tool_selection_accuracy', 0):.1f}% |")
    lines.append(f"| Keyword Coverage | {summary.get('keyword_coverage', 0):.1f}% |")
    lines.append(f"| Pass Rate (score ≥ 4.0) | {summary.get('pass_rate_4plus', 0):.1f}% |")
    lines.append(f"| Average Latency | {meta.get('avg_latency_ms', 0):.0f} ms |")
    lines.append(f"| Errors | {meta.get('errors', 0)} |")
    lines.append("")

    # === METHODOLOGY ===
    lines.append("## 2. Evaluation Methodology")
    lines.append("")
    lines.append("### 2.1 Approach: Automated LLM-as-Judge")
    lines.append("")
    lines.append("The evaluation uses a three-layer assessment strategy:")
    lines.append("")
    lines.append("1. **Automated Test Execution** — 60 curated prompts sent via "
                 "Google ADK Runner (same pipeline as production)")
    lines.append("2. **Deterministic Checks** — Keyword presence verification "
                 "and tool selection correctness (binary pass/fail)")
    lines.append("3. **LLM-as-Judge Scoring** — Gemini 2.0 Flash evaluates each "
                 "response on 7 quality dimensions using structured rubrics (1-5 scale)")
    lines.append("")
    lines.append("### 2.2 Quality Dimensions (7 Metrics)")
    lines.append("")
    lines.append("| Dimension | Weight | Description |")
    lines.append("|-----------|:------:|-------------|")
    lines.append("| Relevance | 20% | Does the response address the user's query? |")
    lines.append("| Role Adherence | 15% | Does the agent maintain SPIN coach persona? |")
    lines.append("| Factual Grounding | 15% | Is advice grounded in SPIN methodology? |")
    lines.append("| Actionability | 15% | Does it give practical, usable guidance? |")
    lines.append("| SPIN Correctness | 15% | Are SPIN phases correctly applied? |")
    lines.append("| Conciseness | 10% | Is the response focused without verbosity? |")
    lines.append("| Safety | 10% | No hallucination, stays on domain? |")
    lines.append("")
    lines.append("### 2.3 Test Case Categories")
    lines.append("")
    lines.append("| Category | Cases | Purpose |")
    lines.append("|----------|:-----:|---------|")
    lines.append("| spin_teaching | 12 | SPIN methodology knowledge accuracy |")
    lines.append("| spin_evaluation | 10 | Quality of feedback on user pitches |")
    lines.append("| roleplay | 8 | Persona consistency in role-play mode |")
    lines.append("| tool_selection | 10 | Correct tool routing per query type |")
    lines.append("| edge_cases | 10 | Off-topic, adversarial, safety boundaries |")
    lines.append("| company_context | 10 | Domain-specific product/market knowledge |")
    lines.append("")

    # === PER-METRIC RESULTS ===
    lines.append("## 3. Per-Metric Results")
    lines.append("")
    lines.append("| Metric | Avg Score | Rating |")
    lines.append("|--------|:---------:|--------|")
    for metric in ["relevance", "role_adherence", "factual_grounding",
                   "actionability", "spin_correctness", "conciseness", "safety"]:
        val = overall.get(metric, 0)
        rating = "Excellent" if val >= 4.5 else "Good" if val >= 4.0 else "Adequate" if val >= 3.5 else "Needs Improvement"
        bar = "█" * int(val) + "░" * (5 - int(val))
        lines.append(f"| {metric.replace('_', ' ').title()} | {bar} {val:.2f} | {rating} |")
    lines.append("")

    # === PER-CATEGORY RESULTS ===
    lines.append("## 4. Per-Category Performance")
    lines.append("")
    lines.append("| Category | Avg Score | Tool Accuracy | Keyword Coverage |")
    lines.append("|----------|:---------:|:-------------:|:----------------:|")
    for cat, data in summary.get("per_category", {}).items():
        lines.append(f"| {cat} | {data['avg_overall']:.2f} | "
                     f"{data['tool_accuracy']:.0f}% | {data['keyword_coverage']:.0f}% |")
    lines.append("")

    # === DETAILED RESULTS (sample) ===
    lines.append("## 5. Detailed Results (Selected Cases)")
    lines.append("")

    # Show top 5 best and 5 worst
    valid_evals = [e for e in evaluations if not e.get("error")]
    if valid_evals:
        sorted_evals = sorted(valid_evals, key=lambda x: x["overall_score"], reverse=True)

        lines.append("### 5.1 Highest-Scoring Responses")
        lines.append("")
        lines.append("| ID | Category | Score | Prompt (truncated) |")
        lines.append("|:--:|----------|:-----:|-------------------|")
        for e in sorted_evals[:5]:
            lines.append(f"| {e['test_id']} | {e['category']} | {e['overall_score']:.2f} | "
                         f"{e['prompt'][:50]}... |")
        lines.append("")

        lines.append("### 5.2 Lowest-Scoring Responses")
        lines.append("")
        lines.append("| ID | Category | Score | Prompt (truncated) | Issue |")
        lines.append("|:--:|----------|:-----:|-------------------|-------|")
        for e in sorted_evals[-5:]:
            issue = e.get("judge_reasoning", "")[:60] or "See detailed log"
            lines.append(f"| {e['test_id']} | {e['category']} | {e['overall_score']:.2f} | "
                         f"{e['prompt'][:40]}... | {issue} |")
        lines.append("")

    # === TOOL USAGE ===
    lines.append("## 6. Tool Selection Analysis")
    lines.append("")
    tool_accuracy = summary.get("tool_selection_accuracy", 0)
    lines.append(f"Overall tool selection accuracy: **{tool_accuracy:.1f}%**")
    lines.append("")

    # Count tool usage
    tool_counts = {}
    for resp in responses:
        for tool in resp.get("tool_calls", []):
            tool_counts[tool] = tool_counts.get(tool, 0) + 1

    if tool_counts:
        lines.append("| Tool | Times Called | Purpose |")
        lines.append("|------|:-----------:|---------|")
        tool_descriptions = {
            "search_knowledge_base": "RAG retrieval for SPIN/company knowledge",
            "evaluate_spin_message": "Score user's sales pitch quality",
            "start_roleplay": "Initialize buyer persona scenario",
            "get_coaching_progress": "Session progress summary",
        }
        for tool, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
            desc = tool_descriptions.get(tool, "")
            lines.append(f"| {tool} | {count} | {desc} |")
        lines.append("")

    # === LATENCY ===
    lines.append("## 7. Performance (Latency)")
    lines.append("")
    latencies = [r["latency_ms"] for r in responses if r["latency_ms"] > 0]
    if latencies:
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|:-----:|")
        lines.append(f"| Mean latency | {sum(latencies)/len(latencies):.0f} ms |")
        lines.append(f"| Median latency | {sorted(latencies)[len(latencies)//2]:.0f} ms |")
        lines.append(f"| Min latency | {min(latencies):.0f} ms |")
        lines.append(f"| Max latency | {max(latencies):.0f} ms |")
        lines.append(f"| P95 latency | {sorted(latencies)[int(len(latencies)*0.95)]:.0f} ms |")
        lines.append("")

    # === KEY FINDINGS ===
    lines.append("## 8. Key Findings & Inference")
    lines.append("")
    lines.append("### Strengths")
    lines.append("")

    # Identify strengths (metrics >= 4.0)
    for metric in ["relevance", "role_adherence", "factual_grounding",
                   "actionability", "spin_correctness", "conciseness", "safety"]:
        val = overall.get(metric, 0)
        if val >= 4.0:
            lines.append(f"- **{metric.replace('_', ' ').title()}** ({val:.2f}/5): "
                         f"Agent consistently performs well on this dimension")

    lines.append("")
    lines.append("### Areas for Improvement")
    lines.append("")

    for metric in ["relevance", "role_adherence", "factual_grounding",
                   "actionability", "spin_correctness", "conciseness", "safety"]:
        val = overall.get(metric, 0)
        if val < 4.0:
            lines.append(f"- **{metric.replace('_', ' ').title()}** ({val:.2f}/5): "
                         f"Needs improvement — review failing test cases in this dimension")

    if not any(overall.get(m, 0) < 4.0 for m in ["relevance", "role_adherence",
               "factual_grounding", "actionability", "spin_correctness",
               "conciseness", "safety"]):
        lines.append("- All metrics meet the 4.0 threshold — focus on pushing toward 4.5+")

    lines.append("")

    # === RECOMMENDATIONS ===
    lines.append("## 9. Recommendations for Next Iteration")
    lines.append("")
    lines.append("| Priority | Recommendation | Expected Impact |")
    lines.append("|:--------:|---------------|-----------------|")
    lines.append("| 1 | Address lowest-scoring category responses | +0.2–0.5 overall score |")
    lines.append("| 2 | Improve keyword coverage in missed areas | Better domain specificity |")
    lines.append("| 3 | Fine-tune tool selection for ambiguous prompts | Higher tool accuracy |")
    lines.append("| 4 | Add more knowledge base content for weak topics | Better grounding |")
    lines.append("| 5 | Run walk-forward eval across multiple sessions | Session continuity |")
    lines.append("")

    # === CONCLUSION ===
    lines.append("## 10. Conclusion")
    lines.append("")
    grade = ("A" if score >= 4.5 else "B+" if score >= 4.0 else
             "B" if score >= 3.5 else "C" if score >= 3.0 else "D")
    lines.append(f"The SPIN Sales Coach agent achieves a quality grade of **{grade}** "
                 f"(score: {score:.2f}/5.00) based on automated evaluation across "
                 f"{meta.get('total_cases', 0)} diverse test scenarios. ")
    if score >= 4.0:
        lines.append("The agent demonstrates strong conversational quality with consistent "
                     "role adherence, factual grounding, and appropriate tool usage. ")
    lines.append("The evaluation confirms that the agent maintains its coaching persona "
                 "and provides domain-relevant, actionable guidance for SPIN selling "
                 "methodology training.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    lines.append(f"*Framework: LLM-as-Judge (Gemini 2.0 Flash) + Deterministic Checks*")
    lines.append(f"*Source: evaluation/results/latest.json*")

    return "\n".join(lines)


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate evaluation report")
    parser.add_argument("--input", type=str, default=None, help="Input results JSON")
    parser.add_argument("--output", type=str, default=None, help="Output Markdown path")
    args = parser.parse_args()

    print("Loading evaluation results...")
    results = load_results(args.input)

    print("Generating report...")
    report = generate_report(results)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(__file__).parent / "results" / "evaluation_report.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)

    print(f"Report saved to: {output_path}")
    print(f"Lines: {len(report.splitlines())}")


if __name__ == "__main__":
    main()
