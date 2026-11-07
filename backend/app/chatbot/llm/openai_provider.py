from typing import Optional
import httpx

from app.chatbot.llm.base import LLMProvider, LLMError


class OpenAIProvider(LLMProvider):
    """OpenAI-compatible chat completion LLM provider wrapper via direct HTTP REST API."""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        provider_name: str = "openai",
        client: Optional[httpx.Client] = None,
    ):
        if not api_key:
            raise LLMError(f"{provider_name.capitalize()} API key is required", provider=provider_name)
        if not model:
            raise LLMError(f"{provider_name.capitalize()} model name is required", provider=provider_name)
        self._api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.provider_name = provider_name
        self._client = client

    def generate(self, system_prompt: str, user_prompt: str, *, timeout: float = 15.0) -> str:
        """Call chat/completions endpoint with 15s timeout and one retry on 5xx or timeout."""
        url = f"{self.base_url}/chat/completions"
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
                            else:
                                provider_err_text = err_json.get("message")
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
                        provider=self.provider_name,
                        status_code=status_code,
                        error_text=last_err_text,
                    )

                if status_code != 200:
                    err_msg = f"Request failed with HTTP {status_code}"
                    if provider_err_text:
                        err_msg += f": {provider_err_text}"
                    raise LLMError(
                        err_msg,
                        provider=self.provider_name,
                        status_code=status_code,
                        error_text=provider_err_text or f"HTTP {status_code}",
                    )

                try:
                    data = response.json()
                    choices = data.get("choices", [])
                    if not choices:
                        raise LLMError("Empty response: no choices returned", provider=self.provider_name)
                    msg = choices[0].get("message", {})
                    content = msg.get("content")
                    if content is None:
                        raise LLMError("Empty response: content is null", provider=self.provider_name)
                    return content.strip()
                except (ValueError, KeyError, IndexError):
                    raise LLMError("Malformed response payload from provider", provider=self.provider_name) from None

            except httpx.TimeoutException:
                last_error_msg = "Request timed out"
                if attempt < max_attempts - 1:
                    continue
                raise LLMError(
                    last_error_msg,
                    provider=self.provider_name,
                    status_code=408,
                    error_text="Request timed out",
                ) from None
            except httpx.RequestError:
                raise LLMError("Network communication error", provider=self.provider_name) from None
            except LLMError:
                raise
            except Exception:
                raise LLMError("Unexpected generation failure", provider=self.provider_name) from None

        raise LLMError(
            last_error_msg,
            provider=self.provider_name,
            status_code=last_status_code,
            error_text=last_err_text,
        )
