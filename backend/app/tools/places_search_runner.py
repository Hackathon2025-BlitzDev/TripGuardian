from __future__ import annotations

import logging
import os
from copy import deepcopy
from typing import Any, Dict, List, Optional

import requests

from app.tools.definitions import PLACES_SEARCH
from route_planner.route_planer import geocode

logger = logging.getLogger(__name__)

PLACES_TEXT_SEARCH = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.location,places.types"


class PlacesSearchToolRunner:
    def __init__(self, max_per_category: int = 4) -> None:
        self._max_per_category = max_per_category
        self._fallback = deepcopy(PLACES_SEARCH.mock_response)

    def __call__(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        location = arguments.get("location")
        if not location:
            raise ValueError("location is required")
        categories = arguments.get("categories") or ["food", "coffee", "culture"]
        return self.search(location, categories)

    def search(self, location: str, categories: List[str]) -> Dict[str, Any]:
        api_key = self._resolve_api_key()
        if not api_key:
            logger.warning("PlacesSearchToolRunner missing API key, returning fallback")
            fallback = deepcopy(self._fallback)
            fallback["warning"] = "GOOGLE_PLACES_API_KEY not configured"
            return fallback

        bias = self._geocode_safely(location)
        results: List[Dict[str, Any]] = []
        for category in categories:
            query = f"{category} in {location}"
            places = self._text_search(api_key, query, bias)
            for place in places[: self._max_per_category]:
                results.append(self._format_place(place, category))
        results.sort(key=lambda item: item.get("rating", 0), reverse=True)
        return {"places": results[: 3 * self._max_per_category]}

    def _geocode_safely(self, location: str) -> Optional[Dict[str, float]]:
        try:
            lon, lat = geocode(location)
            return {"latitude": lat, "longitude": lon}
        except Exception:
            return None

    def _text_search(
        self,
        api_key: str,
        query: str,
        bias: Optional[Dict[str, float]],
    ) -> List[Dict[str, Any]]:
        headers = {
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": FIELD_MASK,
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {"textQuery": query, "maxResultCount": self._max_per_category}
        if bias:
            payload["locationBias"] = {"circle": {"center": bias, "radius": 20000}}
        try:
            response = requests.post(PLACES_TEXT_SEARCH, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get("places", [])
        except Exception as exc:  # pragma: no cover - network
            logger.warning("Places text search failed for query '%s': %s", query, exc)
            return []

    def _format_place(self, place: Dict[str, Any], category: str) -> Dict[str, Any]:
        rating = place.get("rating")
        reviews = place.get("userRatingCount")
        highlight_parts = [place.get("formattedAddress", "").strip()]
        if rating:
            score = f"{rating:.1f}/5"
            if reviews:
                score += f" ({reviews} hodnotení)"
            highlight_parts.append(score)
        highlight = " · ".join(part for part in highlight_parts if part)
        return {
            "name": place.get("displayName", {}).get("text", "Unnamed"),
            "category": category,
            "highlight": highlight or "Bez detailov",
            "rating": rating,
            "location": place.get("location", {}),
            "types": place.get("types", []),
        }

    def _resolve_api_key(self) -> Optional[str]:
        return (
            os.getenv("GOOGLE_PLACES_API_KEY")
            or os.getenv("GOOGLE_MAPS_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )
