"""Fetch current temperature with Open-Meteo (no API key)."""

from __future__ import annotations

import httpx
from pydantic import BaseModel, Field


class WeatherParams(BaseModel):
    latitude: float = Field(..., description="WGS84 latitude")
    longitude: float = Field(..., description="WGS84 longitude")


def weather_current_c(params: WeatherParams) -> str:
    url = "https://api.open-meteo.com/v1/forecast"
    r = httpx.get(
        url,
        params={
            "latitude": params.latitude,
            "longitude": params.longitude,
            "current": "temperature_2m",
        },
        timeout=10.0,
    )
    r.raise_for_status()
    data = r.json()
    t = data.get("current", {}).get("temperature_2m")
    return f"Current temperature: {t} °C" if t is not None else "No temperature in response"


if __name__ == "__main__":
    print(weather_current_c(WeatherParams(latitude=52.52, longitude=13.41)))
