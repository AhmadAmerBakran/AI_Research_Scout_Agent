import re
from datetime import datetime
from models import SearchConstraints

_YEAR = r"(19\d{2}|20\d{2})"
_NUMBER = r"(\d{1,3}(?:,\d{3})+|\d+)"

REMOVE_PATTERNS = [
    rf"published\s+(after|before|in|during|from|since)\s+{_YEAR}",
    rf"(after|before|since|in|during|from)\s+{_YEAR}",
    rf"between\s+{_YEAR}\s+and\s+{_YEAR}",
    rf"(at least|min(?:imum)?|more than|over|greater than|less than|under|at most|max(?:imum)?|approximately|around|about)\s+{_NUMBER}\s+(citations|citation|cites)",
    r"find( me)?( a| an)?( research)? paper(s)?( about| on)?",
    r"summari[sz]e.*$",
    r"explain.*$",
    r"provide.*$",
    r"with\s*$",
]


def _parse_int(value: str) -> int:
    return int(value.replace(",", ""))


def _cleanup_topic(text: str) -> str:
    cleaned = text.lower()
    for pattern in REMOVE_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)

    cleaned = cleaned.replace("citation count", " ")
    cleaned = cleaned.replace("citations", " ")
    cleaned = cleaned.replace("published", " ")
    cleaned = cleaned.replace("relevant", " ")
    cleaned = cleaned.replace("source", " ")
    cleaned = cleaned.replace("the paper", " ")
    cleaned = cleaned.replace("a paper", " ")
    cleaned = cleaned.replace("paper", " ")
    cleaned = cleaned.replace("that was", " ")
    cleaned = cleaned.replace("that were", " ")
    cleaned = cleaned.replace("that has", " ")
    cleaned = cleaned.replace("that have", " ")
    cleaned = cleaned.replace("and has", " ")
    cleaned = cleaned.replace("and have", " ")
    cleaned = cleaned.replace("has at least", " ")
    cleaned = cleaned.replace("have at least", " ")
    cleaned = cleaned.replace("with at least", " ")
    cleaned = cleaned.replace("was published", " ")
    cleaned = cleaned.replace("were published", " ")

    # Remove common instruction words that sometimes remain after the regex cleanup.
    # This keeps the Semantic Scholar query focused on the actual research topic.
    cleaned = re.sub(
        r"\b(find|me|a|an|research|paper|papers|about|on|that|was|were|has|have|and|with|published)\b",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(r"[^a-zA-Z0-9+\- ]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned or text.strip()


def parse_user_request(request: str) -> SearchConstraints:
    """
    Extracts topic, year constraints and citation constraints from a user request.

    This parser is deterministic on purpose. The LLM should not invent constraints,
    citation counts or years. The parser handles common assignment-style prompts.
    """
    text = request.strip()
    lowered = text.lower()
    constraints = SearchConstraints(raw_request=text, topic=_cleanup_topic(text))

    # Year range: between 2020 and 2022
    match = re.search(rf"between\s+{_YEAR}\s+and\s+{_YEAR}", lowered)
    if match:
        constraints.year_operator = "between"
        constraints.year = int(match.group(1))
        constraints.year_end = int(match.group(2))
    else:
        # after/since means strict after in the assignment examples: after 2022 => > 2022
        match = re.search(rf"(?:published\s+)?(?:after|newer than)\s+{_YEAR}", lowered)
        if match:
            constraints.year_operator = ">"
            constraints.year = int(match.group(1))

        match = re.search(rf"(?:published\s+)?since\s+{_YEAR}", lowered)
        if match:
            constraints.year_operator = ">="
            constraints.year = int(match.group(1))

        match = re.search(rf"(?:published\s+)?(?:before|prior to|older than)\s+{_YEAR}", lowered)
        if match:
            constraints.year_operator = "<"
            constraints.year = int(match.group(1))

        match = re.search(rf"(?:published\s+)?(?:in|during|from|exactly)\s+{_YEAR}", lowered)
        if match and constraints.year_operator == "any":
            constraints.year_operator = "=="
            constraints.year = int(match.group(1))

    if "recent" in lowered and constraints.year_operator == "any":
        constraints.year_operator = ">="
        constraints.year = datetime.now().year - 3

    # Citations
    match = re.search(rf"(?:at least|min(?:imum)?)\s+{_NUMBER}\s+(?:citations|citation|cites)", lowered)
    if match:
        constraints.citation_operator = ">="
        constraints.citation_count = _parse_int(match.group(1))

    match = re.search(rf"(?:more than|over|greater than)\s+{_NUMBER}\s+(?:citations|citation|cites)", lowered)
    if match:
        constraints.citation_operator = ">"
        constraints.citation_count = _parse_int(match.group(1))

    match = re.search(rf"(?:less than|under)\s+{_NUMBER}\s+(?:citations|citation|cites)", lowered)
    if match:
        constraints.citation_operator = "<"
        constraints.citation_count = _parse_int(match.group(1))

    match = re.search(rf"(?:at most|max(?:imum)?)\s+{_NUMBER}\s+(?:citations|citation|cites)", lowered)
    if match:
        constraints.citation_operator = "<="
        constraints.citation_count = _parse_int(match.group(1))

    match = re.search(rf"(?:approximately|around|about)\s+{_NUMBER}\s+(?:citations|citation|cites)", lowered)
    if match:
        constraints.citation_operator = "~"
        constraints.citation_count = _parse_int(match.group(1))

    constraints.requested_summary = bool(re.search(r"summari[sz]e|contribution|explain", lowered))
    constraints.ambiguous = len(constraints.topic.split()) < 2

    return constraints