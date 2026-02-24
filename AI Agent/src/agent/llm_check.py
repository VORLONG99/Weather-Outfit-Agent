from __future__ import annotations

from openai import OpenAI

from .config import load_settings


def run_llm_check() -> int:
    settings = load_settings()
    if not settings.llm_api_key:
        print("LLM_API_KEY is empty")
        return 1

    base_url = settings.llm_base_url
    if base_url and base_url.rstrip("/").count("/") == 2:
        base_url = f"{base_url.rstrip('/')}/v1"

    print(f"model={settings.llm_model}")
    print(f"base_url={base_url or '<openai-default>'}")

    client = OpenAI(api_key=settings.llm_api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "user", "content": "请只回复: llm-ok"}],
        temperature=0,
    )
    print("response:", (resp.choices[0].message.content or "").strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(run_llm_check())
