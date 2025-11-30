from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import requests

from app.services.route_cache import ROUTE_CACHE, RouteCacheEntry
from app.tools.definitions import FUEL_STATIONS
from app.tools.route_planner_runner import RoutePlannerToolRunner
from route_planner.route_planer import haversine

logger = logging.getLogger(__name__)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
AMENITY_MAP = {
    "petrol": "fuel",
    "diesel": "fuel",
    "ev": "charging_station",
}
KNOWN_AMENITIES = ["shop", "toilets", "cafe", "restaurant", "car_wash", "charging"]

_ROUTE_RUNNER = RoutePlannerToolRunner()


class FuelStationsToolRunner:
    def __call__(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        route_id = arguments.get("route_id")
        energy = arguments.get("energy_type", "petrol")
        entry = ROUTE_CACHE.get(route_id)
        if not entry:
            self._hydrate_cache(route_id)
            entry = ROUTE_CACHE.get(route_id)
        if not entry:
            logger.warning("FuelStationsToolRunner missing cache for %s", route_id)
            return FUEL_STATIONS.mock_response
        stations = self._search(entry, energy)
        return {"stations": stations[:8]}

    def _search(self, entry: RouteCacheEntry, energy: str) -> List[Dict[str, Any]]:
        amenity = AMENITY_MAP.get(energy, "fuel")
        geometry = self._extract_geometry(entry)
        if not geometry:
            return FUEL_STATIONS.mock_response["stations"]
        bbox = self._bbox(geometry, padding=0.25)
        query = self._build_query(amenity, bbox)
        elements = self._fetch_overpass(query)
        if not elements:
            return FUEL_STATIONS.mock_response["stations"]
        summary = entry.raw.get("trip_summary", {})
        start = summary.get("start_coords")
        duration = entry.payload.get("estimated_duration_minutes") or 0
        distance = entry.payload.get("distance_km") or 1
        avg_speed = distance / (duration / 60) if duration else 80
        stations: List[Dict[str, Any]] = []
        for element in elements:
            lat, lon = self._extract_coords(element)
            if lat is None or lon is None:
                continue
            eta = self._estimate_eta(start, lat, lon, avg_speed)
            stations.append(
                {
                    "name": element.get("tags", {}).get("name", "Fuel stop"),
                    "amenities": self._collect_amenities(element.get("tags", {})),
                    "eta_from_start_minutes": int(eta),
                    "location": {"lat": lat, "lon": lon},
                }
            )
        return sorted(stations, key=lambda s: s.get("eta_from_start_minutes", 0))

    def _extract_geometry(self, entry: RouteCacheEntry) -> List[Tuple[float, float]]:
        routes = entry.raw.get("routes", [])
        if not routes:
            return []
        candidate = routes[0]
        return candidate.get("geometry") or []

    def _bbox(self, geometry: List[Tuple[float, float]], padding: float) -> Tuple[float, float, float, float]:
        lats = [lat for lat, _ in geometry]
        lons = [lon for _, lon in geometry]
        return (
            min(lats) - padding,
            min(lons) - padding,
            max(lats) + padding,
            max(lons) + padding,
        )

    def _build_query(self, amenity: str, bbox: Tuple[float, float, float, float]) -> str:
        south, west, north, east = bbox
        return (
            "[out:json][timeout:25];"
            "("
            f"  node[\"amenity\"=\"{amenity}\"]({south},{west},{north},{east});"
            f"  way[\"amenity\"=\"{amenity}\"]({south},{west},{north},{east});"
            ");"
            "out center 40;"
        )

    def _fetch_overpass(self, query: str) -> List[Dict[str, Any]]:
        try:
            response = requests.post(OVERPASS_URL, data=query.encode("utf-8"), timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("elements", [])
        except Exception as exc:  # pragma: no cover - network
            logger.warning("Overpass query failed: %s", exc)
            return []

    def _extract_coords(self, element: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
        if "lat" in element and "lon" in element:
            return element["lat"], element["lon"]
        center = element.get("center")
        if center:
            return center.get("lat"), center.get("lon")
        return None, None

    def _collect_amenities(self, tags: Dict[str, Any]) -> List[str]:
        found = []
        for key in KNOWN_AMENITIES:
            if key in tags:
                found.append(key)
        if tags.get("fuel:diesel") == "yes":
            found.append("diesel")
        if tags.get("fuel:octane_95") == "yes":
            found.append("95")
        if tags.get("fuel:charging") == "yes":
            found.append("charging")
        return found or ["basic"]

    def _estimate_eta(self, start: Dict[str, Any], lat: float, lon: float, avg_speed: float) -> float:
        if not start or start.get("lat") is None or start.get("lon") is None:
            return 0.0
        start_coord = (start.get("lon"), start.get("lat"))
        target = (lon, lat)
        distance = haversine(start_coord, target)
        hours = distance / max(avg_speed, 1)
        return hours * 60

    def _hydrate_cache(self, route_id: str) -> None:
        parts = [part.strip() for part in route_id.replace(">", "-").split("-") if part.strip()]
        if len(parts) < 2:
            return
        origin, destination = parts[0], parts[-1]
        try:
            _ROUTE_RUNNER.run(origin, destination)
        except Exception as exc:  # pragma: no cover - network
            logger.warning("Failed to hydrate route cache for %s: %s", route_id, exc)
