from __future__ import annotations

import logging
import logging
from dataclasses import dataclass
from typing import Any, Dict, List

from app.agent.context import ScenarioContext
from app.agent.results import AgentResult
from app.config import AGENT_CONFIG
from app.services.llm_client import get_openai_client
from app.services.planning import ResponseComposer, SimpleToolPlanner
from app.services.tool_registry import ToolExecutionResult, ToolRegistry

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


@dataclass
class AgentContextPayload:
    mode: str
    scenario: Dict[str, Any]
    sub_agents: List[Dict[str, Any]]


class TripPlannerAgent:
    """Drafts a route using lightweight heuristics + tool registry."""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.planner = SimpleToolPlanner(registry)
        self.composer = ResponseComposer()

    def run(self, scenario: ScenarioContext) -> AgentResult:
        plans = self.planner.plan(
            scenario.query,
            origin=scenario.origin,
            destination=scenario.destination,
            time_budget_minutes=scenario.time_budget_minutes,
            preferred_categories=scenario.preferences.get("categories") if scenario.preferences else None,
        )
        tool_results: List[ToolExecutionResult] = []
        for plan in plans:
            tool_results.append(
                self.registry.execute(plan.name, plan.arguments, rationale=plan.rationale)
            )
        text = self.composer.build_text(scenario.query, tool_results)
        decision = self._rank_with_llm(tool_results, scenario)
        if decision:
            text = text + "\n\nAI vyber trasy:\n" + decision
        ctx = AgentContextPayload(
            mode="planner",
            scenario={
                "origin": scenario.origin,
                "destination": scenario.destination,
                "event": scenario.event.title if scenario.event else None,
            },
            sub_agents=[
                {"agent": result.name, "summary": result.rationale, "artifacts": result.output}
                for result in tool_results
            ],
        )
        return AgentResult(text=text, context=ctx.__dict__)

    def _rank_with_llm(self, tool_results: List[ToolExecutionResult], scenario: ScenarioContext) -> str:
        """Ask LLM to pick the best variant and count POI time budget."""

        client = get_openai_client()
        legs = []
        for result in tool_results:
            if result.name == "RoutePlannerTool":
                legs = result.output.get("legs", [])
        places = []
        for result in tool_results:
            if result.name == "POINearRouteTool":
                places = result.output.get("suggestions", [])
        content = (
            "Vyhodnot pripraveny draft trasy. Vyber najlepsi variant pre pouzivatela a odhadni kolko zastavok/POI sa stihne.\n"
            f"Start: {scenario.origin} -> Ciel: {scenario.destination}\n"
            f"Legs: {legs}\n"
            f"POI navrhy: {places}\n"
            "Vrat 2-3 vety v slovenčine: (1) ktoru trasu by si zvolil a preco, (2) kolko zastavok odporucas stihnut."
        )
        try:
            completion = client.chat.completions.create(
                model=AGENT_CONFIG.model,
                messages=[
                    {"role": "system", "content": "Si TripGuardian, expert na trasy na Slovensku."},
                    {"role": "user", "content": content},
                ],
                temperature=AGENT_CONFIG.temperature,
                max_completion_tokens=300,
            )
            return completion.choices[0].message.content.strip()
        except Exception as exc:  # pragma: no cover - network guard
            logger.warning("LLM ranking failed: %s", exc)
            return ""


class CalendarWatcherAgent:
    """Evaluates calendar events and proposes a draft trip."""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def run(self, scenario: ScenarioContext) -> AgentResult:
        if not scenario.event:
            return AgentResult(
                text="Nebola dodana ziadna udalost v kalendari, nie je co planovat.",
                context={"mode": "calendar", "scenario": {}, "sub_agents": []},
            )

        origin = scenario.user_profile.home_city if scenario.user_profile and scenario.user_profile.home_city else scenario.origin
        destination = scenario.event.location or scenario.destination
        route = self.registry.execute(
            "RoutePlannerTool",
            {
                "origin": origin,
                "destination": destination,
                "time_budget_minutes": 120,
            },
            rationale="Skusam odhadnut vzdialenost a cas k udalosti z kalendara.",
        )

        needs_trip = (route.output or {}).get("distance_km", 0) and (route.output or {}).get("distance_km", 0) > 30
        text_lines = [
            f"Kalendár: {scenario.event.title} @ {scenario.event.location}",
            f"Odhad trasy {origin} -> {destination}: {route.output.get('distance_km')} km / {route.output.get('estimated_duration_minutes')} min.",
        ]
        if needs_trip:
            text_lines.append("Odporucam pripravit draft tripu a pridat zastavky.")
        else:
            text_lines.append("Udalost je blizko, staci kratke upozornenie, plny trip netreba.")

        ctx = AgentContextPayload(
            mode="calendar",
            scenario={"origin": origin, "destination": destination, "event": scenario.event.title},
            sub_agents=[{"agent": "RoutePlannerTool", "summary": route.rationale, "artifacts": route.output}],
        )
        return AgentResult(text="\n".join(text_lines), context=ctx.__dict__)


