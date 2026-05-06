# ML & LLMs Assignment : AI Research Agent Using AutoGen

### Group members:

- Ahmad Amer Bakran
- Mahmoud Eybo

## 1. Project purpose

This project implements an AI research assistant for a software company. The agent receives a user request such as:

> Find a research paper about LLM agents for software engineering that was published after 2022 and has at least 100 citations.

The agent then:

1. Parses the user request.
2. Extracts topic, year constraint and citation constraint.
3. Calls an external research-paper API tool.
4. Filters papers using deterministic Python code.
5. Selects a matching paper.
6. Uses AutoGen to produce a short evidence-based explanation from verified metadata.
7. Refuses to invent a paper if no candidate satisfies the constraints.