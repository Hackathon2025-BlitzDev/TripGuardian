from __future__ import annotations

import logging
import os
from copy import deepcopy
from typing import Any, Dict, List, Optional

from app.services.route_cache import ROUTE_CACHE
from app.tools.definitions import ROUTE_PLANNER
from route_planner.route_planer import plan_trip

logger = logging.getLogger(__name__)


class RoutePlannerToolRunner:
    """Executes the legacy route planner script and normalizes its output."""

    def __init__(self, poi_categories: Optional[List[str]] = None) -> None:
        self._poi_categories = poi_categories or [
            "attractions",
            "dining",
            "accommodation",
            "services",
            "nature",
        ]
        self._fallback_payload = deepcopy(ROUTE_PLANNER.mock_response)

    def __call__(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return self.run(
            origin=arguments.get("origin", "Kosice"),
            destination=arguments.get("destination", "Bratislava"),
            time_budget_minutes=arguments.get("time_budget_minutes"),
        )

    def run(self, origin: str, destination: str, time_budget_minutes: Optional[int] = None) -> Dict[str, Any]:
        logger.info("RoutePlannerTool -> %s → %s", origin, destination)
        try:
            api_key = self._resolve_api_key()
            raw_result = plan_trip(
                start=origin,
                end=destination,
                auto_discover_routes=True,
                poi_categories=self._poi_categories,
                api_key=api_key,
            )
            if not raw_result.get("routes"):
                raise ValueError("Planner did not return any candidates")
            best_route = min(
                raw_result["routes"],
                key=lambda route: route.get("duration_min") or float("inf"),
            )
            legs = self._build_legs(raw_result["routes"], origin, destination, time_budget_minutes)
            payload = {
                "distance_km": best_route.get("distance_km"),
                "estimated_duration_minutes": best_route.get("duration_min"),
                "legs": legs,
                "poi_highlights": [
                    poi.get("name") for poi in best_route.get("top_pois", [])[:5]
                ],
                "recommendations": raw_result.get("recommendations", {}),
                "metadata": raw_result.get("trip_summary", {}),
            }
            ROUTE_CACHE.store(
                origin=origin,
                destination=destination,
                payload=payload,
                raw=raw_result,
                alias=f"{origin}-{destination}",
            )
            return payload
        except Exception as exc:  # pragma: no cover - guarded network code
            logger.exception("Route planner execution failed: %s", exc)
            fallback = deepcopy(self._fallback_payload)
            fallback["error"] = str(exc)
            fallback["origin"] = origin
            fallback["destination"] = destination
            return fallback

    def _resolve_api_key(self) -> Optional[str]:
        return (
            os.getenv("GOOGLE_PLACES_API_KEY")
            or os.getenv("GOOGLE_MAPS_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )

    def _build_legs(
        self,
        routes: List[Dict[str, Any]],
        origin: str,
        destination: str,
        time_budget_minutes: Optional[int],
    ) -> List[Dict[str, Any]]:
        legs: List[Dict[str, Any]] = []
        for route in sorted(routes, key=lambda r: r.get("duration_min") or float("inf"))[:3]:
            poi_hint = self._format_poi_hint(route.get("poi_summary", {}).get("categories", {}))
            instruction = f"Variant '{route.get('name', 'Trasa')}' ~{route.get('duration_min')} min"
            if time_budget_minutes:
                instruction += f" (limit {time_budget_minutes} min)"
            if poi_hint:
                instruction += f" – {poi_hint}"
            legs.append(
                {
                    "from": origin,
                    "to": destination,
                    "distance_km": route.get("distance_km"),
                    "instructions": instruction,
                    "waypoints": [
                        {"lat": wp[1], "lon": wp[0]} for wp in route.get("waypoints") or []
                    ],
                }
            )
        return legs or deepcopy(self._fallback_payload["legs"])

    def _format_poi_hint(self, categories: Dict[str, Dict[str, Any]]) -> str:
        if not categories:
            return ""
        ranked = sorted(
            categories.items(),
            key=lambda item: item[1].get("count", 0),
            reverse=True,
        )
        pieces = []
        for name, meta in ranked[:2]:
            count = meta.get("count", 0)
            top = meta.get("top_rated")
            if count and top:
                pieces.append(f"{name}: {count} tipov (napr. {top})")
            elif count:
                pieces.append(f"{name}: {count} tipov")
            elif top:
                pieces.append(f"Top {name}: {top}")
        return ", ".join(pieces)