class LiveRouteAgent:
    """Monitors active trip, checks weather + timing, and suggests adjustments."""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def run(self, scenario: ScenarioContext) -> AgentResult:
        route_id = scenario.active_route_id or f"{scenario.origin}-{scenario.destination}"
        waypoints = [scenario.current_location or scenario.origin, scenario.destination]
        simulate_weather = None
        if any(keyword in scenario.query.lower() for keyword in ["rain", "dazd", "burka", "storm"]):
            simulate_weather = "storm" if any(k in scenario.query.lower() for k in ["burka", "storm"]) else "rain"

        weather = self.registry.execute(
            "WeatherTool",
            {
                "waypoints": waypoints,
                "simulate": simulate_weather,
            },
            rationale="Kontrolujem pocasie na dalsie useky.",
        )
        fuel = self.registry.execute(
            "FuelStationsTool",
            {"route_id": route_id, "energy_type": "petrol"},
            rationale="Hladam moznosti tankovania na trase.",
        )
        poi = self.registry.execute(
            "POINearRouteTool",
            {"route_id": route_id, "max_detour_km": 25},
            rationale="Hladam rychle zastavky, keby sa treba odklonit.",
        )

        delay = scenario.delay_minutes or 0
        suggestions = []
        if delay > 20:
            suggestions.append("Si vo vacsom meskani, zvaz skratit dalsiu zastavku.")
        if (weather.output or {}).get("forecast"):
            first = weather.output["forecast"][0]
            if first.get("condition") and "dazd" in first.get("condition", "").lower():
                suggestions.append("Prsi na trase, priprav si alternativu pod strechou.")

        text_lines = [
            f"Aktivny trip: {route_id}",
            f"Aktualna poloha: {scenario.current_location or 'nezadana'}; meskanie: {delay} min",
            f"Pocasie checkpointy: {weather.output.get('forecast')}",
            f"Tankovanie tipy: {fuel.output.get('stations', [])[:2]}",
            f"Rychle POI: {poi.output.get('suggestions', [])[:2]}",
        ]
        if suggestions:
            text_lines.append("Doporucenia: " + " ".join(suggestions))
        else:
            text_lines.append("Zatial ziadne zmeny netreba.")

        ai_summary = self._llm_live_summary(
            scenario=scenario,
            weather=weather.output or {},
            fuel=fuel.output or {},
            poi=poi.output or {},
            suggestions=suggestions,
        )
        response_text = ai_summary if ai_summary else "\n".join(text_lines)

        ctx = AgentContextPayload(
            mode="live",
            scenario={
                "origin": scenario.origin,
                "destination": scenario.destination,
                "route_id": route_id,
                "current_location": scenario.current_location,
            },
            sub_agents=[
                {"agent": "WeatherTool", "summary": weather.rationale, "artifacts": weather.output},
                {"agent": "FuelStationsTool", "summary": fuel.rationale, "artifacts": fuel.output},
                {"agent": "POINearRouteTool", "summary": poi.rationale, "artifacts": poi.output},
            ],
        )
        return AgentResult(text=response_text, context=ctx.__dict__)

    def _llm_live_summary(
        self,
        scenario: ScenarioContext,
        weather: Dict[str, Any],
        fuel: Dict[str, Any],
        poi: Dict[str, Any],
        suggestions: List[str],
    ) -> str:
        """Generate a JSON travel announcement for the current trip state."""

        client = get_openai_client()
        planned_stops = scenario.preferences.get("stops") if scenario.preferences else []
        content = (
            "Vygeneruj oznam pre cestovatela v live mode ako JSON string. "
            "Dodrz strukturu: {\"summary\": \"\", \"recommendation\": \"\", \"actions\": [\"...\"]}. "
            "Maj 2-3 vety v poliach, slovensky. Ak je burka/dazd, odporuc preskocit outdoor zastavky (hrad, vyhladka), navrhni alternativu pod strechou.\n"
            f"Trasa: {scenario.origin} -> {scenario.destination}, route_id={scenario.active_route_id or ''}\n"
            f"Aktualna poloha: {scenario.current_location or 'nezadana'}, meskanie: {scenario.delay_minutes} min\n"
            f"Pocasie: {weather.get('forecast')}\n"
            f"Stanice: {fuel.get('stations', [])[:3]}\n"
            f"POI: {poi.get('suggestions', [])[:3]}\n"
            f"Planovane zastavky: {planned_stops}\n"
            f"Predbezne doporucenia: {suggestions}"
        )
        try:
            completion = client.chat.completions.create(
                model=AGENT_CONFIG.model,
                messages=[
                    {"role": "system", "content": "Si TripGuardian, strucny live copilot. Bud konkretna a akcna."},
                    {"role": "user", "content": content},
                ],
                temperature=AGENT_CONFIG.temperature,
                max_completion_tokens=200,
            )
            return completion.choices[0].message.content.strip()
        except Exception as exc:  # pragma: no cover - network guard
            logger.warning("LLM live summary failed: %s", exc)
            return ""
