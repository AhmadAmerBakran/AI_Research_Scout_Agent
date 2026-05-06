import argparse

from agent import ResearchScoutAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Research Scout Agent using AutoGen and Semantic Scholar")
    parser.add_argument("prompt", help="Research paper request, including topic/year/citation constraints")
    parser.add_argument("--limit", type=int, default=30, help="Number of candidate papers to retrieve")
    parser.add_argument("--no-llm", action="store_true", help="Use deterministic output without AutoGen synthesis")

    args = parser.parse_args()

    agent = ResearchScoutAgent(use_llm=not args.no_llm, search_limit=args.limit)
    result = agent.solve(args.prompt)

    print(result.answer)


if __name__ == "__main__":
    main()
