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

## 2. External tool (API)

The implemented custom tool is:

```text
/tools/semantic_scholar_tool.py
```

It calls the Semantic Scholar Graph API paper search endpoint and retrieves:

- paper title
- authors
- publication year
- citation count
- URL
- DOI, if available
- abstract, if available
- venue, if available


## 3. Agent workflow

The workflow is intentionally split between deterministic code and the LLM.

### Deterministic Python handles

- parsing year and citation constraints
- calling Semantic Scholar
- filtering papers by year and citations
- checking whether a result satisfies constraints
- rejecting invalid candidates

### AutoGen LLM handles

- writing the final explanation
- explaining why the selected paper is relevant
- explaining uncertainty and limitations

## 4. Setup instructions

### Step 1: Clone or open the project (PyCharm)

Open the project in PyCharm.

### Step 2: Create virtual environment

In PyCharm, create a new Python virtual environment, preferably Python 3.12.X

### Step 3: Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Configure environment

Copy `.env.example` to `.env`.

(Get your own API keys)

For local Ollama:

```text
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b
OLLAMA_HOST=http://127.0.0.1:11434
```

Then run:

```powershell
ollama pull llama3.1:8b
```

## 5. How to run the agent

From the project root:

```powershell
python -m main "Find a research paper about LLM agents for software engineering that was published after 2022 and has at least 100 citations. Explain why the paper is relevant and provide the source of the citation count."
```

To run without LLM synthesis and only use deterministic output:

```powershell
python -m main "Find a paper about retrieval-augmented generation published before 2021 with more than 500 citations." --no-llm
```

## 6. How to run the evaluation

The assignment requires at least 10 test prompts. They are implemented in:

```text
/evaluation/evaluate_agent.py
```

Run:

```powershell
python -m evaluation.evaluate_agent --use-llm
```

For faster evaluation without LLM calls:

```powershell
python -m evaluation.evaluate_agent
```

The script creates:

```text
results/evaluation_results.json
results/evaluation_results.md
```

## 7. Evaluation method

The evaluation checks whether the agent:

- found a relevant paper
- respected the year constraint
- respected the citation constraint
- provided a valid source
- avoided hallucinated information
- gave a useful explanation


### How did we prevent incorrect answers?

- Citation counts come from the API.
- Year and citation constraints are checked by Python code.
- The agent rejects invalid candidates.
- The final prompt tells the LLM not to invent missing information.
- The answer includes uncertainty.


## 8. Group member contributions

Ahmad Amer Bakran:

- Set up the project structure and Python environment.
- Implemented the AutoGen agent workflow and CLI entry point.
- Worked on request parsing, deterministic filtering and documentation.

Mahmoud Eybo:

- Worked on the Semantic Scholar API tool and API failure handling.
- Helped test the agent with different prompts and reviewed evaluation output.
- Helped prepare the demonstration and checked that the workflow matched the assignment requirements.

