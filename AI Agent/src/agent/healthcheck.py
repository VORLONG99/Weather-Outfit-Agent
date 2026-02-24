from __future__ import annotations

import socket
from urllib.parse import urlparse

import requests

from .config import load_settings
from .weather_client import FORECAST_URL


def _resolve(host: str) -> tuple[bool, str]:
    try:
        infos = socket.getaddrinfo(host, None)
        ip = infos[0][4][0]
        return True, f"resolved to {ip}"
    except Exception as exc:
        return False, str(exc)


def _tcp_connect(host: str, port: int, timeout: float = 5.0) -> tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, "connected"
    except Exception as exc:
        return False, str(exc)


def _http_get(url: str, timeout: float = 10.0) -> tuple[bool, str]:
    try:
        r = requests.get(url, timeout=timeout)
        return True, f"HTTP {r.status_code}"
    except Exception as exc:
        return False, str(exc)


def run_healthcheck() -> int:
    settings = load_settings()
    weather_host = urlparse(FORECAST_URL).hostname or "api.open-meteo.com"
    smtp_host = settings.smtp_host
    smtp_port = settings.smtp_port
    llm_host = None
    if settings.llm_base_url:
        llm_host = urlparse(settings.llm_base_url).hostname

    checks = [
        ("DNS weather", _resolve(weather_host)),
        ("TCP weather:443", _tcp_connect(weather_host, 443)),
        ("HTTP weather", _http_get(FORECAST_URL)),
        ("DNS smtp", _resolve(smtp_host)),
        ("TCP smtp", _tcp_connect(smtp_host, smtp_port)),
    ]
    if llm_host:
        checks.extend(
            [
                ("DNS llm", _resolve(llm_host)),
                ("TCP llm:443", _tcp_connect(llm_host, 443)),
            ]
        )

    has_error = False
    for name, (ok, detail) in checks:
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {name}: {detail}")
        if not ok:
            has_error = True

    return 1 if has_error else 0


if __name__ == "__main__":
    raise SystemExit(run_healthcheck())
