from research_scout_agent.models import AgentResult, Paper, SearchConstraints


def format_constraints(constraints: SearchConstraints) -> str:
    parts = [f"topic='{constraints.topic}'"]
    if constraints.year_operator != "any":
        if constraints.year_operator == "between":
            parts.append(f"year between {constraints.year} and {constraints.year_end}")
        else:
            parts.append(f"year {constraints.year_operator} {constraints.year}")
    if constraints.citation_operator != "any":
        parts.append(f"citations {constraints.citation_operator} {constraints.citation_count}")
    return ", ".join(parts)


def format_paper_block(paper: Paper) -> str:
    authors = ", ".join(paper.authors[:6])
    if len(paper.authors) > 6:
        authors += ", et al."

    return f"""Paper title: {paper.title}
Authors: {authors or "Unknown"}
Publication year: {paper.year if paper.year is not None else "Unknown"}
Citation count: {paper.citation_count if paper.citation_count is not None else "Unknown"}
Source of citation count: {paper.source}
Paper URL: {paper.url or "No URL returned"}
DOI: {paper.doi or "No DOI returned"}
Venue: {paper.venue or "Unknown"}"""


def deterministic_answer(result: AgentResult) -> str:
    constraints_text = format_constraints(result.constraints)

    if result.selected_paper is None:
        return f"""No matching paper was found.

Parsed constraints: {constraints_text}
Tool used: {result.tool_name}
Tool query: {result.tool_query}
Candidates checked: {result.candidates_seen}
Candidates after strict filtering: {result.candidates_after_filtering}

Explanation:
The agent rejected all retrieved candidates because none satisfied the parsed year and citation constraints at the same time. To avoid hallucination, no paper title or citation count is invented.

Uncertainty:
{result.uncertainty}"""

    paper = result.selected_paper
    abstract_hint = ""
    if paper.abstract:
        abstract_hint = paper.abstract[:700].replace("\n", " ")
        if len(paper.abstract) > 700:
            abstract_hint += "..."

    return f"""Recommended paper

{format_paper_block(paper)}

Why this paper matches the request:
- Parsed constraints: {constraints_text}
- The paper was returned by {result.tool_name}, not from the LLM's memory.
- The publication year and citation count were checked by deterministic Python filtering.
- Citation count source: {paper.source}.
- The paper title/abstract contains terms related to the requested topic.

Short contribution / relevance summary:
{abstract_hint or "No abstract was returned by the API, so the explanation is limited to the title, venue, year and citation metadata."}

Search transparency:
- Tool query: {result.tool_query}
- Candidates checked: {result.candidates_seen}
- Candidates after filtering: {result.candidates_after_filtering}

Uncertainty:
{result.uncertainty}"""
