from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

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
                raise ValueError("Neplatný formát dátumu v calendar_event.datetime") from exc
        raise ValueError("calendar_event.datetime musí byť datetime alebo ISO reťazec")


class UserProfileInput(BaseModel):
    home_city: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    travel_style: Optional[str] = None


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Používateľský dopyt pre hlavného agenta.")
    calendar_event: Optional["CalendarEvent"] = Field(
        None, description="Voliteľná udalosť z kalendára, ktorá spúšťa plánovanie.",
    )
    user_profile: Optional["UserProfileInput"] = Field(
        None, description="Zachytené preferencie používateľa.",
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
