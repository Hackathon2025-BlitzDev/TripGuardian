from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict

from app.agent.context import ScenarioContext
from app.services.tool_registry import ToolExecutionResult, ToolRegistry

logger = logging.getLogger(__name__)


@dataclass
class SubAgentResult:
    agent: str
    summary: str
    artifacts: Dict[str, Any]


class BaseSubAgent:
    name: str = "BaseAgent"
    description: str = ""

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    async def run(self, context: ScenarioContext) -> SubAgentResult:
        raise NotImplementedError

    async def _call_tool(self, name: str, arguments: Dict[str, Any], rationale: str) -> ToolExecutionResult:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.registry.execute(name=name, arguments=arguments, rationale=rationale),
        )


class TravelPlannerAgent(BaseSubAgent):
    name = "TravelPlanner"
    description = "Plánuje dopravu a harmonogram cesty."

    async def run(self, context: ScenarioContext) -> SubAgentResult:
        logger.info("%s analyzuje trasu %s -> %s", self.name, context.origin, context.destination)
        route = await self._call_tool(
            "RoutePlannerTool",
            {
                "origin": context.origin,
                "destination": context.destination,
                "time_budget_minutes": 120,
            },
            "Vyhodnocujem najlepšiu trasu",
        )
        fuel = await self._call_tool(
            "FuelStationsTool",
            {
                "route_id": f"{context.origin}-{context.destination}",
                "energy_type": "petrol",
            },
            "Hľadám tankovanie",
        )

        summary = (
            f"Navrhnutá trasa má {route.output.get('distance_km')} km,"
            f" očakávaj {route.output.get('estimated_duration_minutes')} min jazdy."
        )
        summary += " Navrhol som aj praktické miesta na doplnenie paliva." if fuel.output else ""
        artifacts = {
            "route": route.output,
            "fuel": fuel.output,
        }
        return SubAgentResult(agent=self.name, summary=summary, artifacts=artifacts)


class WeatherAdvisorAgent(BaseSubAgent):
    name = "WeatherAdvisor"
    description = "Monitoruje počasie a odporúča oblečenie."

    async def run(self, context: ScenarioContext) -> SubAgentResult:
        logger.info("%s kontroluje počasie pre %s a %s", self.name, context.origin, context.destination)
        weather = await self._call_tool(
            "WeatherTool",
            {"waypoints": [context.origin, context.destination]},
            "Overujem predpoveď",
        )
        suggestions = self._build_clothing_tips(weather.output)
        summary = "Počítaj s podmienkami: " + ", ".join(
            f"{item['location']} {item['condition']}" for item in weather.output.get("forecast", [])
        )
        return SubAgentResult(
            agent=self.name,
            summary=summary + ". " + suggestions,
            artifacts={"forecast": weather.output, "tips": suggestions},
        )

    def _build_clothing_tips(self, weather_response: Dict[str, Any]) -> str:
        temps = [item.get("temp_c") for item in weather_response.get("forecast", []) if "temp_c" in item]
        if not temps:
            return "Bez špecifických odporúčaní."
        avg = sum(temps) / len(temps)
        if avg < 10:
            return "Zober si teplý kabát a rukavice."
        if avg < 18:
            return "Ľahká bunda bude istota, pribaľ dáždnik." 
        return "Stačí ľahké oblečenie, no sleduj prehánky."


class StopsAdvisorAgent(BaseSubAgent):
    name = "StopsAdvisor"
    description = "Navrhuje zastávky, jedlo a body záujmu."

    async def run(self, context: ScenarioContext) -> SubAgentResult:
        logger.info("%s hľadá zastávky na trase %s -> %s", self.name, context.origin, context.destination)
        poi = await self._call_tool(
            "POINearRouteTool",
            {
                "route_id": f"{context.origin}-{context.destination}",
                "max_detour_km": 25,
            },
            "Hľadám rýchle zaujímavosti",
        )
        places = await self._call_tool(
            "PlacesSearchTool",
            {
                "location": context.destination,
                "categories": ["food", "coffee", "culture"],
            },
            "Hľadám jedlo a kávu",
        )

        summary = "Tipy na cestu pripravené: "
        summary += f"{len(poi.output.get('suggestions', []))} zastávok a "
        summary += f"{len(places.output.get('places', []))} miest na jedlo."
        artifacts = {"poi": poi.output, "places": places.output}
        return SubAgentResult(agent=self.name, summary=summary, artifacts=artifacts)
