from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from app.agent.context import CalendarEventContext, ScenarioContext, UserProfileContext
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


_ROUTE_REGEX = re.compile(
    r"z\s+(?P<origin>[A-Za-zÁ-ž\s]+?)\s+do\s+(?P<destination>[A-Za-zÁ-ž\s]+)", re.IGNORECASE
)


@dataclass
class AgentResult:
    text: str
    context: Dict[str, Any]


class AgentBrain:
    """Koordinátor, ktorý riadi viacero pod-agentov paralelne."""

    def __init__(self, tool_registry: ToolRegistry, sub_agents: Optional[List] = None) -> None:
        self.tool_registry = tool_registry
        self.sub_agents = sub_agents or [
            TravelPlannerAgent(tool_registry),
            WeatherAdvisorAgent(tool_registry),
            StopsAdvisorAgent(tool_registry),
        ]
        logger.info(
            "Koordinátor pripravený (%d pod-agentov, projekt %s)",
            len(self.sub_agents),
            APP_CONFIG.project_name,
        )

    async def process_request(self, request: QueryRequest) -> AgentResult:
        scenario = self._build_scenario(request)
        logger.info("Hlavný agent vyhodnocuje scenár: %s", scenario.describe())
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
                        summary="Agent narazil na chybu a odporúča manuálnu kontrolu.",
                        artifacts={},
                    )
                )
            else:
                normalized.append(result)
        return normalized

    def _compose_narrative(self, scenario: ScenarioContext, results: List[SubAgentResult]) -> str:
        lines = [
            f"Scenár: {scenario.describe()}",
            "",
        ]
        for result in results:
            lines.append(f"{result.agent}: {result.summary}")
        lines.append(
            "\nZhrnutie: všetky odporúčania sú mockované pre potreby hackathon kostry."
        )
        return "\n".join(lines)

    def _build_scenario(self, request: QueryRequest) -> ScenarioContext:
        origin, destination = self._parse_route(request)
        event_ctx = self._build_event_context(request.calendar_event)
        user_ctx = self._build_user_context(request.user_profile)
        if event_ctx and event_ctx.location:
            destination = event_ctx.location
        if user_ctx and user_ctx.home_city:
            origin = user_ctx.home_city
        return ScenarioContext(
            query=request.query,
            origin=origin or "Košice",
            destination=destination or "Bratislava",
            event=event_ctx,
            user_profile=user_ctx,
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

    def _build_user_context(self, profile: Optional[UserProfileInput]) -> Optional[UserProfileContext]:
        if not profile:
            return None
        return UserProfileContext(
            home_city=profile.home_city,
            interests=profile.interests,
            travel_style=profile.travel_style,
        )
