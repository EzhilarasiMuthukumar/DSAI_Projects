"""
Tools for the SPIN Sales Coach agent.
Provides RAG-based knowledge retrieval and coaching utilities.
"""

import json
from pathlib import Path
from google.adk.tools import ToolContext

# Load knowledge base at module level
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "training_data"
KNOWLEDGE_BASE = []

_kb_file = DATA_DIR / "knowledge_base.json"
if _kb_file.exists():
    with open(_kb_file) as f:
        KNOWLEDGE_BASE = json.load(f)


def search_knowledge_base(query: str, max_results: int = 5) -> dict:
    """Search the SPIN selling and company knowledge base for relevant training content.

    Use this tool when the sales representative asks about:
    - SPIN methodology (situation, problem, implication, need-payoff questions)
    - Company products, positioning, or competitive landscape
    - Sales scenarios, objection handling, or role-play preparation
    - Time-focused or budget-focused selling techniques
    - Call structure, time allocation, or efficiency tips

    Args:
        query: The topic or question to search for in the knowledge base.
        max_results: Maximum number of relevant chunks to return (1-10).

    Returns:
        Relevant training content sections with source references.
    """
    if not KNOWLEDGE_BASE:
        return {
            "status": "error",
            "error": "Knowledge base not loaded. Run 'python scripts/prepare_data.py' first.",
        }

    max_results = min(max(max_results, 1), 10)
    query_lower = query.lower()
    query_words = set(query_lower.split())

    # Simple keyword-based relevance scoring
    scored = []
    for chunk in KNOWLEDGE_BASE:
        content_lower = chunk["content"].lower()
        section_lower = chunk["section"].lower()

        # Score based on word overlap
        score = 0
        for word in query_words:
            if len(word) < 3:
                continue
            if word in content_lower:
                score += content_lower.count(word)
            if word in section_lower:
                score += 5  # Section title matches are worth more

        # Boost for exact phrase matches
        if query_lower in content_lower:
            score += 20

        # Boost for SPIN phase keywords
        spin_keywords = {
            "situation": ["situation", "current state", "fact"],
            "problem": ["problem", "challenge", "difficulty", "pain"],
            "implication": ["implication", "impact", "consequence", "cost"],
            "need-payoff": ["need-payoff", "need payoff", "value", "benefit", "roi"],
        }
        for phase, keywords in spin_keywords.items():
            if any(kw in query_lower for kw in keywords):
                if any(kw in content_lower for kw in keywords):
                    score += 10

        if score > 0:
            scored.append((score, chunk))

    # Sort by relevance and return top results
    scored.sort(key=lambda x: x[0], reverse=True)
    results = scored[:max_results]

    if not results:
        return {
            "status": "no_results",
            "message": f"No relevant content found for: '{query}'. Try different keywords.",
            "suggestion": "Try searching for: SPIN, situation, problem, implication, need-payoff, company, objection, budget, time, compliance",
        }

    return {
        "status": "success",
        "query": query,
        "result_count": len(results),
        "results": [
            {
                "section": chunk["section"],
                "source": chunk["source"],
                "content": chunk["content"][:1500],  # Limit size
                "relevance_score": score,
            }
            for score, chunk in results
        ],
    }


