from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    city_name: str
    city_lat: float | None
    city_lon: float | None
    recipient_email: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_from: str
    timezone: str
    schedule_hour: int
    schedule_minute: int
    llm_api_key: str | None
    llm_model: str
    llm_base_url: str | None
    llm_strict_mode: bool


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required env var: {name}")
    return value


def load_settings() -> Settings:
    load_dotenv()
    llm_api_key = os.getenv("LLM_API_KEY", "").strip() or os.getenv(
        "OPENAI_API_KEY", ""
    ).strip()
    llm_model = os.getenv("LLM_MODEL", "").strip() or os.getenv(
        "OPENAI_MODEL", "gpt-4o-mini"
    ).strip()
    llm_base_url = os.getenv("LLM_BASE_URL", "").strip() or os.getenv(
        "OPENAI_BASE_URL", ""
    ).strip()
    city_lat_raw = os.getenv("CITY_LAT", "").strip()
    city_lon_raw = os.getenv("CITY_LON", "").strip()
    llm_strict_mode = os.getenv("LLM_STRICT_MODE", "false").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )

    return Settings(
        city_name=os.getenv("CITY_NAME", "Beijing").strip(),
        city_lat=float(city_lat_raw) if city_lat_raw else None,
        city_lon=float(city_lon_raw) if city_lon_raw else None,
        recipient_email=_required("RECIPIENT_EMAIL"),
        smtp_host=_required("SMTP_HOST"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=_required("SMTP_USER"),
        smtp_password=_required("SMTP_PASSWORD"),
        smtp_from=_required("SMTP_FROM"),
        timezone=os.getenv("TIMEZONE", "Asia/Shanghai").strip(),
        schedule_hour=int(os.getenv("SCHEDULE_HOUR", "8")),
        schedule_minute=int(os.getenv("SCHEDULE_MINUTE", "0")),
        llm_api_key=llm_api_key or None,
        llm_model=llm_model,
        llm_base_url=llm_base_url or None,
        llm_strict_mode=llm_strict_mode,
    )
