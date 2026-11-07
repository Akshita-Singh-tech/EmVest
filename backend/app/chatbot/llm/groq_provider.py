from typing import Optional
import httpx

from app.chatbot.llm.openai_provider import OpenAIProvider


class GroqProvider(OpenAIProvider):
    """Groq chat completion provider reusing the OpenAI-compatible REST API.

    Uses base URL https://api.groq.com/openai/v1 and leverages Groq's high-throughput
    LPU hardware-accelerated open-weights inference models (e.g. llama-3.3-70b-versatile).
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://api.groq.com/openai/v1",
        client: Optional[httpx.Client] = None,
    ):
        super().__init__(
            api_key=api_key,
            model=model,
            base_url=base_url,
            provider_name="groq",
            client=client,
        )