def evaluate_spin_message(
    rep_message: str, spin_phase: str, tool_context: ToolContext
) -> dict:
    """Evaluate a sales representative's message for SPIN technique quality.

    Use this tool when the rep shares a sales pitch, question, or conversation
    snippet and wants feedback on their SPIN technique.

    Args:
        rep_message: The sales rep's message or question to evaluate.
        spin_phase: Which SPIN phase this belongs to - "situation", "problem",
                    "implication", "need_payoff", or "unknown".

    Returns:
        Evaluation with scores and improvement suggestions.
    """
    evaluation = {
        "message_analyzed": rep_message[:200],
        "declared_phase": spin_phase,
        "checks": [],
    }

    msg_lower = rep_message.lower()

    # Check if it's actually a question (SPIN is about asking, not telling)
    is_question = "?" in rep_message
    evaluation["checks"].append({
        "criterion": "Is it a question?",
        "passed": is_question,
        "note": "Good — SPIN uses questions to guide" if is_question
                else "SPIN is about asking, not telling. Rephrase as a question.",
    })

    # Check for open-ended vs closed
    open_starters = ["how", "what", "why", "tell me", "describe", "explain"]
    is_open = any(msg_lower.strip().startswith(s) for s in open_starters)
    evaluation["checks"].append({
        "criterion": "Open-ended question?",
        "passed": is_open,
        "note": "Good — open questions encourage elaboration" if is_open
                else "Consider making it open-ended (How/What/Why) for richer responses.",
    })

    # Phase-specific checks
    if spin_phase == "situation":
        is_factual = any(w in msg_lower for w in ["how many", "currently", "what is your", "do you"])
        evaluation["checks"].append({
            "criterion": "Factual/contextual (appropriate for Situation)?",
            "passed": is_factual,
            "note": "Good — gathering facts about current state" if is_factual
                    else "Situation questions should gather facts, not probe problems yet.",
        })
    elif spin_phase == "problem":
        is_problem = any(w in msg_lower for w in ["challenge", "problem", "difficulty", "frustrat", "concern", "issue", "struggle"])
        evaluation["checks"].append({
            "criterion": "Probes a pain point (appropriate for Problem)?",
            "passed": is_problem,
            "note": "Good — uncovering pain points" if is_problem
                    else "Problem questions should surface difficulties or dissatisfactions.",
        })
    elif spin_phase == "implication":
        is_impact = any(w in msg_lower for w in ["impact", "affect", "cost", "consequence", "happen", "mean for", "result"])
        evaluation["checks"].append({
            "criterion": "Explores consequences (appropriate for Implication)?",
            "passed": is_impact,
            "note": "Good — amplifying the impact of the problem" if is_impact
                    else "Implication questions should make the customer feel the WEIGHT of the problem.",
        })
    elif spin_phase == "need_payoff":
        is_value = any(w in msg_lower for w in ["if you could", "what would", "how would", "value", "benefit", "save", "improve"])
        evaluation["checks"].append({
            "criterion": "Gets customer to state value (appropriate for Need-Payoff)?",
            "passed": is_value,
            "note": "Good — letting the customer articulate the value" if is_value
                    else "Need-Payoff questions should get the CUSTOMER to state why a solution matters.",
        })

    # Time-focus check
    is_concise = len(rep_message.split()) < 40
    evaluation["checks"].append({
        "criterion": "Concise (time-focused)?",
        "passed": is_concise,
        "note": "Good — brief and focused" if is_concise
                else "Consider shortening. Time-focused reps keep questions under 30 words.",
    })

    # Score
    passed = sum(1 for c in evaluation["checks"] if c["passed"])
    total = len(evaluation["checks"])
    evaluation["score"] = f"{passed}/{total}"
    evaluation["rating"] = "Excellent" if passed == total else "Good" if passed >= total - 1 else "Needs Improvement"

    # Track in session
    history = tool_context.state.get("evaluation_history", [])
    history.append({"phase": spin_phase, "score": f"{passed}/{total}", "rating": evaluation["rating"]})
    tool_context.state["evaluation_history"] = history

    return evaluation


def get_coaching_progress(tool_context: ToolContext) -> dict:
    """Get the sales rep's coaching session progress and performance summary.

    Use this when the rep asks about their progress, scores, or wants a summary
    of their training session.

    Returns:
        Session statistics and performance trends.
    """
    history = tool_context.state.get("evaluation_history", [])
    roleplay_count = tool_context.state.get("roleplay_count", 0)

    if not history and roleplay_count == 0:
        return {
            "status": "no_data",
            "message": "No evaluations or role-plays completed yet. Start practicing!",
            "suggestions": [
                "Try: 'Evaluate my question: How many patients does your clinic see monthly?'",
                "Try: 'Let's role-play — you be a veterinarian and I'll practice SPIN'",
                "Try: 'What are good Problem questions for a small clinic?'",
            ],
        }

    # Analyze history
    phase_scores = {}
    for entry in history:
        phase = entry["phase"]
        if phase not in phase_scores:
            phase_scores[phase] = []
        # Parse score
        parts = entry["score"].split("/")
        if len(parts) == 2:
            phase_scores[phase].append(int(parts[0]) / int(parts[1]))

    summary = {
        "total_evaluations": len(history),
        "roleplay_sessions": roleplay_count,
        "phase_performance": {},
    }

    for phase, scores in phase_scores.items():
        avg = sum(scores) / len(scores) if scores else 0
        summary["phase_performance"][phase] = {
            "attempts": len(scores),
            "average_score": f"{avg:.0%}",
            "trend": "improving" if len(scores) > 1 and scores[-1] > scores[0] else "stable",
        }

    # Identify weakest area
    if phase_scores:
        weakest = min(phase_scores.items(), key=lambda x: sum(x[1]) / len(x[1]))
        summary["focus_area"] = f"Practice more {weakest[0]} questions — this is your growth area."

    return summary


