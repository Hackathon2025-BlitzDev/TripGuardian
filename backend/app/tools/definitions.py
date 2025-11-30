from __future__ import annotations

from typing import List

from .base import ToolDefinition

ROUTE_PLANNER = ToolDefinition(
    name="RoutePlannerTool",
    description=(
        "Analyzes the requested journey between two points and produces a staged route "
        "with timing estimates and navigation hints for each leg."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "origin": {"type": "string", "description": "Starting city or coordinates."},
            "destination": {"type": "string", "description": "Target city or coordinates."},
            "time_budget_minutes": {
                "type": "integer",
                "description": "Optional flexible time that can be spent on detours or stops.",
            },
        },
        "required": ["origin", "destination"],
    },
    mock_response={"distance_km": None, "estimated_duration_minutes": None, "legs": []},
)

PLACES_SEARCH = ToolDefinition(
    name="PlacesSearchTool",
    description="Finds noteworthy attractions, cafes, and meal spots around a waypoint or city.",
    input_schema={
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City or waypoint name."},
            "categories": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Types of locations to look for (cafes, nature, culture, etc.).",
            },
        },
        "required": ["location"],
    },
    mock_response={"places": []},
)

POI_NEAR_ROUTE = ToolDefinition(
    name="POINearRouteTool",
    description="Suggests quick points of interest close to the currently planned route.",
    input_schema={
        "type": "object",
        "properties": {
            "route_id": {
                "type": "string",
                "description": "Identifier of the active route (mock-only placeholder).",
            },
            "max_detour_km": {
                "type": "number",
                "description": "How far from the main corridor the user is willing to go.",
            },
        },
        "required": ["route_id"],
    },
    mock_response={"suggestions": []},
)

FUEL_STATIONS = ToolDefinition(
    name="FuelStationsTool",
    description="Lists convenient fuel or EV charging stops along the corridor.",
    input_schema={
        "type": "object",
        "properties": {
            "route_id": {"type": "string"},
            "energy_type": {
                "type": "string",
                "enum": ["petrol", "diesel", "ev"],
                "description": "Preferred fueling energy type.",
            },
        },
        "required": ["route_id", "energy_type"],
    },
    mock_response={"stations": []},
)

WEATHER = ToolDefinition(
    name="WeatherTool",
    description="Provides forecast for the next 6 hours along specified waypoints.",
    input_schema={
        "type": "object",
        "properties": {
            "waypoints": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Ordered list of city names or coordinates to check.",
            }
        },
        "required": ["waypoints"],
    },
    mock_response={"forecast": []},
)

USER_PROFILE = ToolDefinition(
    name="UserProfileTool",
    description="Retrieves stored preference snapshot for personalization.",
    input_schema={
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "Internal user identifier."}
        },
        "required": ["user_id"],
    },
    mock_response={"preferences": {}},
)

TRIP_SUMMARY = ToolDefinition(
    name="TripSummaryTool",
    description="Aggregates the final plan into a shareable summary payload.",
    input_schema={
        "type": "object",
        "properties": {
            "stops": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Ordered list of confirmed stops.",
            },
            "notes": {"type": "string"},
        },
        "required": ["stops"],
    },
    mock_response={"summary": ""},
)


TOOL_DEFINITIONS: List[ToolDefinition] = [
    ROUTE_PLANNER,
    PLACES_SEARCH,
    POI_NEAR_ROUTE,
    FUEL_STATIONS,
    WEATHER,
    USER_PROFILE,
    TRIP_SUMMARY,
]
