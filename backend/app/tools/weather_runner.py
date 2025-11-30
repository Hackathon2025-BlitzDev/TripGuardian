from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests

from app.tools.definitions import WEATHER
from route_planner.route_planer import geocode

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_CODES = {
    0: "jasno",
    1: "takmer jasno",
    2: "polooblačno",
    3: "zamračené",
    45: "hmla",
    48: "hmla s námrazou",
    51: "mrholenie",
    61: "mierny dážď",
    63: "dážď",
    65: "silný dážď",
    71: "sneženie",
    80: "prehánky",
    81: "silné prehánky",
    82: "búrlivý dážď",
}


class WeatherToolRunner:
    def __call__(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        waypoints = arguments.get("waypoints") or []
        if not waypoints:
            return WEATHER.mock_response
        forecast = []
        for waypoint in waypoints:
            entry = self._forecast_for_location(waypoint)
            if entry:
                forecast.append(entry)
        return {"forecast": forecast or WEATHER.mock_response["forecast"]}

    def _forecast_for_location(self, location: str) -> Optional[Dict[str, Any]]:
        try:
            lon, lat = geocode(location)
        except Exception as exc:
            logger.warning("WeatherToolRunner geocode failed for %s: %s", location, exc)
            return None
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,precipitation_probability,weathercode",
            "timezone": "auto",
        }
        try:
            response = requests.get(OPEN_METEO_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
        except Exception as exc:  # pragma: no cover - network
            logger.warning("Weather API failed for %s: %s", location, exc)
            return None

        return self._parse_forecast(location, data)

    def _parse_forecast(self, location: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        hourly = data.get("hourly") or {}
        times = hourly.get("time") or []
        temps = hourly.get("temperature_2m") or []
        precip = hourly.get("precipitation_probability") or []
        codes = hourly.get("weathercode") or []
        if not times:
            return None
        now = datetime.now(timezone.utc)
        horizon = now + timedelta(hours=6)
        best_idx = 0
        for idx, timestamp in enumerate(times):
            try:
                slot = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                continue
            if now <= slot <= horizon:
                best_idx = idx
                break
        temp = temps[best_idx] if best_idx < len(temps) else temps[0]
        code = codes[best_idx] if best_idx < len(codes) else codes[0]
        precip_val = precip[best_idx] if best_idx < len(precip) else None
        condition = WEATHER_CODES.get(code, "neurčitá situácia")
        return {
            "location": location,
            "condition": condition,
            "temp_c": round(temp, 1) if temp is not None else None,
            "precip_probability": precip_val,
        }
