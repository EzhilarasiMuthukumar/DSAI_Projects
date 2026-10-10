"""
prepare_data.py — Convert raw markdown training data into chunked JSON
suitable for RAG retrieval with Google ADK agents.

Splits raw_data into:
  - training_data/ (chunked documents for RAG)
  - test_data/ (sample queries + expected behavior)

Usage:
    python scripts/prepare_data.py
"""

import json
import os
import re
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "data" / "raw_data"
TRAIN_DIR = BASE_DIR / "data" / "training_data"
TEST_DIR = BASE_DIR / "data" / "test_data"


def chunk_markdown(content: str, source_file: str, max_chunk_size: int = 1500) -> list[dict]:
    """Split markdown content into chunks by H2/H3 sections.
    
    Each chunk gets metadata for retrieval context.
    """
    chunks = []
    
    # Split by H2 (##) headers
    sections = re.split(r'\n(?=## )', content)
    
    for section in sections:
        if not section.strip():
            continue
        
        # Extract section title
        title_match = re.match(r'^#{1,3}\s+(.+)', section.strip())
        title = title_match.group(1) if title_match else "General"
        
        # If section is small enough, keep as one chunk
        if len(section) <= max_chunk_size:
            chunks.append({
                "id": f"{source_file}::{title}",
                "source": source_file,
                "section": title,
                "content": section.strip(),
                "metadata": {
                    "file": source_file,
                    "section": title,
                    "char_count": len(section.strip()),
                }
            })
        else:
            # Split large sections by H3 (###) or paragraphs
            subsections = re.split(r'\n(?=### )', section)
            for i, subsec in enumerate(subsections):
                if not subsec.strip():
                    continue
                sub_title_match = re.match(r'^#{1,3}\s+(.+)', subsec.strip())
                sub_title = sub_title_match.group(1) if sub_title_match else f"{title} (part {i+1})"
                
                # Further split if still too large
                if len(subsec) > max_chunk_size:
                    paragraphs = subsec.split('\n\n')
                    current_chunk = ""
                    part_num = 1
                    for para in paragraphs:
                        if len(current_chunk) + len(para) > max_chunk_size and current_chunk:
                            chunks.append({
                                "id": f"{source_file}::{sub_title}::part{part_num}",
                                "source": source_file,
                                "section": f"{sub_title} (part {part_num})",
                                "content": current_chunk.strip(),
                                "metadata": {
                                    "file": source_file,
                                    "section": sub_title,
                                    "part": part_num,
                                    "char_count": len(current_chunk.strip()),
                                }
                            })
                            current_chunk = para + "\n\n"
                            part_num += 1
                        else:
                            current_chunk += para + "\n\n"
                    if current_chunk.strip():
                        chunks.append({
                            "id": f"{source_file}::{sub_title}::part{part_num}",
                            "source": source_file,
                            "section": f"{sub_title} (part {part_num})",
                            "content": current_chunk.strip(),
                            "metadata": {
                                "file": source_file,
                                "section": sub_title,
                                "part": part_num,
                                "char_count": len(current_chunk.strip()),
                            }
                        })
                else:
                    chunks.append({
                        "id": f"{source_file}::{sub_title}",
                        "source": source_file,
                        "section": sub_title,
                        "content": subsec.strip(),
                        "metadata": {
                            "file": source_file,
                            "section": sub_title,
                            "char_count": len(subsec.strip()),
                        }
                    })
    
    return chunks


