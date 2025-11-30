from __future__ import annotations

import logging
import re
from typing import List, Optional, Tuple

from .tool_registry import ToolExecutionResult, ToolPlan, ToolRegistry

_ROUTE_REGEX = re.compile(r"z\s+(?P<origin>[A-Za-zÁ-ž\s]+?)\s+do\s+(?P<destination>[A-Za-zÁ-ž\s]+)", re.IGNORECASE)

logger = logging.getLogger(__name__)


class SimpleToolPlanner:
    """Very small heuristic planner used until the true LLM reasoning is wired up."""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def plan(self, query: str) -> List[ToolPlan]:
        origin, destination = self._extract_route_pair(query)
        plans: List[ToolPlan] = []
        time_budget = 120 if "hod" in query.lower() else 45
        logger.info(
            "Building plan for query (origin=%s, destination=%s, time_budget=%d)",
            origin or "unknown",
            destination or "unknown",
            time_budget,
        )

        plan = ToolPlan(
            name="RoutePlannerTool",
            rationale="Potrebujem hrubý itinerár medzi bodmi trasy.",
            arguments={
                "origin": origin or "Košice",
                "destination": destination or "Bratislava",
                "time_budget_minutes": time_budget,
            },
        )
        plans.append(plan)
        logger.info("Agent plánuje použiť %s: %s", plan.name, plan.rationale)

        plan = ToolPlan(
            name="POINearRouteTool",
            rationale="Hľadám rýchle zaujímavosti v okolí hlavného ťahu.",
            arguments={
                "route_id": f"{origin or 'KE'}-{destination or 'BA'}",
                "max_detour_km": 20,
            },
        )
        plans.append(plan)
        logger.info("Agent plánuje použiť %s: %s", plan.name, plan.rationale)

        plan = ToolPlan(
            name="PlacesSearchTool",
            rationale="Vyberám konkrétne zastávky na jedlo a krátky oddych.",
            arguments={
                "location": destination or "Bratislava",
                "categories": ["food", "coffee", "culture"],
            },
        )
        plans.append(plan)
        logger.info("Agent plánuje použiť %s: %s", plan.name, plan.rationale)

        if any(keyword in query.lower() for keyword in ["počasie", "dážď", "rain"]):
            plan = ToolPlan(
                name="WeatherTool",
                rationale="Požiadavka spomína počasie, chcem preveriť úseky s rizikom dažďa.",
                arguments={"waypoints": [origin or "Košice", destination or "Bratislava"]},
            )
            plans.append(plan)
            logger.info("Agent plánuje použiť %s: %s", plan.name, plan.rationale)
        else:
            plan = ToolPlan(
                name="WeatherTool",
                rationale="Pred dlhšou cestou vždy kontrolujem predpoveď na trase.",
                arguments={"waypoints": [origin or "Košice", destination or "Bratislava"]},
            )
            plans.append(plan)
            logger.info("Agent plánuje použiť %s: %s", plan.name, plan.rationale)

        plan = ToolPlan(
            name="FuelStationsTool",
            rationale="Dopĺňam možnosti tankovania/ nabíjania v strede trasy.",
            arguments={"route_id": f"{origin or 'KE'}-{destination or 'BA'}", "energy_type": "petrol"},
        )
        plans.append(plan)
        logger.info("Agent plánuje použiť %s: %s", plan.name, plan.rationale)

        plan = ToolPlan(
            name="UserProfileTool",
            rationale="Personalizujem odporúčania podľa uložených preferencií.",
            arguments={"user_id": "demo-user"},
        )
        plans.append(plan)
        logger.info("Agent plánuje použiť %s: %s", plan.name, plan.rationale)

        plan = ToolPlan(
            name="TripSummaryTool",
            rationale="Na záver zhrniem hotovú trasu a poznámky.",
            arguments={
                "stops": [origin or "Košice", "Zvolen", destination or "Bratislava"],
                "notes": "Simulovaná verzia bez reálnych API volaní.",
            },
        )
        plans.append(plan)
        logger.info("Agent plánuje použiť %s: %s", plan.name, plan.rationale)

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
        tool_lines = [
            f"- {result.name}: {result.rationale or 'Simulovaný výstup'}" for result in tool_results
        ]

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
            f"- {item['name']} ({item['detour_km']} km zachádzka): {item['reason']}"
            for item in poi.get("suggestions", [])
        ]

        weather_lines = [
            f"- {item['location']}: {item['condition']} ({item['temp_c']} degC)"
            for item in weather.get("forecast", [])
        ]

        fuel_lines = [
            f"- {station['name']} - {', '.join(station['amenities'])} (~{station['eta_from_start_minutes']} min od štartu)"
            for station in fuel.get("stations", [])
        ]

        sections = [
            "Ako som uvažoval:",
            "\n".join(tool_lines) or "- Nenašli sa žiadne volania nástrojov.",
            "",
            "Návrh trasy:",
            "\n".join(legs_lines) or "- RoutePlannerTool zatiaľ nič nevrátil.",
            "",
            "Zastávky a jedlo:",
            "\n".join(place_lines or poi_lines) or "- Bez odporúčaní.",
            "",
            "Počasie na trase:",
            "\n".join(weather_lines) or "- Predpoveď nie je k dispozícii.",
            "",
            "Tankovanie / nabíjanie:",
            "\n".join(fuel_lines) or "- Bez tipov na stanice.",
            "",
            "Finálne odporúčanie:",
            "Kombinuj zastávku v regióne Zvolen/Banská Bystrica na oddych, potom pokračuj do cieľa."
            " Všetky údaje sú mockované, takže slúžia ako demonštrácia toku rozhodovania.",
        ]

        final_text = "\n".join(sections).strip()
        logger.debug("Response text length: %d chars", len(final_text))
        return final_text

    def _find_output(self, tool_results: List[ToolExecutionResult], tool_name: str):
        for result in tool_results:
            if result.name == tool_name:
                return result.output
        return None
