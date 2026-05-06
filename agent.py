import json
from typing import Optional

from autogen import AssistantAgent

from answer_formatter import deterministic_answer, format_constraints
from config import get_llm_config
from filtering import filter_candidates
from models import AgentResult, Paper
from request_parser import parse_user_request
from tools.semantic_scholar_tool import search_papers_as_models


class ResearchScoutAgent:
    """
    AutoGen-based research scout agent.

    Design decision:
    - Deterministic Python parses constraints and filters papers.
    - Semantic Scholar API provides metadata and citation counts.
    - AutoGen LLM only writes the final explanation from verified data.

    This prevents the LLM from inventing citation counts or paper metadata.
    """

    def __init__(self, use_llm: bool = True, search_limit: int = 30):
        self.use_llm = use_llm
        self.search_limit = search_limit
        self.assistant: Optional[AssistantAgent] = None

        if use_llm:
            self.assistant = AssistantAgent(
                name="ResearchScout",
                system_message=(
                    "You are a careful research scout for a software company. "
                    "You must only use the paper metadata provided by the Python tool layer. "
                    "Never invent paper titles, authors, years, URLs, DOIs, abstracts or citation counts. "
                    "If information is missing, say that it was not returned by the API. "
                    "Write short, evidence-based recommendations."
                ),
                llm_config=get_llm_config(),
            )

    def solve(self, request: str) -> AgentResult:
        constraints = parse_user_request(request)
        tool_query = constraints.topic
        tool_name = "Semantic Scholar Graph API paper search tool"

        tool_error = None

        try:
            papers = search_papers_as_models(tool_query, limit=self.search_limit)
        except Exception as error:
            papers = []
            tool_error = str(error)

        filtered = filter_candidates(papers, constraints)
        selected = filtered[0] if filtered else None

        uncertainty = (
            "Citation counts are retrieved from Semantic Scholar at runtime and may change over time. "
            "The agent does not verify full paper content beyond returned metadata/abstract."
        )

        if tool_error:
            uncertainty += (
                "\n\nExternal tool issue: "
                f"{tool_error}\n"
                "Because the external research API failed, the agent refuses to invent a paper or citation count."
            )

        result = AgentResult(
            request=request,
            constraints=constraints,
            tool_name=tool_name,
            tool_query=tool_query,
            candidates_seen=len(papers),
            candidates_after_filtering=len(filtered),
            selected_paper=selected,
            answer="",
            uncertainty=uncertainty,
            tool_called=True,
        )

        if tool_error:
            result.answer = deterministic_answer(result)
        else:
            result.answer = self._build_answer(result, filtered[:5])

        return result

    def _build_answer(self, result: AgentResult, top_candidates: list[Paper]) -> str:
        fallback = deterministic_answer(result)

        if not self.use_llm or self.assistant is None:
            return fallback

        try:
            metadata = {
                "user_request": result.request,
                "parsed_constraints": format_constraints(result.constraints),
                "tool_name": result.tool_name,
                "tool_query": result.tool_query,
                "candidates_seen": result.candidates_seen,
                "candidates_after_filtering": result.candidates_after_filtering,
                "selected_paper": result.selected_paper.as_dict() if result.selected_paper else None,
                "top_filtered_candidates": [paper.as_dict() for paper in top_candidates],
                "uncertainty": result.uncertainty,
            }

            prompt = f"""
Create the final answer for the user from this verified metadata.

Rules:
- Do not add any citation count, URL, title, author or year that is not present in the metadata.
- If selected_paper is null, clearly reject the request and explain why.
- Include: title, authors, publication year, citation count, source of citation count, link, and explanation.
- Mention uncertainty.
- Keep it concise.

Verified metadata:
{json.dumps(metadata, indent=2)}
"""

            reply = self.assistant.generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )

            if isinstance(reply, dict):
                content = reply.get("content", "").strip()
            else:
                content = str(reply).strip()

            return content or fallback
        except Exception as error:
            return fallback + f"\n\nLLM synthesis failed, so deterministic answer was used. Error: {error}"
