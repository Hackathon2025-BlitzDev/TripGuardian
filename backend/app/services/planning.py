from __future__ import annotations

import logging
import re
from typing import List, Optional, Tuple

from .tool_registry import ToolExecutionResult, ToolPlan, ToolRegistry

_ROUTE_REGEX = re.compile(r"z\s+(?P<origin>[A-Za-z\s]+?)\s+do\s+(?P<destination>[A-Za-z\s]+)", re.IGNORECASE)

logger = logging.getLogger(__name__)


class SimpleToolPlanner:
    """Very small heuristic planner used until the true LLM reasoning is wired up."""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def plan(
        self,
        query: str,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        time_budget_minutes: Optional[int] = None,
        preferred_categories: Optional[List[str]] = None,
    ) -> List[ToolPlan]:
        parsed_origin, parsed_destination = self._extract_route_pair(query)
        origin = origin or parsed_origin
        destination = destination or parsed_destination
        plans: List[ToolPlan] = []
        time_budget = time_budget_minutes if time_budget_minutes else (120 if "hod" in query.lower() else 45)
        logger.info(
            "Building plan for query (origin=%s, destination=%s, time_budget=%d)",
            origin or "unknown",
            destination or "unknown",
            time_budget,
        )

        plans.append(
            ToolPlan(
                name="RoutePlannerTool",
                rationale="Potrebujem hruby itinerar medzi bodmi trasy.",
                arguments={
                    "origin": origin or "Kosice",
                    "destination": destination or "Bratislava",
                    "time_budget_minutes": time_budget,
                },
            )
        )

        plans.append(
            ToolPlan(
                name="POINearRouteTool",
                rationale="Hladam rychle zaujimavosti v okoli hlavneho tahu.",
                arguments={
                    "route_id": f"{origin or 'KE'}-{destination or 'BA'}",
                    "max_detour_km": 20,
                },
            )
        )

        plans.append(
            ToolPlan(
                name="PlacesSearchTool",
                rationale="Vyberam konkretne zastavky na jedlo a kratky oddych.",
                arguments={
                    "location": destination or "Bratislava",
                    "categories": preferred_categories or ["food", "coffee", "culture"],
                },
            )
        )

        plans.append(
            ToolPlan(
                name="WeatherTool",
                rationale="Pred dlhsou cestou vzdy kontrolujem predpoved na trase.",
                arguments={"waypoints": [origin or "Kosice", destination or "Bratislava"]},
            )
        )

        plans.append(
            ToolPlan(
                name="FuelStationsTool",
                rationale="Doplnam moznosti tankovania/ nabijania v strede trasy.",
                arguments={"route_id": f"{origin or 'KE'}-{destination or 'BA'}", "energy_type": "petrol"},
            )
        )

        plans.append(
            ToolPlan(
                name="UserProfileTool",
                rationale="Personalizujem odporucania podla ulozenych preferencii.",
                arguments={"user_id": "demo-user"},
            )
        )

        plans.append(
            ToolPlan(
                name="TripSummaryTool",
                rationale="Na zaver zhrniem hotovy plan a poznamky.",
                arguments={
                    "stops": [origin or "Kosice", destination or "Bratislava"],
                    "notes": "Simulovana verzia bez realnych API volani.",
                },
            )
        )

        logger.debug("Planner produced %d tool invocations", len(plans))
        return plans

    def _extract_route_pair(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        match = _ROUTE_REGEX.search(query)
        if not match:
            logger.debug("No explicit origin/destination detected in query")
            return None, None
        origin = match.group("origin").strip().title()
        destination = match.group("destination").strip().title()
        logger.debug("Extracted route pair %s -> %s", origin, destination)
        return origin, destination


class ResponseComposer:
    """Builds the human-friendly answer from executed tool outputs."""

    def build_text(self, query: str, tool_results: List[ToolExecutionResult]) -> str:
        logger.info("Composing response from %d tool results", len(tool_results))
        tool_lines = [f"- {result.name}: {result.rationale or 'Simulovany vystup'}" for result in tool_results]

        route = self._find_output(tool_results, "RoutePlannerTool") or {}
        places = self._find_output(tool_results, "PlacesSearchTool") or {}
        poi = self._find_output(tool_results, "POINearRouteTool") or {}
        weather = self._find_output(tool_results, "WeatherTool") or {}
        fuel = self._find_output(tool_results, "FuelStationsTool") or {}

        legs_lines = []
        for leg in route.get("legs", []):
            legs_lines.append(
                f"- {leg['from']} -> {leg['to']} ({leg['distance_km']} km): {leg['instructions']}"
            )

        place_lines = [
            f"- {place['name']} ({place['category']}): {place['highlight']}"
            for place in places.get("places", [])
        ]

        poi_lines = [
            f"- {item['name']} ({item['detour_km']} km zachadzka): {item['reason']}"
            for item in poi.get("suggestions", [])
        ]

        weather_lines = [
            f"- {item['location']}: {item['condition']} ({item['temp_c']} degC)"
            for item in weather.get("forecast", [])
        ]

        fuel_lines = [
            f"- {station['name']} - {', '.join(station['amenities'])} (~{station['eta_from_start_minutes']} min od startu)"
            for station in fuel.get("stations", [])
        ]

        sections = [
            "Ako som uvazoval:",
            "\n".join(tool_lines) or "- Nenasli sa ziadne volania nastrojov.",
            "",
            "Navrh trasy:",
            "\n".join(legs_lines) or "- RoutePlannerTool zatial nic nevratil.",
            "",
            "Zastavky a jedlo:",
            "\n".join(place_lines or poi_lines) or "- Bez odporucani.",
            "",
            "Pocasie na trase:",
            "\n".join(weather_lines) or "- Predpoved nie je k dispozicii.",
            "",
            "Tankovanie / nabijanie:",
            "\n".join(fuel_lines) or "- Bez tipov na stanice.",
            "",
            "Finalne odporucanie:",
            "Kombinuj zastavku v regione stredneho Slovenska na oddych, potom pokracuj do ciela."
            " Vsetky udaje su mockovane, sluzia ako demonstracia toku rozhodovania.",
        ]

        final_text = "\n".join(sections).strip()
        logger.debug("Response text length: %d chars", len(final_text))
        return final_text

    def _find_output(self, tool_results: List[ToolExecutionResult], tool_name: str):
        for result in tool_results:
            if result.name == tool_name:
                return result.output
        return None
