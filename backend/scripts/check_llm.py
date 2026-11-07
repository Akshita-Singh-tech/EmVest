#!/usr/bin/env python3
"""Live integration check script for Emvest LLM provider.

Invokes the configured provider (Gemini or OpenAI) with a simple prompt,
measures network latency, and prints the first 200 characters of the response.
NEVER prints the API key or raw authorization headers.
"""

import os
import sys
import time

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.chatbot.llm import get_provider, LLMError


def main():
    print("=" * 60)
    print("Emvest LLM Live Integration Check")
    print("=" * 60)

    provider = get_provider()

    if provider is None:
        print("\n[!] No active LLM provider detected.")
        print("    Neither GEMINI_API_KEY nor OPENAI_API_KEY is configured in backend environment,")
        print("    or DEFAULT_LLM_PROVIDER is set to 'deterministic'.")
        print("\nTo test live:")
        print("  export GEMINI_API_KEY='your_api_key_here'")
        print("  python scripts/check_llm.py")
        sys.exit(1)

    provider_class = provider.__class__.__name__
    provider_name = "Gemini" if "Gemini" in provider_class else ("OpenAI" if "OpenAI" in provider_class else provider_class)
    model_name = getattr(provider, "model", "default")

    print(f"Provider: {provider_name} (Model: {model_name})")
    print("Sending live test prompt...")

    system_prompt = "You are Emvest AI. Provide a concise 2-sentence overview of the NIFTY 50 index. End with 'Not financial advice.'"
    user_prompt = "What is the NIFTY 50 benchmark index?"

    t_start = time.perf_counter()
    try:
        answer = provider.generate(system_prompt=system_prompt, user_prompt=user_prompt, timeout=15.0)
        latency = time.perf_counter() - t_start
    except LLMError as err:
        latency = time.perf_counter() - t_start
        print(f"\n[X] Live call failed after {latency:.2f}s: {err}")
        sys.exit(1)
    except Exception as exc:
        latency = time.perf_counter() - t_start
        print(f"\n[X] Unexpected error after {latency:.2f}s: {exc.__class__.__name__}")
        sys.exit(1)

    print("\n[✓] Live LLM Response Received:")
    print(f"    Latency: {latency:.2f}s")
    print("-" * 60)
    preview = answer[:200]
    print(f"    Preview: {preview}")
    if len(answer) > 200:
        print("    ...")
    print("-" * 60)
    print("Live integration check completed successfully.")


if __name__ == "__main__":
    main()
