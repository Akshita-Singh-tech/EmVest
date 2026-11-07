from typing import Optional
import httpx

from app.chatbot.llm.base import LLMProvider, LLMError


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider wrapper via direct HTTP REST API."""

    def __init__(
        self,
        api_key: str,
        model: str,
        client: Optional[httpx.Client] = None,
    ):
        if not api_key:
            raise LLMError("Gemini API key is required", provider="gemini")
        if not model:
            raise LLMError("Gemini model name is required", provider="gemini")
        self._api_key = api_key
        self.model = model
        self._client = client

    def generate(self, system_prompt: str, user_prompt: str, *, timeout: float = 15.0) -> str:
        """Call Gemini generateContent endpoint with 15s timeout and one retry on 5xx or timeout."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        headers = {
            "x-goog-api-key": self._api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "parts": [{"text": user_prompt}]
                }
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
                    raise LLMError(last_error_msg, provider="gemini")

                if status_code != 200:
                    raise LLMError(f"Request failed with HTTP {status_code}", provider="gemini")

                try:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        raise LLMError("Empty response: no candidates returned", provider="gemini")
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if not parts or not parts[0].get("text"):
                        raise LLMError("Empty response: no content text returned", provider="gemini")
                    return parts[0]["text"].strip()
                except (ValueError, KeyError, IndexError) as err:
                    raise LLMError("Malformed response payload from provider", provider="gemini") from None

            except httpx.TimeoutException:
                last_error_msg = "Request timed out"
                if attempt < max_attempts - 1:
                    continue
                raise LLMError(last_error_msg, provider="gemini") from None
            except httpx.RequestError:
                raise LLMError("Network communication error", provider="gemini") from None
            except LLMError:
                raise
            except Exception:
                raise LLMError("Unexpected generation failure", provider="gemini") from None

        raise LLMError(last_error_msg, provider="gemini")

