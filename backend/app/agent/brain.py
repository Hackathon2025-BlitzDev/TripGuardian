from __future__ import annotations

import asyncio
import logging
import re
from typing import List, Optional, Tuple

from app.agent.agents import CalendarWatcherAgent, LiveRouteAgent, TripPlannerAgent
from app.agent.context import CalendarEventContext, ScenarioContext, UserProfileContext
from app.agent.results import AgentResult
from app.agent.sub_agents import (
    StopsAdvisorAgent,
    SubAgentResult,
    TravelPlannerAgent,
    WeatherAdvisorAgent,
)
from app.api.schemas import CalendarEvent, QueryRequest, UserProfileInput
from app.config import APP_CONFIG
from app.services.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

_ROUTE_REGEX = re.compile(r"z\s+(?P<origin>[A-Za-z\s]+?)\s+do\s+(?P<destination>[A-Za-z\s]+)", re.IGNORECASE)


class AgentBrain:
    """High level coordinator that can run dedicated agents or a legacy multi-agent demo."""

    def __init__(self, tool_registry: ToolRegistry, sub_agents: Optional[List] = None) -> None:
        self.tool_registry = tool_registry
        # Legacy skeleton agents used for the "multi" demo mode
        self.sub_agents = sub_agents or [
            TravelPlannerAgent(tool_registry),
            WeatherAdvisorAgent(tool_registry),
            StopsAdvisorAgent(tool_registry),
        ]
        # New focused agents aligned with the README
        self.trip_planner_agent = TripPlannerAgent(tool_registry)
        self.calendar_agent = CalendarWatcherAgent(tool_registry)
        self.live_agent = LiveRouteAgent(tool_registry)
        logger.info(
            "Koordinator pripraveny (%d pod-agentov, projekt %s)",
            len(self.sub_agents),
            APP_CONFIG.project_name,
        )

    async def process_request(self, request: QueryRequest) -> AgentResult:
        scenario = self._build_scenario(request)
        mode = (request.mode or "planner").lower()
        logger.info("Agent mode=%s, scenario=%s", mode, scenario.describe())

        if mode == "planner":
            return self.trip_planner_agent.run(scenario)
        if mode == "calendar":
            return self.calendar_agent.run(scenario)
        if mode == "live":
            return self.live_agent.run(scenario)

        # fallback to legacy multi-agent demo
        sub_results = await self._run_sub_agents(scenario)
        final_text = self._compose_narrative(scenario, sub_results)
        context_payload = {
            "mode": "multi-agent",
            "scenario": {
                "origin": scenario.origin,
                "destination": scenario.destination,
                "event": scenario.event.title if scenario.event else None,
                "event_time": scenario.event.when.isoformat() if scenario.event and scenario.event.when else None,
            },
            "sub_agents": [
                {"agent": result.agent, "summary": result.summary, "artifacts": result.artifacts}
                for result in sub_results
            ],
        }
        return AgentResult(text=final_text, context=context_payload)

    async def _run_sub_agents(self, scenario: ScenarioContext) -> List[SubAgentResult]:
        tasks = [agent.run(scenario) for agent in self.sub_agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        normalized: List[SubAgentResult] = []
        for agent, result in zip(self.sub_agents, results):
            if isinstance(result, Exception):
                logger.exception("Pod-agent %s zlyhal", agent.name, exc_info=result)
                normalized.append(
                    SubAgentResult(
                        agent=agent.name,
                        summary="Agent narazil na chybu a odporuca manualnu kontrolu.",
                        artifacts={},
                    )
                )
            else:
                normalized.append(result)
        return normalized

    def _compose_narrative(self, scenario: ScenarioContext, results: List[SubAgentResult]) -> str:
        lines = [
            f"Scenar: {scenario.describe()}",
            "",
        ]
        for result in results:
            lines.append(f"{result.agent}: {result.summary}")
        lines.append("\nZhrnutie: vsetky odporucania su mocky pre potreby hackathon kostry.")
        return "\n".join(lines)

    def _build_scenario(self, request: QueryRequest) -> ScenarioContext:
        origin, destination = self._parse_route(request)
        time_budget = None
        preferences: dict = {}
        if request.structured_trip:
            origin = request.structured_trip.start
            destination = request.structured_trip.destination
            preferences = {
                "categories": (request.structured_trip.preferences.categories if request.structured_trip.preferences else []),
                "transport": request.structured_trip.preferences.transport if request.structured_trip and request.structured_trip.preferences else None,
                "budget": request.structured_trip.preferences.budget if request.structured_trip and request.structured_trip.preferences else None,
                "notes": request.structured_trip.preferences.notes if request.structured_trip and request.structured_trip.preferences else None,
                "stops": request.structured_trip.stops,
            }
            if request.structured_trip.startDate and request.structured_trip.endDate:
                delta = request.structured_trip.endDate - request.structured_trip.startDate
                if delta.total_seconds() > 0:
                    time_budget = int(delta.total_seconds() // 60)

        event_ctx = self._build_event_context(request.calendar_event)
        user_ctx = self._build_user_context(request.user_profile, preferences)
        if event_ctx and event_ctx.location:
            destination = event_ctx.location
        if user_ctx and user_ctx.home_city:
            origin = user_ctx.home_city
        return ScenarioContext(
            query=request.query,
            origin=origin or "Kosice",
            destination=destination or "Bratislava",
            current_location=request.current_location,
            active_route_id=request.active_route_id,
            delay_minutes=request.delay_minutes or 0,
            time_budget_minutes=time_budget,
            event=event_ctx,
            user_profile=user_ctx,
            preferences=preferences,
        )

    def _parse_route(self, request: QueryRequest) -> Tuple[Optional[str], Optional[str]]:
        match = _ROUTE_REGEX.search(request.query)
        if not match:
            return None, None
        return match.group("origin").strip().title(), match.group("destination").strip().title()

    def _build_event_context(self, event: Optional[CalendarEvent]) -> Optional[CalendarEventContext]:
        if not event:
            return None
        return CalendarEventContext(
            title=event.title,
            location=event.location,
            when=event.datetime,
            notes=event.notes,
        )

    def _build_user_context(self, profile: Optional[UserProfileInput], preferences: Optional[dict] = None) -> Optional[UserProfileContext]:
        if not profile:
            if preferences:
                return UserProfileContext(
                    home_city=preferences.get("home_city"),
                    interests=preferences.get("categories", []),
                    travel_style=preferences.get("transport"),
                )
            return None
        return UserProfileContext(
            home_city=profile.home_city,
            interests=profile.interests,
            travel_style=profile.travel_style,
        )
