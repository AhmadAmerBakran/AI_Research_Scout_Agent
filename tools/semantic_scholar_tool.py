import os
import time
from typing import Annotated, Any

import requests

from research_scout_agent.models import Paper

SEMANTIC_SCHOLAR_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

FIELDS = ",".join(
    [
        "paperId",
        "url",
        "title",
        "abstract",
        "venue",
        "year",
        "citationCount",
        "authors",
        "externalIds",
    ]
)


def _paper_from_api_item(item: dict[str, Any]) -> Paper:
    external_ids = item.get("externalIds") or {}
    doi = external_ids.get("DOI") if isinstance(external_ids, dict) else None

    return Paper(
        paper_id=str(item.get("paperId") or ""),
        title=str(item.get("title") or "Untitled"),
        authors=[author.get("name", "Unknown") for author in item.get("authors", [])],
        year=item.get("year"),
        citation_count=item.get("citationCount"),
        url=item.get("url"),
        abstract=item.get("abstract"),
        venue=item.get("venue"),
        doi=doi,
        source="Semantic Scholar Graph API",
        raw=item,
    )


def search_papers_semantic_scholar(
    query: Annotated[str, "Research topic or keywords to search for."],
    limit: Annotated[int, "Maximum number of papers to retrieve."] = 20,
) -> list[dict[str, Any]]:
    """
    Search Semantic Scholar for academic papers.

    Citation counts are taken directly from Semantic Scholar.
    The LLM must not invent or modify citation counts.
    """
    api_key = os.getenv("S2_API_KEY")
    headers = {}

    if api_key:
        headers["x-api-key"] = api_key

    params = {
        "query": query,
        "limit": max(1, min(limit, 100)),
        "fields": FIELDS,
    }

    last_error: str = "No request was completed."
    max_retries = 6

    for attempt in range(max_retries):
        try:
            time.sleep(1)

            response = requests.get(
                SEMANTIC_SCHOLAR_SEARCH_URL,
                params=params,
                headers=headers,
                timeout=30,
            )

            if response.status_code == 429:
                retry_after_header = response.headers.get("Retry-After")

                try:
                    retry_after = int(retry_after_header) if retry_after_header else 10
                except ValueError:
                    retry_after = 10

                delay = max(retry_after, 10 * (attempt + 1))

                last_error = (
                    f"Semantic Scholar rate limit hit: HTTP 429. "
                    f"Attempt {attempt + 1}/{max_retries}. "
                    f"Retrying after {delay} seconds."
                )

                if attempt < max_retries - 1:
                    time.sleep(delay)
                    continue

                break

            if response.status_code >= 500:
                delay = 5 * (attempt + 1)

                last_error = (
                    f"Semantic Scholar server error: HTTP {response.status_code}. "
                    f"Response: {response.text[:300]}"
                )

                if attempt < max_retries - 1:
                    time.sleep(delay)
                    continue

                break

            response.raise_for_status()

            payload = response.json()
            papers = [_paper_from_api_item(item) for item in payload.get("data", [])]

            return [paper.as_dict() for paper in papers]

        except requests.RequestException as error:
            last_error = str(error)

            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue

    raise RuntimeError(f"Semantic Scholar search failed after retries: {last_error}")


def search_papers_as_models(query: str, limit: int = 20) -> list[Paper]:
    """
    Internal helper for deterministic filtering.
    """
    return [Paper(**paper) for paper in search_papers_semantic_scholar(query, limit)]