def start_roleplay(
    clinic_type: str, difficulty: str, tool_context: ToolContext
) -> dict:
    """Initialize a role-play scenario where the agent plays a veterinarian.

    The sales rep will practice their SPIN selling technique against
    a simulated buyer persona.

    Args:
        clinic_type: Type of clinic to simulate - "small_solo", "multi_vet",
                     "hospital_group", or "cat_specialist".
        difficulty: How challenging the buyer should be - "easy", "medium", or "hard".

    Returns:
        Scenario setup and the buyer persona's opening context.
    """
    scenarios = {
        "small_solo": {
            "name": "Dr. Sarah Martinez",
            "clinic": "PawCare Veterinary Clinic",
            "size": "Single vet, 800 patients/month",
            "current_brand": "Competitor topical flea/tick product",
            "compliance": "25%",
            "personality": "Friendly but time-pressed, budget-conscious",
            "hidden_pain": "High summer flea infestation cases, staff frustrated with client conversations",
        },
        "multi_vet": {
            "name": "Sarah Thompson (Practice Manager)",
            "clinic": "Regional Animal Hospital",
            "size": "5 vets, 3,000 patients/month",
            "current_brand": "Split across 3 brands",
            "compliance": "35%",
            "personality": "Data-driven, focused on efficiency and margins",
            "hidden_pain": "$4,500 in annual expired product waste, staff confusion with multiple protocols",
        },
        "hospital_group": {
            "name": "Dr. James Wilson (Clinical Director)",
            "clinic": "Metro Veterinary Partners (4 locations)",
            "size": "12 vets, 8,000 patients/month across locations",
            "current_brand": "Single competitor brand via national contract",
            "compliance": "40%",
            "personality": "Analytical, needs strong data, loyal to current supplier",
            "hidden_pain": "Contract renewal coming up, dissatisfied with rep support quality",
        },
        "cat_specialist": {
            "name": "Dr. Lisa Chen",
            "clinic": "Feline Focus Veterinary",
            "size": "2 vets, 500 cat patients/month",
            "current_brand": "Topical products only",
            "compliance": "20%",
            "personality": "Expert in feline medicine, skeptical of new products",
            "hidden_pain": "Cat owners hate topicals, compliance is worst in the industry for cats",
        },
    }

    if clinic_type not in scenarios:
        clinic_type = "small_solo"

    scenario = scenarios[clinic_type]

    # Adjust for difficulty
    difficulty_notes = {
        "easy": "Buyer is receptive, openly shares problems, minimal objections.",
        "medium": "Buyer is neutral, needs good questions to open up, some pushback.",
        "hard": "Buyer is skeptical, gives short answers, raises budget and loyalty objections.",
    }

    # Track in session
    tool_context.state["active_roleplay"] = {
        "scenario": scenario,
        "difficulty": difficulty,
        "started": True,
    }
    count = tool_context.state.get("roleplay_count", 0)
    tool_context.state["roleplay_count"] = count + 1

    return {
        "status": "roleplay_started",
        "scenario": {
            "buyer_name": scenario["name"],
            "clinic": scenario["clinic"],
            "clinic_size": scenario["size"],
            "difficulty": difficulty,
            "difficulty_description": difficulty_notes.get(difficulty, difficulty_notes["medium"]),
        },
        "instructions_for_agent": (
            f"You are now role-playing as {scenario['name']} from {scenario['clinic']}. "
            f"Your personality: {scenario['personality']}. "
            f"Your hidden pain: {scenario['hidden_pain']}. "
            f"Current product: {scenario['current_brand']}. Compliance: {scenario['compliance']}. "
            f"Difficulty: {difficulty}. "
            f"Respond naturally as this buyer would. Don't reveal hidden pain until the rep "
            f"asks good Problem/Implication questions. After the role-play, provide SPIN feedback."
        ),
        "opening_for_rep": (
            f"You're about to call {scenario['name']} at {scenario['clinic']} "
            f"({scenario['size']}). You know they use {scenario['current_brand']}. "
            f"Start your SPIN conversation — what's your opening?"
        ),
    }
