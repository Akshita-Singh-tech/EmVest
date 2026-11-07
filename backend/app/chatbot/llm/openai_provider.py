from typing import Optional
import httpx

from app.chatbot.llm.base import LLMProvider, LLMError


class OpenAIProvider(LLMProvider):
    """OpenAI chat completion LLM provider wrapper via direct HTTP REST API."""

    def __init__(
        self,
        api_key: str,
        model: str,
        client: Optional[httpx.Client] = None,
    ):
        if not api_key:
            raise LLMError("OpenAI API key is required", provider="openai")
        if not model:
            raise LLMError("OpenAI model name is required", provider="openai")
        self._api_key = api_key
        self.model = model
        self._client = client

    def generate(self, system_prompt: str, user_prompt: str, *, timeout: float = 15.0) -> str:
        """Call OpenAI chat/completions endpoint with 15s timeout and one retry on 5xx or timeout."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        # Up to 2 attempts (initial attempt + one retry on timeout or 5xx)
        max_attempts = 2
        last_error_msg = "Unknown error"

        for attempt in range(max_attempts):
            try:
                # Use injected client if provided (e.g. for MockTransport testing), else create managed client
                if self._client is not None:
                    response = self._client.post(url, headers=headers, json=payload, timeout=timeout)
                else:
                    with httpx.Client(timeout=timeout) as client:
                        response = client.post(url, headers=headers, json=payload)

                status_code = response.status_code

                # Retry on 5xx server errors
                if status_code >= 500:
                    last_error_msg = f"Server returned HTTP {status_code}"
                    if attempt < max_attempts - 1:
                        continue
                    raise LLMError(last_error_msg, provider="openai")

                if status_code != 200:
                    raise LLMError(f"Request failed with HTTP {status_code}", provider="openai")

                try:
                    data = response.json()
                    choices = data.get("choices", [])
                    if not choices:
                        raise LLMError("Empty response: no choices returned", provider="openai")
                    msg = choices[0].get("message", {})
                    content = msg.get("content")
                    if content is None:
                        raise LLMError("Empty response: content is null", provider="openai")
                    return content.strip()
                except (ValueError, KeyError, IndexError) as err:
                    raise LLMError("Malformed response payload from provider", provider="openai") from None

            except httpx.TimeoutException:
                last_error_msg = "Request timed out"
                if attempt < max_attempts - 1:
                    continue
                raise LLMError(last_error_msg, provider="openai") from None
            except httpx.RequestError:
                raise LLMError("Network communication error", provider="openai") from None
            except LLMError:
                raise
            except Exception:
                raise LLMError("Unexpected generation failure", provider="openai") from None

        raise LLMError(last_error_msg, provider="openai")
