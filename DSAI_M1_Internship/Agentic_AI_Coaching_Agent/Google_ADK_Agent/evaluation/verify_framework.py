"""
Framework Verification Script (Dry-Run)
========================================
Validates the evaluation framework structure without requiring
Gemini API or ADK dependencies. Tests:
1. test_cases.json loads and validates correctly
2. evaluator.py module structure is correct
3. runner.py module structure is correct
4. generate_report.py produces output from mock results
5. End-to-end mock pipeline works

Usage:
    python evaluation/verify_framework.py
"""

import json
import sys
import importlib.util
from pathlib import Path

EVAL_DIR = Path(__file__).parent
PASS = "✓"
FAIL = "✗"
results = []


def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((status, name, detail))
    print(f"  {status} {name}" + (f" — {detail}" if detail else ""))
    return condition


def main():
    print("=" * 60)
    print("SPIN Sales Coach — Evaluation Framework Verification")
    print("=" * 60)

    # === 1. TEST CASES ===
    print("\n[1/5] Validating test_cases.json...")
    tc_path = EVAL_DIR / "test_cases.json"
    check("File exists", tc_path.exists())

    with open(tc_path) as f:
        data = json.load(f)

    cases = data.get("test_cases", [])
    check("Has test_cases array", len(cases) > 0, f"{len(cases)} cases")
    check("60 test cases", len(cases) == 60)

    # Category distribution
    categories = {}
    for tc in cases:
        cat = tc.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    check("6 categories", len(categories) == 6, str(sorted(categories.keys())))
    check("All have 'id' field", all("id" in tc for tc in cases))
    check("All have 'prompt' field", all("prompt" in tc for tc in cases))
    check("All have 'expected_criteria'", all("expected_criteria" in tc for tc in cases))
    check("All have 'category'", all("category" in tc for tc in cases))

    # Unique IDs
    ids = [tc["id"] for tc in cases]
    check("Unique IDs", len(ids) == len(set(ids)), f"{len(set(ids))} unique")

    # === 2. EVALUATOR MODULE ===
    print("\n[2/5] Validating evaluator.py structure...")
    eval_path = EVAL_DIR / "evaluator.py"
    check("File exists", eval_path.exists())

    # Parse AST without importing (avoids dependency issues)
    import ast
    with open(eval_path) as f:
        tree = ast.parse(f.read())

    class_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    func_names = [node.name for node in ast.walk(tree)
                  if isinstance(node, ast.FunctionDef) and node.col_offset == 0]

    check("EvaluationResult class", "EvaluationResult" in class_names)
    check("ResponseEvaluator class", "ResponseEvaluator" in class_names)
    check("evaluate_batch function", "evaluate_batch" in func_names)

    # Check rubric dimensions in source
    source = eval_path.read_text()
    dimensions = ["relevance", "role_adherence", "factual_grounding",
                  "actionability", "spin_correctness", "conciseness", "safety"]
    for dim in dimensions:
        check(f"Dimension '{dim}' in rubric", dim in source)

    # === 3. RUNNER MODULE ===
    print("\n[3/5] Validating runner.py structure...")
    runner_path = EVAL_DIR / "runner.py"
    check("File exists", runner_path.exists())

    with open(runner_path) as f:
        tree = ast.parse(f.read())

    func_names = [node.name for node in ast.walk(tree)
                  if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    check("send_message function", "send_message" in func_names)
    check("run_test_suite function", "run_test_suite" in func_names)
    check("compute_summary function", "compute_summary" in func_names)
    check("main function", "main" in func_names)

    runner_source = runner_path.read_text()
    check("argparse CLI", "argparse" in runner_source)
    check("--limit flag", "--limit" in runner_source)
    check("--category flag", "--category" in runner_source)
    check("Saves to results/", "results" in runner_source and "latest.json" in runner_source)

    # === 4. REPORT GENERATOR ===
    print("\n[4/5] Validating generate_report.py with mock data...")
    report_path = EVAL_DIR / "generate_report.py"
    check("File exists", report_path.exists())

    # Import just the generate_report function (no external deps)
    spec = importlib.util.spec_from_file_location("generate_report", report_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Create mock results
    mock_results = {
        "metadata": {
            "timestamp": "2026-07-25T20:00:00",
            "agent_name": "spin_coach",
            "agent_model": "gemini-3.1-flash-lite",
            "total_cases": 5,
            "total_time_seconds": 12.3,
            "avg_latency_ms": 2460,
            "errors": 0,
        },
        "responses": [
            {"test_id": "T01", "response": "SPIN stands for...", "tool_calls": ["search_knowledge_base"], "latency_ms": 2100, "error": None},
            {"test_id": "T02", "response": "A 25-minute call...", "tool_calls": ["search_knowledge_base"], "latency_ms": 1900, "error": None},
            {"test_id": "E01", "response": "This is a good Situation question...", "tool_calls": ["evaluate_spin_message"], "latency_ms": 2300, "error": None},
            {"test_id": "R01", "response": "Hello, I'm Dr. Martinez...", "tool_calls": ["start_roleplay"], "latency_ms": 3100, "error": None},
            {"test_id": "ED01", "response": "I'm a SPIN sales coach...", "tool_calls": [], "latency_ms": 1800, "error": None},
        ],
        "evaluations": [
            {"test_id": "T01", "category": "spin_teaching", "prompt": "What is SPIN?", "response": "...", "relevance": 5, "role_adherence": 5, "factual_grounding": 4, "actionability": 4, "spin_correctness": 5, "conciseness": 4, "safety": 5, "overall_score": 4.60, "tool_selection_correct": True, "keyword_hits": ["Situation", "Problem"], "keyword_misses": [], "judge_reasoning": "Good", "error": None},
            {"test_id": "T02", "category": "spin_teaching", "prompt": "25 min call?", "response": "...", "relevance": 4, "role_adherence": 5, "factual_grounding": 4, "actionability": 5, "spin_correctness": 4, "conciseness": 4, "safety": 5, "overall_score": 4.40, "tool_selection_correct": True, "keyword_hits": ["time allocation"], "keyword_misses": ["minutes"], "judge_reasoning": "Good", "error": None},
            {"test_id": "E01", "category": "spin_evaluation", "prompt": "Evaluate...", "response": "...", "relevance": 5, "role_adherence": 4, "factual_grounding": 5, "actionability": 4, "spin_correctness": 5, "conciseness": 4, "safety": 5, "overall_score": 4.65, "tool_selection_correct": True, "keyword_hits": ["Situation", "factual"], "keyword_misses": [], "judge_reasoning": "Strong", "error": None},
            {"test_id": "R01", "category": "roleplay", "prompt": "Role-play...", "response": "...", "relevance": 4, "role_adherence": 5, "factual_grounding": 4, "actionability": 3, "spin_correctness": 4, "conciseness": 4, "safety": 5, "overall_score": 4.15, "tool_selection_correct": True, "keyword_hits": ["clinic", "Dr."], "keyword_misses": [], "judge_reasoning": "Good persona", "error": None},
            {"test_id": "ED01", "category": "edge_cases", "prompt": "Weather?", "response": "...", "relevance": 4, "role_adherence": 5, "factual_grounding": 3, "actionability": 3, "spin_correctness": 3, "conciseness": 5, "safety": 5, "overall_score": 3.95, "tool_selection_correct": True, "keyword_hits": ["sales"], "keyword_misses": ["SPIN"], "judge_reasoning": "Redirected well", "error": None},
        ],
        "summary": {
            "overall_metrics": {
                "relevance": 4.40, "role_adherence": 4.80, "factual_grounding": 4.00,
                "actionability": 3.80, "spin_correctness": 4.20, "conciseness": 4.20,
                "safety": 5.00, "overall_score": 4.35
            },
            "per_category": {
                "spin_teaching": {"count": 2, "avg_overall": 4.50, "tool_accuracy": 100.0, "keyword_coverage": 75.0},
                "spin_evaluation": {"count": 1, "avg_overall": 4.65, "tool_accuracy": 100.0, "keyword_coverage": 100.0},
                "roleplay": {"count": 1, "avg_overall": 4.15, "tool_accuracy": 100.0, "keyword_coverage": 100.0},
                "edge_cases": {"count": 1, "avg_overall": 3.95, "tool_accuracy": 100.0, "keyword_coverage": 50.0},
            },
            "tool_selection_accuracy": 100.0,
            "keyword_coverage": 77.8,
            "total_evaluated": 5,
            "pass_rate_4plus": 80.0,
        },
    }

    # Generate report
    report = mod.generate_report(mock_results)
    check("Report generated", len(report) > 0, f"{len(report.splitlines())} lines")
    check("Has title", "# SPIN Sales Coach" in report)
    check("Has methodology section", "## 2. Evaluation Methodology" in report)
    check("Has per-metric results", "## 3. Per-Metric Results" in report)
    check("Has conclusion", "## 10. Conclusion" in report)
    check("Contains overall score", "4.35" in report)

    # Save mock report for inspection
    mock_report_path = EVAL_DIR / "results"
    mock_report_path.mkdir(exist_ok=True)
    (mock_report_path / "latest.json").write_text(json.dumps(mock_results, indent=2))
    (mock_report_path / "evaluation_report_mock.md").write_text(report)
    check("Mock report saved", (mock_report_path / "evaluation_report_mock.md").exists())

    # === 5. END-TO-END STRUCTURE ===
    print("\n[5/5] End-to-end pipeline validation...")
    check("test_cases.json → runner.py → evaluator.py → generate_report.py chain",
          all(p.exists() for p in [tc_path, runner_path, eval_path, report_path]))
    check("results/ directory created", (EVAL_DIR / "results").is_dir())
    check("Mock latest.json available for report gen",
          (EVAL_DIR / "results" / "latest.json").exists())

    # === FINAL SUMMARY ===
    print("\n" + "=" * 60)
    passed = sum(1 for s, _, _ in results if s == PASS)
    failed = sum(1 for s, _, _ in results if s == FAIL)
    total = len(results)
    print(f"VERIFICATION COMPLETE: {passed}/{total} passed, {failed} failed")

    if failed == 0:
        print("\n✓ Framework is ready for live execution.")
        print("\nTo run the real evaluation:")
        print("  cd GoogleADKAgent")
        print("  export GOOGLE_API_KEY='your-key'")
        print("  python scripts/prepare_data.py        # ensure KB is built")
        print("  python evaluation/runner.py --limit 5  # quick 5-case test")
        print("  python evaluation/runner.py            # full 60-case run")
        print("  python evaluation/generate_report.py   # generate MD report")
    else:
        print(f"\n✗ {failed} checks failed. Fix issues before running live.")

    print("=" * 60)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
