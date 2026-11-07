from typing import Optional

from app.core.config import settings
from app.chatbot.llm.base import LLMProvider
from app.chatbot.llm.gemini_provider import GeminiProvider
from app.chatbot.llm.openai_provider import OpenAIProvider


def get_provider(
    provider_type: Optional[str] = None,
    gemini_key: Optional[str] = None,
    gemini_model: Optional[str] = None,
    openai_key: Optional[str] = None,
    openai_model: Optional[str] = None,
) -> Optional[LLMProvider]:
    """Factory to retrieve the configured LLMProvider instance.

    Uses settings.default_llm_provider by default:
    - 'auto': returns GeminiProvider if gemini_api_key is set,
              else OpenAIProvider if openai_api_key is set,
              else None.
    - 'deterministic': always returns None.
    - 'gemini': returns GeminiProvider if key is set, else None.
    - 'openai': returns OpenAIProvider if key is set, else None.
    """
    mode = (provider_type or settings.default_llm_provider or "auto").lower().strip()
    g_key = gemini_key if gemini_key is not None else settings.gemini_api_key
    g_model = gemini_model or settings.gemini_model or "gemini-2.5-flash"
    o_key = openai_key if openai_key is not None else settings.openai_api_key
    o_model = openai_model or settings.openai_model or "gpt-4o-mini"

    if mode == "deterministic":
        return None

    if mode == "auto":
        if g_key and g_key.strip():
            return GeminiProvider(api_key=g_key.strip(), model=g_model)
        if o_key and o_key.strip():
            return OpenAIProvider(api_key=o_key.strip(), model=o_model)
        return None

    if mode == "gemini":
        if g_key and g_key.strip():
            return GeminiProvider(api_key=g_key.strip(), model=g_model)
        return None

    if mode == "openai":
        if o_key and o_key.strip():
            return OpenAIProvider(api_key=o_key.strip(), model=o_model)
        return None

    return None
