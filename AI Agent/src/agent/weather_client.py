from __future__ import annotations

from dataclasses import dataclass

import requests


GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


@dataclass(frozen=True)
class DailyWeather:
    city: str
    date: str
    temp_max: float
    temp_min: float
    apparent_temp_max: float
    apparent_temp_min: float
    precipitation_probability_max: int
    wind_speed_max: float

    @property
    def temp_avg(self) -> float:
        return (self.temp_max + self.temp_min) / 2


class WeatherClient:
    def __init__(self, timeout_seconds: int = 20) -> None:
        self.timeout_seconds = timeout_seconds

    def _geocode(self, city_name: str) -> tuple[float, float, str]:
        response = requests.get(
            GEOCODE_URL,
            params={"name": city_name, "count": 1, "language": "zh", "format": "json"},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        results = payload.get("results") or []
        if not results:
            raise ValueError(f"Could not find city: {city_name}")
        result = results[0]
        lat = result["latitude"]
        lon = result["longitude"]
        name = result.get("name", city_name)
        return lat, lon, name

    def fetch_today(
        self,
        city_name: str,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> DailyWeather:
        if latitude is not None and longitude is not None:
            lat, lon, resolved_city = latitude, longitude, city_name
        else:
            lat, lon, resolved_city = self._geocode(city_name)
        response = requests.get(
            FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": ",".join(
                    [
                        "temperature_2m_max",
                        "temperature_2m_min",
                        "apparent_temperature_max",
                        "apparent_temperature_min",
                        "precipitation_probability_max",
                        "wind_speed_10m_max",
                    ]
                ),
                "timezone": "auto",
                "forecast_days": 1,
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        daily = response.json()["daily"]
        return DailyWeather(
            city=resolved_city,
            date=daily["time"][0],
            temp_max=float(daily["temperature_2m_max"][0]),
            temp_min=float(daily["temperature_2m_min"][0]),
            apparent_temp_max=float(daily["apparent_temperature_max"][0]),
            apparent_temp_min=float(daily["apparent_temperature_min"][0]),
            precipitation_probability_max=int(daily["precipitation_probability_max"][0]),
            wind_speed_max=float(daily["wind_speed_10m_max"][0]),
        )
