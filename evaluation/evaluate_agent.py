import argparse
import json
from datetime import datetime
from pathlib import Path

from agent import ResearchScoutAgent
from filtering import citation_matches, relevance_score, year_matches

TEST_PROMPTS = [
    "Find a research paper about LLM agents for software engineering that was published after 2022 and has at least 100 citations. Explain why the paper is relevant and provide the source of the citation count.",
    "Find a paper about retrieval-augmented generation published before 2021 with more than 500 citations. Summarize its contribution in 5-7 sentences.",
    "Find a recent paper about AI agents using tools and explain whether it would be useful for someone building autonomous software agents.",
    "Find a paper about chain-of-thought prompting published in 2022 with at least 1000 citations.",
    "Find a paper about code generation with large language models after 2020 with at least 200 citations.",
    "Find a paper about software defect prediction before 2015 with more than 1000 citations.",
    "Find a paper about diffusion models published in 2020 with at least 500 citations.",
    "Find a paper about quantum potato debugging after 2024 with at least 9999 citations.",
    "Find me a good paper about agents.",
    "Find a paper about transformers in natural language processing published in 2017 with at least 10000 citations.",
]


def evaluate_result(result) -> dict:
    paper = result.selected_paper

    found_relevant_paper = False
    respected_year = False
    respected_citations = False
    valid_source = False
    avoided_hallucination = True
    useful_explanation = len(result.answer) > 300 and "Uncertainty" in result.answer

    if paper:
        found_relevant_paper = relevance_score(paper, result.constraints) > 0
        respected_year = year_matches(paper, result.constraints)
        respected_citations = citation_matches(paper, result.constraints)
        valid_source = bool(paper.source and paper.url)
        avoided_hallucination = (
            str(paper.citation_count) in result.answer
            and paper.title in result.answer
            and paper.source in result.answer
        )
    else:
        # If no paper is found, the agent is still correct when it clearly refuses to invent a result.
        found_relevant_paper = False
        respected_year = True
        respected_citations = True
        valid_source = True
        avoided_hallucination = "No matching paper was found" in result.answer or "not invent" in result.answer

    passed = all(
        [
            respected_year,
            respected_citations,
            valid_source,
            avoided_hallucination,
            useful_explanation,
        ]
    )

    return {
        "prompt": result.request,
        "found_paper": paper is not None,
        "paper_title": paper.title if paper else None,
        "paper_year": paper.year if paper else None,
        "paper_citations": paper.citation_count if paper else None,
        "tool_called": result.tool_called,
        "candidates_seen": result.candidates_seen,
        "candidates_after_filtering": result.candidates_after_filtering,
        "found_relevant_paper": found_relevant_paper,
        "respected_year_constraint": respected_year,
        "respected_citation_constraint": respected_citations,
        "provided_valid_source": valid_source,
        "avoided_hallucination": avoided_hallucination,
        "useful_explanation": useful_explanation,
        "passed_core_checks": passed,
    }


def write_markdown_report(rows: list[dict], output_file: Path) -> None:
    passed = sum(1 for row in rows if row["passed_core_checks"])

    lines = [
        "# Evaluation Results",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"Passed core checks: {passed}/{len(rows)}",
        "",
        "## Method",
        "",
        "The evaluation follows a systematic checklist inspired by agent evaluation principles: task success, constraint satisfaction, source validity, hallucination control, and usefulness of the explanation. For each prompt, the agent must retrieve data through the Semantic Scholar tool, filter papers using deterministic year/citation checks, and produce an answer that includes verifiable metadata.",
        "",
        "## Results Table",
        "",
        "| # | Prompt | Found | Year OK | Citations OK | Source OK | No hallucination | Useful explanation | Passed | Selected paper |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]

    for index, row in enumerate(rows, start=1):
        selected = (row["paper_title"] or "No paper selected").replace("|", "-")
        prompt = row["prompt"].replace("|", "-")[:90] + "..."
        lines.append(
            f"| {index} | {prompt} | {row['found_paper']} | {row['respected_year_constraint']} | "
            f"{row['respected_citation_constraint']} | {row['provided_valid_source']} | "
            f"{row['avoided_hallucination']} | {row['useful_explanation']} | "
            f"{row['passed_core_checks']} | {selected} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- A failure to find a paper is not automatically a hallucination failure. It is acceptable when the agent clearly rejects the request and does not invent metadata.",
            "- Citation counts are time-sensitive and may change because they are retrieved live from Semantic Scholar.",
            "- Ambiguous prompts are expected to be weaker because the agent must infer a broad topic.",
        ]
    )

    output_file.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the Research Scout Agent on 10 prompts")
    parser.add_argument("--use-llm", action="store_true", help="Use AutoGen LLM synthesis during evaluation")
    parser.add_argument("--limit", type=int, default=30, help="Candidate papers per prompt")
    args = parser.parse_args()

    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    agent = ResearchScoutAgent(use_llm=args.use_llm, search_limit=args.limit)

    rows = []
    for prompt in TEST_PROMPTS:
        print(f"Evaluating: {prompt}")
        result = agent.solve(prompt)
        rows.append(evaluate_result(result))

    json_file = results_dir / "evaluation_results.json"
    markdown_file = results_dir / "evaluation_results.md"

    json_file.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    write_markdown_report(rows, markdown_file)

    print(f"Wrote {json_file}")
    print(f"Wrote {markdown_file}")


if __name__ == "__main__":
    main()