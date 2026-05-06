import os
from dotenv import load_dotenv

load_dotenv()


def get_llm_config() -> dict:
    """
    Returns an AutoGen LLM config.

    Default: Ollama locally, because it avoids committing API keys.
    Optional: Mistral cloud, if MISTRAL_API_KEY is configured.
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

    if provider == "mistral":
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError(
                "LLM_PROVIDER=mistral requires MISTRAL_API_KEY in .env or environment variables."
            )

        return {
            "config_list": [
                {
                    "model": os.getenv("MISTRAL_MODEL", "open-mistral-nemo"),
                    "api_key": api_key,
                    "api_type": "mistral",
                    "api_rate_limit": 0.25,
                    "repeat_penalty": 1.1,
                    "temperature": 0.0,
                    "seed": 42,
                    "stream": False,
                    "native_tool_calls": False,
                    "cache_seed": None,
                }
            ],
            "cache_seed": None,
            "timeout": 120,
        }

    return {
        "config_list": [
            {
                "model": os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
                "api_type": "ollama",
                "client_host": os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434"),
                "stream": False,
                "temperature": 0.0,
                "seed": 42,
                "top_k": 40,
                "top_p": 0.8,
                "repeat_penalty": 1.1,
                "num_predict": -1,
                "native_tool_calls": False,
            }
        ],
        "cache_seed": None,
        "timeout": 120,
    }
