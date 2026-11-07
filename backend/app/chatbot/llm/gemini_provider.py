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
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ],
        }

        # Up to 2 attempts (initial attempt + one retry on timeout or 5xx)
        max_attempts = 2
        last_error_msg = "Unknown error"
        last_status_code = None
        last_err_text = None

        for attempt in range(max_attempts):
            try:
                # Use injected client if provided (e.g. for MockTransport testing), else create managed client
                if self._client is not None:
                    response = self._client.post(url, headers=headers, json=payload, timeout=timeout)
                else:
                    with httpx.Client(timeout=timeout) as client:
                        response = client.post(url, headers=headers, json=payload)

                status_code = response.status_code

                # Parse provider's error text safely if available
                provider_err_text = None
                if status_code != 200:
                    try:
                        err_json = response.json()
                        if isinstance(err_json, dict):
                            err_obj = err_json.get("error")
                            if isinstance(err_obj, dict):
                                provider_err_text = err_obj.get("message")
                            elif isinstance(err_obj, str):
                                provider_err_text = err_obj
                    except Exception:
                        pass

                # Retry on 5xx server errors
                if status_code >= 500:
                    last_error_msg = f"Server returned HTTP {status_code}"
                    last_status_code = status_code
                    last_err_text = provider_err_text or f"Server error {status_code}"
                    if attempt < max_attempts - 1:
                        continue
                    raise LLMError(
                        last_error_msg,
                        provider="gemini",
                        status_code=status_code,
                        error_text=last_err_text,
                    )

                if status_code != 200:
                    err_msg = f"Request failed with HTTP {status_code}"
                    if provider_err_text:
                        err_msg += f": {provider_err_text}"
                    raise LLMError(
                        err_msg,
                        provider="gemini",
                        status_code=status_code,
                        error_text=provider_err_text or f"HTTP {status_code}",
                    )

                try:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        raise LLMError("Empty response: no candidates returned", provider="gemini")
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if not parts or not parts[0].get("text"):
                        raise LLMError("Empty response: no content text returned", provider="gemini")
                    return parts[0]["text"].strip()
                except (ValueError, KeyError, IndexError):
                    raise LLMError("Malformed response payload from provider", provider="gemini") from None

            except httpx.TimeoutException:
                last_error_msg = "Request timed out"
                if attempt < max_attempts - 1:
                    continue
                raise LLMError(
                    last_error_msg,
                    provider="gemini",
                    status_code=408,
                    error_text="Request timed out",
                ) from None
            except httpx.RequestError:
                raise LLMError("Network communication error", provider="gemini") from None
            except LLMError:
                raise
            except Exception:
                raise LLMError("Unexpected generation failure", provider="gemini") from None

        raise LLMError(
            last_error_msg,
            provider="gemini",
            status_code=last_status_code,
            error_text=last_err_text,
        )
