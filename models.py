from dataclasses import dataclass, field
from typing import Any, Literal, Optional

YearOperator = Literal[">", ">=", "<", "<=", "==", "between", "any"]
CitationOperator = Literal[">", ">=", "<", "<=", "~", "any"]


@dataclass
class SearchConstraints:
    raw_request: str
    topic: str
    year_operator: YearOperator = "any"
    year: Optional[int] = None
    year_end: Optional[int] = None
    citation_operator: CitationOperator = "any"
    citation_count: Optional[int] = None
    approximate_tolerance: float = 0.25
    requested_summary: bool = False
    ambiguous: bool = False


@dataclass
class Paper:
    paper_id: str
    title: str
    authors: list[str]
    year: Optional[int]
    citation_count: Optional[int]
    url: Optional[str]
    abstract: Optional[str]
    venue: Optional[str] = None
    doi: Optional[str] = None
    source: str = "Semantic Scholar Graph API"
    raw: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "citation_count": self.citation_count,
            "url": self.url,
            "abstract": self.abstract,
            "venue": self.venue,
            "doi": self.doi,
            "source": self.source,
        }


@dataclass
class AgentResult:
    request: str
    constraints: SearchConstraints
    tool_name: str
    tool_query: str
    candidates_seen: int
    candidates_after_filtering: int
    selected_paper: Optional[Paper]
    answer: str
    uncertainty: str
    tool_called: bool = True
