from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict


@dataclass
class CalendarEventContext:
    title: str
    location: str
    when: Optional[datetime] = None
    notes: Optional[str] = None


@dataclass
class UserProfileContext:
    home_city: Optional[str] = None
    interests: List[str] = field(default_factory=list)
    travel_style: Optional[str] = None


@dataclass
class ScenarioContext:
    query: str
    origin: str
    destination: str
    current_location: Optional[str] = None
    active_route_id: Optional[str] = None
    delay_minutes: int = 0
    time_budget_minutes: Optional[int] = None
    event: Optional[CalendarEventContext] = None
    user_profile: Optional[UserProfileContext] = None
    preferences: Dict[str, any] = field(default_factory=dict)

    def describe(self) -> str:
        event_part = f"Udalost: {self.event.title} v {self.event.location}" if self.event else "Bez udalosti"
        return f"{event_part}; trasa {self.origin} -> {self.destination}"
