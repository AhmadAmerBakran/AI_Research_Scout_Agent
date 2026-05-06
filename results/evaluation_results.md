# Evaluation Results

Generated: 2026-05-06T13:44:05

Passed core checks: 10/10

## Method

The evaluation follows a systematic checklist inspired by agent evaluation principles: task success, constraint satisfaction, source validity, hallucination control, and usefulness of the explanation. For each prompt, the agent must retrieve data through the Semantic Scholar tool, filter papers using deterministic year/citation checks, and produce an answer that includes verifiable metadata.

## Results Table

| # | Prompt                                                                                        | Found | Year OK | Citations OK | Source OK | No hallucination | Useful explanation | Passed | Selected paper |
|---|-----------------------------------------------------------------------------------------------|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Find a research paper about LLM agents for software engineering that was published after 2... | True | True | True | True | True | True | True | Agentless: Demystifying LLM-based Software Engineering Agents |
| 2 | Find a paper about retrieval-augmented generation published before 2021 with more than 500... | True | True | True | True | True | True | True | Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks |
| 3 | Find a recent paper about AI agents using tools and explain whether it would be useful for... | True | True | True | True | True | True | True | Agent Hospital: A Simulacrum of Hospital with Evolvable Medical Agents |
| 4 | Find a paper about chain-of-thought prompting published in 2022 with at least 1000 citatio... | True | True | True | True | True | True | True | Chain of Thought Prompting Elicits Reasoning in Large Language Models |
| 5 | Find a paper about code generation with large language models after 2020 with at least 200... | True | True | True | True | True | True | True | Evaluating Large Language Models Trained on Code |
| 6 | Find a paper about software defect prediction before 2015 with more than 1000 citations....   | False | True | True | True | True | True | True | No paper selected |
| 7 | Find a paper about diffusion models published in 2020 with at least 500 citations....         | False | True | True | True | True | True | True | No paper selected |
| 8 | Find a paper about quantum potato debugging after 2024 with at least 9999 citations....       | False | True | True | True | True | True | True | No paper selected |
| 9 | Find me a good paper about agents....                                                         | True | True | True | True | True | True | True | Green activation using reducing agents of carbon-based 3D printed electrodes: Turning good electrodes to great |
| 10 | Find a paper about transformers in natural language processing published in 2017 with at l... | False | True | True | True | True | True | True | No paper selected |

## Notes

- A failure to find a paper is not automatically a hallucination failure. It is acceptable when the agent clearly rejects the request and does not invent metadata.
- Citation counts are time-sensitive and may change because they are retrieved live from Semantic Scholar.
- Ambiguous prompts are expected to be weaker because the agent must infer a broad topic.