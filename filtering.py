import math
import re
from research_scout_agent.models import Paper, SearchConstraints

STOP_WORDS = {
    "the", "a", "an", "and", "or", "for", "of", "to", "in", "on", "with",
    "using", "use", "about", "based", "paper", "research", "recent", "good",
    "find", "recommend", "summary", "summarize", "explain", "citation", "citations",
}


def _terms(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return {word for word in words if len(word) > 2 and word not in STOP_WORDS}


def year_matches(paper: Paper, constraints: SearchConstraints) -> bool:
    if constraints.year_operator == "any" or constraints.year is None:
        return True
    if paper.year is None:
        return False

    if constraints.year_operator == ">":
        return paper.year > constraints.year
    if constraints.year_operator == ">=":
        return paper.year >= constraints.year
    if constraints.year_operator == "<":
        return paper.year < constraints.year
    if constraints.year_operator == "<=":
        return paper.year <= constraints.year
    if constraints.year_operator == "==":
        return paper.year == constraints.year
    if constraints.year_operator == "between":
        if constraints.year_end is None:
            return False
        return constraints.year <= paper.year <= constraints.year_end

    return True


def citation_matches(paper: Paper, constraints: SearchConstraints) -> bool:
    if constraints.citation_operator == "any" or constraints.citation_count is None:
        return True
    if paper.citation_count is None:
        return False

    target = constraints.citation_count

    if constraints.citation_operator == ">":
        return paper.citation_count > target
    if constraints.citation_operator == ">=":
        return paper.citation_count >= target
    if constraints.citation_operator == "<":
        return paper.citation_count < target
    if constraints.citation_operator == "<=":
        return paper.citation_count <= target
    if constraints.citation_operator == "~":
        lower = math.floor(target * (1 - constraints.approximate_tolerance))
        upper = math.ceil(target * (1 + constraints.approximate_tolerance))
        return lower <= paper.citation_count <= upper

    return True


def relevance_score(paper: Paper, constraints: SearchConstraints) -> float:
    topic_terms = _terms(constraints.topic)
    if not topic_terms:
        return 0.0

    searchable = " ".join(
        [
            paper.title or "",
            paper.abstract or "",
            paper.venue or "",
        ]
    )
    paper_terms = _terms(searchable)
    overlap = len(topic_terms.intersection(paper_terms)) / max(1, len(topic_terms))
    citation_bonus = min((paper.citation_count or 0) / 1000, 2.0) * 0.05
    year_bonus = 0.05 if paper.year and paper.year >= 2020 else 0.0
    return overlap + citation_bonus + year_bonus


def filter_candidates(papers: list[Paper], constraints: SearchConstraints) -> list[Paper]:
    filtered = [
        paper for paper in papers
        if year_matches(paper, constraints) and citation_matches(paper, constraints)
    ]

    return sorted(
        filtered,
        key=lambda paper: (relevance_score(paper, constraints), paper.citation_count or 0),
        reverse=True,
    )


def select_best_paper(papers: list[Paper], constraints: SearchConstraints) -> Paper | None:
    filtered = filter_candidates(papers, constraints)
    return filtered[0] if filtered else None