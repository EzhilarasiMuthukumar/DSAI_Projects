"""
Automated Test Runner for SPIN Sales Coach Agent
=================================================
Sends all test cases through the ADK Runner, collects responses and tool calls,
then evaluates each using the LLM-as-Judge evaluator.

Usage:
    cd GoogleADKAgent
    python evaluation/runner.py                    # Full run (60 cases)
    python evaluation/runner.py --limit 5          # Quick validation (5 cases)
    python evaluation/runner.py --category edge_cases  # Single category
    python evaluation/runner.py --output results/my_run.json

Prerequisites:
    - GOOGLE_API_KEY set in environment
    - Knowledge base prepared: python scripts/prepare_data.py
"""

import asyncio
import json
import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "agent"))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from evaluator import ResponseEvaluator, EvaluationResult


# =============================================================================
# AGENT INTERACTION
# =============================================================================

async def send_message(runner, session_service, session_id, user_id, message_text):
    """Send a message to the agent and collect the full response + tool calls.

    Returns:
        dict with 'response' (str) and 'tool_calls' (list of str)
    """
    message = types.Content(
        role="user",
        parts=[types.Part(text=message_text)],
    )

    response_text = ""
    tool_calls = []

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text
                if part.function_call:
                    tool_calls.append(part.function_call.name)

    return {
        "response": response_text,
        "tool_calls": tool_calls,
    }


# =============================================================================
# TEST EXECUTION
# =============================================================================

async def run_test_suite(
    test_cases: list,
    evaluate: bool = True,
    verbose: bool = True,
) -> dict:
    """Execute all test cases against the agent and optionally evaluate.

    Args:
        test_cases: List of test case dicts from test_cases.json
        evaluate: Whether to run LLM-as-Judge scoring
        verbose: Print progress to stdout

    Returns:
        dict with 'metadata', 'responses', and optionally 'evaluations'
    """
    from spin_coach import root_agent

    # Setup ADK runner
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="evaluation",
        session_service=session_service,
    )

    # Create a session
    session = await session_service.create_session(
        app_name="evaluation", user_id="eval_user"
    )

    if verbose:
        print(f"Agent: {root_agent.name} ({root_agent.model})")
        print(f"Tests: {len(test_cases)}")
        print(f"Session: {session.id}")
        print("=" * 60)

    # Run all test cases
    responses = []
    total_start = time.time()

    for i, tc in enumerate(test_cases):
        test_id = tc["id"]
        prompt = tc["prompt"]

        if verbose:
            print(f"  [{i+1}/{len(test_cases)}] {test_id}: {prompt[:50]}...", end="")

        # Handle empty prompt edge case
        if not prompt.strip():
            responses.append({
                "test_id": test_id,
                "response": "(empty prompt — skipped)",
                "tool_calls": [],
                "latency_ms": 0,
                "error": None,
            })
            if verbose:
                print(" [SKIP: empty]")
            continue

        # Send to agent
        start = time.time()
        try:
            result = await send_message(
                runner, session_service, session.id, "eval_user", prompt
            )
            latency = (time.time() - start) * 1000

            responses.append({
                "test_id": test_id,
                "response": result["response"],
                "tool_calls": result["tool_calls"],
                "latency_ms": round(latency, 1),
                "error": None,
            })

            if verbose:
                tools_str = f" [{','.join(result['tool_calls'])}]" if result["tool_calls"] else ""
                print(f" ✓ {latency:.0f}ms{tools_str}")

        except Exception as e:
            latency = (time.time() - start) * 1000
            responses.append({
                "test_id": test_id,
                "response": "",
                "tool_calls": [],
                "latency_ms": round(latency, 1),
                "error": str(e),
            })
            if verbose:
                print(f" ✗ ERROR: {str(e)[:60]}")

    total_time = time.time() - total_start

    if verbose:
        print("=" * 60)
        print(f"Execution complete: {len(responses)} responses in {total_time:.1f}s")
        errors = sum(1 for r in responses if r["error"])
        if errors:
            print(f"  Errors: {errors}")

    # Build result
    run_result = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "agent_name": root_agent.name,
            "agent_model": root_agent.model,
            "total_cases": len(test_cases),
            "total_time_seconds": round(total_time, 2),
            "avg_latency_ms": round(
                sum(r["latency_ms"] for r in responses) / max(len(responses), 1), 1
            ),
            "errors": sum(1 for r in responses if r["error"]),
        },
        "responses": responses,
    }

    # Evaluate if requested
    if evaluate:
        if verbose:
            print("\nRunning LLM-as-Judge evaluation...")

        evaluator = ResponseEvaluator()
        evaluations = []

        for tc, resp in zip(test_cases, responses):
            if resp["error"]:
                # Create a failed evaluation
                eval_result = EvaluationResult(
                    test_id=tc["id"],
                    category=tc["category"],
                    prompt=tc["prompt"],
                    response="",
                    error=resp["error"],
                )
                eval_result.compute_overall()
                evaluations.append(eval_result.to_dict())
                continue

            eval_result = evaluator.evaluate(
                test_case=tc,
                agent_response=resp["response"],
                tool_calls=resp["tool_calls"],
            )
            evaluations.append(eval_result.to_dict())

            if verbose:
                print(f"  {tc['id']}: {eval_result.overall_score:.2f}/5.00"
                      f" | Tools={'✓' if eval_result.tool_selection_correct else '✗'}"
                      f" | Keywords={len(eval_result.keyword_hits)}/{len(eval_result.keyword_hits)+len(eval_result.keyword_misses)}")

        run_result["evaluations"] = evaluations

        # Compute summary stats
        valid_evals = [e for e in evaluations if not e.get("error")]
        if valid_evals:
            run_result["summary"] = compute_summary(valid_evals, test_cases)

        if verbose:
            print_summary(run_result.get("summary", {}))

    return run_result


