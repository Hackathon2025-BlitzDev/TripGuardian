from __future__ import annotations

import logging
from typing import Any, Dict, List

from shapely.geometry import LineString, Point

from app.services.route_cache import ROUTE_CACHE, RouteCacheEntry
from app.tools.definitions import POI_NEAR_ROUTE
from app.tools.route_planner_runner import RoutePlannerToolRunner
from route_planner.route_planer import haversine

logger = logging.getLogger(__name__)

_ROUTE_RUNNER = RoutePlannerToolRunner()


class POINearRouteToolRunner:
    def __call__(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        route_id = arguments.get("route_id")
        max_detour = float(arguments.get("max_detour_km", 25) or 25)
        entry = ROUTE_CACHE.get(route_id)
        if not entry:
            self._hydrate_cache(route_id)
            entry = ROUTE_CACHE.get(route_id)
        if not entry:
            logger.warning("POINearRouteToolRunner no cache for %s", route_id)
            return POI_NEAR_ROUTE.mock_response
        suggestions = self._build_suggestions(entry, max_detour)
        return {"suggestions": suggestions[:10]}

    def _build_suggestions(self, entry: RouteCacheEntry, max_detour: float) -> List[Dict[str, Any]]:
        routes = entry.raw.get("routes", [])
        if not routes:
            return POI_NEAR_ROUTE.mock_response["suggestions"]
        base_route = min(routes, key=lambda r: r.get("duration_min") or float("inf"))
        geometry = base_route.get("geometry") or []
        if len(geometry) < 2:
            return POI_NEAR_ROUTE.mock_response["suggestions"]
        line = LineString([(lon, lat) for lat, lon in geometry])
        poi_list = base_route.get("top_pois", [])
        suggestions: List[Dict[str, Any]] = []
        for poi in poi_list:
            loc = poi.get("location") or {}
            lat = loc.get("lat")
            lon = loc.get("lon")
            if lat is None or lon is None:
                continue
            point = Point(lon, lat)
            distance_deg = line.distance(point)
            distance_km = distance_deg * 111
            if distance_km > max_detour:
                continue
            detour = self._estimate_detour(entry, lat, lon)
            suggestions.append(
                {
                    "name": poi.get("name", "Unnamed"),
                    "detour_km": round(detour, 1),
                    "reason": poi.get("category", "point of interest"),
                    "location": loc,
                }
            )
        if not suggestions:
            return POI_NEAR_ROUTE.mock_response["suggestions"]
        return sorted(suggestions, key=lambda item: item.get("detour_km", 999))

    def _estimate_detour(self, entry: RouteCacheEntry, lat: float, lon: float) -> float:
        start = entry.raw.get("trip_summary", {}).get("start_coords")
        end = entry.raw.get("trip_summary", {}).get("end_coords")
        if not start or not end:
            return 0.0
        start_coord = (start.get("lon"), start.get("lat"))
        end_coord = (end.get("lon"), end.get("lat"))
        poi_coord = (lon, lat)
        direct = haversine(start_coord, end_coord)
        via = haversine(start_coord, poi_coord) + haversine(poi_coord, end_coord)
        return max(0.0, via - direct)

    def _hydrate_cache(self, route_id: str) -> None:
        parts = [part.strip() for part in route_id.replace(">", "-").split("-") if part.strip()]
        if len(parts) < 2:
            return
        origin, destination = parts[0], parts[-1]
        try:
            _ROUTE_RUNNER.run(origin, destination)
        except Exception as exc:  # pragma: no cover - network
            logger.warning("Failed to hydrate cache for %s: %s", route_id, exc)
