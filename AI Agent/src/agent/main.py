from __future__ import annotations

import logging

from .config import load_settings
from .email_sender import EmailSender
from .outfit_agent import build_recommendation
from .weather_client import WeatherClient


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run_once() -> None:
    settings = load_settings()

    weather_client = WeatherClient()
    weather = weather_client.fetch_today(
        settings.city_name, latitude=settings.city_lat, longitude=settings.city_lon
    )

    recommendation = build_recommendation(
        weather,
        llm_api_key=settings.llm_api_key,
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        strict_mode=settings.llm_strict_mode,
    )

    sender = EmailSender(
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        smtp_user=settings.smtp_user,
        smtp_password=settings.smtp_password,
        smtp_from=settings.smtp_from,
    )
    sender.send(
        to_email=settings.recipient_email,
        subject=recommendation.subject,
        body=recommendation.body,
    )
    logger.info("Sent recommendation email to %s", settings.recipient_email)


if __name__ == "__main__":
    run_once()