def generate_test_data() -> list[dict]:
    """Generate test queries and expected behaviors for evaluation."""
    return [
        {
            "id": "test_01",
            "query": "How should I start a sales conversation with a new veterinary clinic?",
            "expected_behavior": "Should recommend starting with Situation questions, mention pre-call research, suggest 2-3 factual questions about clinic size and current products.",
            "expected_topics": ["situation questions", "pre-call research", "clinic size"],
            "spin_phase": "situation",
        },
        {
            "id": "test_02",
            "query": "The vet says they're happy with their current flea treatment. What should I do?",
            "expected_behavior": "Should NOT challenge directly. Should suggest Problem questions to uncover hidden dissatisfaction like compliance gaps or administration issues.",
            "expected_topics": ["problem questions", "compliance", "don't challenge directly"],
            "spin_phase": "problem",
        },
        {
            "id": "test_03",
            "query": "How do I make the vet see the urgency of switching products?",
            "expected_behavior": "Should recommend Implication questions that quantify the cost of the current problem. Connect to revenue impact, client retention, staff frustration.",
            "expected_topics": ["implication questions", "cost quantification", "urgency"],
            "spin_phase": "implication",
        },
        {
            "id": "test_04",
            "query": "The clinic says they don't have budget for new products this quarter.",
            "expected_behavior": "Should suggest quantifying cost of inaction, offering a low-commitment trial, identifying budget cycle timing, and framing ROI.",
            "expected_topics": ["budget objection", "trial offer", "ROI", "cost of inaction"],
            "spin_phase": "need-payoff",
        },
        {
            "id": "test_05",
            "query": "I only have 10 minutes with this vet. How do I run SPIN effectively?",
            "expected_behavior": "Should provide compressed SPIN format: 1 situation question, lead with hypothesis for problem, one powerful implication, quick need-payoff, and offer low-friction next step.",
            "expected_topics": ["time-focused", "compressed SPIN", "10 minutes"],
            "spin_phase": "all",
        },
        {
            "id": "test_06",
            "query": "Can you role-play as a veterinarian? I want to practice my SPIN questions.",
            "expected_behavior": "Should enter role-play mode as a vet, present realistic responses, allow the rep to practice, then provide feedback on SPIN technique.",
            "expected_topics": ["role-play", "practice", "feedback"],
            "spin_phase": "all",
        },
        {
            "id": "test_07",
            "query": "What ROI numbers should I bring to a multi-vet hospital?",
            "expected_behavior": "Should mention: compliance gap revenue calculation, inventory waste from multiple brands, staff time savings from consolidation, and margin improvement.",
            "expected_topics": ["ROI", "multi-vet", "consolidation", "budget-focused"],
            "spin_phase": "need-payoff",
        },
        {
            "id": "test_08",
            "query": "What are common mistakes SPIN sellers make?",
            "expected_behavior": "Should list anti-patterns: feature dumping, premature closing, too many situation questions, not getting commitment, ignoring budget signals.",
            "expected_topics": ["anti-patterns", "feature dumping", "premature close"],
            "spin_phase": "all",
        },
    ]


def main():
    # Create output directories
    TRAIN_DIR.mkdir(parents=True, exist_ok=True)
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process raw markdown files
    all_chunks = []
    
    for md_file in sorted(RAW_DIR.glob("*.md")):
        print(f"Processing: {md_file.name}")
        content = md_file.read_text()
        chunks = chunk_markdown(content, md_file.name)
        all_chunks.extend(chunks)
        print(f"  → {len(chunks)} chunks extracted")
    
    # Write training data
    training_file = TRAIN_DIR / "knowledge_base.json"
    with open(training_file, "w") as f:
        json.dump(all_chunks, f, indent=2)
    print(f"\nTraining data: {len(all_chunks)} chunks → {training_file}")
    
    # Write individual chunk files (alternative format for simpler loading)
    chunks_dir = TRAIN_DIR / "chunks"
    chunks_dir.mkdir(exist_ok=True)
    for i, chunk in enumerate(all_chunks):
        chunk_file = chunks_dir / f"chunk_{i:03d}.json"
        with open(chunk_file, "w") as f:
            json.dump(chunk, f, indent=2)
    print(f"Individual chunks: {len(all_chunks)} files → {chunks_dir}/")
    
    # Write a flat text version (for simple RAG loading)
    flat_file = TRAIN_DIR / "knowledge_base_flat.txt"
    with open(flat_file, "w") as f:
        for chunk in all_chunks:
            f.write(f"--- {chunk['section']} ({chunk['source']}) ---\n")
            f.write(chunk["content"])
            f.write("\n\n")
    print(f"Flat text version → {flat_file}")
    
    # Generate and write test data
    test_data = generate_test_data()
    test_file = TEST_DIR / "evaluation_queries.json"
    with open(test_file, "w") as f:
        json.dump(test_data, f, indent=2)
    print(f"\nTest data: {len(test_data)} queries → {test_file}")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"DATA PREPARATION COMPLETE")
    print(f"{'='*50}")
    print(f"  Raw files processed: {len(list(RAW_DIR.glob('*.md')))}")
    print(f"  Training chunks: {len(all_chunks)}")
    print(f"  Test queries: {len(test_data)}")
    print(f"  Output: {TRAIN_DIR}/")
    print(f"  Output: {TEST_DIR}/")


if __name__ == "__main__":
    main()
