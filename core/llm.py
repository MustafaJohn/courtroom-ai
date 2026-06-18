import time
from openai import OpenAI, APIError, APITimeoutError, RateLimitError
from core.config import settings

client = OpenAI(api_key=settings.openai_api_key, timeout=30.0)

MAX_RETRIES = 3
BACKOFF_SECONDS = 2  # doubles each retry: 2s, 4s, 8s


def chat(system: str, user: str) -> str:
    """
    Single-turn chat completion. Returns assistant content as string.
    Retries on transient failures (timeout, rate limit, API error) with
    exponential backoff. Raises on final failure — the caller (main.py)
    decides how to surface that to the user.
    """
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=settings.model,
                temperature=settings.temperature,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            content = response.choices[0].message.content
            if not content or not content.strip():
                raise ValueError("Model returned an empty response.")
            return content.strip()

        except (APITimeoutError, RateLimitError, APIError) as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(BACKOFF_SECONDS * attempt)
                continue
            raise RuntimeError(
                f"LLM call failed after {MAX_RETRIES} attempts: {e}"
            ) from e

    # Unreachable, but keeps type-checkers happy.
    raise RuntimeError(f"LLM call failed: {last_error}")