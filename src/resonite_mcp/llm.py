import logging
import os

import httpx

logger = logging.getLogger(__name__)

# Constants for local substrate detection
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
LM_STUDIO_URL = os.environ.get("LM_STUDIO_URL", "http://localhost:1234")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class LLMSubstrate:
    """Unified interface for LLM substrate interaction."""

    def __init__(self, name: str, provider: str, url: str, model_id: str | None = None):
        self.name = name
        self.provider = provider
        self.url = url
        self.model_id = model_id


async def detect_local_llms() -> list[LLMSubstrate]:
    """Probes local endpoints for running LLM servers."""
    found = []

    # Check Ollama
    try:
        async with httpx.AsyncClient(timeout=0.5) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = data.get("models", [])
                if models:
                    found.append(
                        LLMSubstrate(
                            name=models[0]["name"],
                            provider="Ollama",
                            url=OLLAMA_URL,
                            model_id=models[0]["name"],
                        )
                    )
                else:
                    found.append(
                        LLMSubstrate(
                            name="Ollama (No Models Installed)",
                            provider="Ollama",
                            url=OLLAMA_URL,
                        )
                    )
    except (httpx.ConnectError, httpx.TimeoutException):
        pass

    # Check LM Studio
    try:
        async with httpx.AsyncClient(timeout=0.5) as client:
            resp = await client.get(f"{LM_STUDIO_URL}/v1/models")
            if resp.status_code == 200:
                data = resp.json()
                models = data.get("data", [])
                if models:
                    found.append(
                        LLMSubstrate(
                            name=models[0]["id"],
                            provider="LM Studio",
                            url=LM_STUDIO_URL,
                            model_id=models[0]["id"],
                        )
                    )
                else:
                    found.append(
                        LLMSubstrate(
                            name="LM Studio (Running)",
                            provider="LM Studio",
                            url=LM_STUDIO_URL,
                        )
                    )
    except (httpx.ConnectError, httpx.TimeoutException):
        pass

    return found


async def synthesize_answer(prompt: str, context: str, substrate: LLMSubstrate) -> str:
    """Synthesizes an answer using the detected substrate."""
    full_prompt = f"Context from documentation:\n{context}\n\nQuestion: {prompt}\n\nPlease provide a concise technical answer based ONLY on the context above."

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if substrate.provider == "Ollama":
                payload = {
                    "model": substrate.model_id or "gemma2:9b",  # Fallback default
                    "prompt": full_prompt,
                    "stream": False,
                }
                resp = await client.post(f"{substrate.url}/api/generate", json=payload)
                if resp.status_code == 200:
                    return resp.json().get("response", "No response from Ollama.")

            elif substrate.provider == "LM Studio":
                payload = {
                    "model": substrate.model_id,
                    "messages": [{"role": "user", "content": full_prompt}],
                    "temperature": 0.3,
                }
                resp = await client.post(f"{substrate.url}/v1/chat/completions", json=payload)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]

    except Exception as e:
        logger.error(f"Synthesis failed with {substrate.provider}: {e}")

    return "Failed to synthesize answer with local LLM."


async def get_best_substrate() -> LLMSubstrate | None:
    """Returns the most capable local substrate, or None."""
    local_llms = await detect_local_llms()
    if local_llms:
        # Prioritize substrates with actual models loaded
        with_models = [s for s in local_llms if s.model_id]
        if with_models:
            return with_models[0]
        return local_llms[0]
    return None
