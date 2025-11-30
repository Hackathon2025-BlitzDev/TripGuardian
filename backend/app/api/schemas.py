from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class CalendarEvent(BaseModel):
    title: str
    location: str
    datetime: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator("datetime", mode="before")
    @classmethod
    def _coerce_datetime(cls, value: Any) -> Optional[datetime]:
        if value in (None, ""):
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            normalized = value.replace("Z", "+00:00")
            try:
                return datetime.fromisoformat(normalized)
            except ValueError as exc:  # pragma: no cover - defensive guard
                raise ValueError("Neplatny format datumu v calendar_event.datetime") from exc
        raise ValueError("calendar_event.datetime musi byt datetime alebo ISO retazec")


class UserProfileInput(BaseModel):
    home_city: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    travel_style: Optional[str] = None


class TripPreferences(BaseModel):
    categories: List[str] = Field(default_factory=list)
    transport: Optional[str] = None
    budget: Optional[float] = None
    notes: Optional[str] = None

    @field_validator("budget", mode="before")
    @classmethod
    def _coerce_budget(cls, value: Any) -> Optional[float]:
        """Allow both numeric and string budgets; normalize to float."""
        if value in (None, ""):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.replace(",", "").strip()
            try:
                return float(cleaned)
            except ValueError as exc:  # pragma: no cover - defensive guard
                raise ValueError("budget musi byt cislo") from exc
        raise ValueError("budget musi byt cislo")

class StructuredTripInput(BaseModel):
    start: str
    destination: str
    stops: List[str] = Field(default_factory=list)
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    flexibleDates: bool = False
    preferences: Optional[TripPreferences] = None

    @field_validator("startDate", "endDate", mode="before")
    @classmethod
    def _coerce_datetime(cls, value: Any) -> Optional[datetime]:
        if value in (None, ""):
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            normalized = value.replace("Z", "+00:00")
            try:
                return datetime.fromisoformat(normalized)
            except ValueError as exc:
                raise ValueError("Neplatny format datumu v structured_trip startDate/endDate") from exc
        raise ValueError("structured_trip datetimes musia byt datetime alebo ISO retazce")


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Pouzivatelsky dopyt pre hlavneho agenta.")
    mode: Literal["planner", "calendar", "live", "multi"] = Field(
        "planner", description="Ktory agent sa ma spustit."
    )
    structured_trip: Optional["StructuredTripInput"] = Field(
        None, description="Strukturovany trip payload z frontendu (start/destination/stops/preferences)."
    )
    current_location: Optional[str] = Field(
        None, description="Volitelne: aktualna poloha pre live agenta."
    )
    active_route_id: Optional[str] = Field(
        None, description="Volitelne: identifikator aktivnej trasy pre live agenta."
    )
    delay_minutes: Optional[int] = Field(0, description="Volitelne: meskanie v minutach pre live agenta.")
    calendar_event: Optional["CalendarEvent"] = Field(
        None, description="Volitelna udalost z kalendara, ktora spusta planovanie.",
    )
    user_profile: Optional["UserProfileInput"] = Field(
        None, description="Zachytene preferencie pouzivatela.",
    )


class AgentContext(BaseModel):
    mode: str
    scenario: Dict[str, Any]
    sub_agents: List["SubAgentReport"]


class QueryResponse(BaseModel):
    text: str
    context: AgentContext


class SubAgentReport(BaseModel):
    agent: str
    summary: str
    artifacts: Dict[str, Any]