# =============================================================================
# SUMMARY COMPUTATION
# =============================================================================

def compute_summary(evaluations: list, test_cases: list) -> dict:
    """Compute aggregate statistics from evaluation results."""
    metrics = [
        "relevance", "role_adherence", "factual_grounding",
        "actionability", "spin_correctness", "conciseness", "safety"
    ]

    # Overall averages
    overall = {}
    for m in metrics:
        values = [e[m] for e in evaluations if e.get(m)]
        overall[m] = round(sum(values) / max(len(values), 1), 2)

    overall["overall_score"] = round(
        sum(e["overall_score"] for e in evaluations) / max(len(evaluations), 1), 2
    )

    # Per-category averages
    categories = set(e["category"] for e in evaluations)
    per_category = {}
    for cat in sorted(categories):
        cat_evals = [e for e in evaluations if e["category"] == cat]
        per_category[cat] = {
            "count": len(cat_evals),
            "avg_overall": round(
                sum(e["overall_score"] for e in cat_evals) / max(len(cat_evals), 1), 2
            ),
            "tool_accuracy": round(
                sum(1 for e in cat_evals if e.get("tool_selection_correct", False))
                / max(len(cat_evals), 1) * 100, 1
            ),
            "keyword_coverage": round(
                sum(len(e.get("keyword_hits", [])) for e in cat_evals)
                / max(sum(len(e.get("keyword_hits", [])) + len(e.get("keyword_misses", []))
                          for e in cat_evals), 1) * 100, 1
            ),
        }

    # Tool selection accuracy
    tool_correct = sum(1 for e in evaluations if e.get("tool_selection_correct", False))
    tool_total = len(evaluations)

    # Keyword coverage
    total_hits = sum(len(e.get("keyword_hits", [])) for e in evaluations)
    total_expected = sum(
        len(e.get("keyword_hits", [])) + len(e.get("keyword_misses", []))
        for e in evaluations
    )

    return {
        "overall_metrics": overall,
        "per_category": per_category,
        "tool_selection_accuracy": round(tool_correct / max(tool_total, 1) * 100, 1),
        "keyword_coverage": round(total_hits / max(total_expected, 1) * 100, 1),
        "total_evaluated": len(evaluations),
        "pass_rate_4plus": round(
            sum(1 for e in evaluations if e["overall_score"] >= 4.0)
            / max(len(evaluations), 1) * 100, 1
        ),
    }


def print_summary(summary: dict):
    """Print a formatted summary to stdout."""
    if not summary:
        print("  No summary available.")
        return

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    overall = summary.get("overall_metrics", {})
    print(f"\n  Overall Score: {overall.get('overall_score', 0):.2f} / 5.00")
    print(f"  Tool Accuracy: {summary.get('tool_selection_accuracy', 0):.1f}%")
    print(f"  Keyword Coverage: {summary.get('keyword_coverage', 0):.1f}%")
    print(f"  Pass Rate (≥4.0): {summary.get('pass_rate_4plus', 0):.1f}%")

    print(f"\n  Per-Metric Averages:")
    for m, v in overall.items():
        if m != "overall_score":
            bar = "█" * int(v) + "░" * (5 - int(v))
            print(f"    {m:<20} {bar} {v:.2f}")

    print(f"\n  Per-Category:")
    for cat, data in summary.get("per_category", {}).items():
        print(f"    {cat:<18} avg={data['avg_overall']:.2f} "
              f"tools={data['tool_accuracy']:.0f}% "
              f"keywords={data['keyword_coverage']:.0f}%")

    print("=" * 60)


# =============================================================================
# CLI ENTRYPOINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Run automated evaluation of the SPIN Sales Coach agent"
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Limit number of test cases (for quick validation)"
    )
    parser.add_argument(
        "--category", type=str, default=None,
        help="Run only a specific category (e.g., edge_cases)"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output JSON path (default: evaluation/results/run_TIMESTAMP.json)"
    )
    parser.add_argument(
        "--no-eval", action="store_true",
        help="Skip LLM-as-Judge evaluation (just collect responses)"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress verbose output"
    )
    args = parser.parse_args()

    # Load test cases
    tc_path = Path(__file__).parent / "test_cases.json"
    with open(tc_path) as f:
        data = json.load(f)
    test_cases = data["test_cases"]

    # Filter
    if args.category:
        test_cases = [tc for tc in test_cases if tc["category"] == args.category]
        if not test_cases:
            print(f"ERROR: No test cases found for category '{args.category}'")
            sys.exit(1)

    if args.limit:
        test_cases = test_cases[:args.limit]

    # Check API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY environment variable not set.")
        print("  export GOOGLE_API_KEY='your-key-here'")
        sys.exit(1)

    # Run
    print(f"\n{'='*60}")
    print(f"SPIN Sales Coach — Automated Evaluation")
    print(f"{'='*60}")
    print(f"Test cases: {len(test_cases)}")
    if args.category:
        print(f"Category filter: {args.category}")
    print()

    results = asyncio.run(
        run_test_suite(
            test_cases=test_cases,
            evaluate=not args.no_eval,
            verbose=not args.quiet,
        )
    )

    # Save results
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = results_dir / f"run_{timestamp}.json"

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_path}")

    # Also save as 'latest' for report generation
    latest_path = results_dir / "latest.json"
    with open(latest_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Latest symlink: {latest_path}")


if __name__ == "__main__":
    main()
