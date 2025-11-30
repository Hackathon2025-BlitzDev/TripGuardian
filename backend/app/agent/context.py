from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


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
    event: Optional[CalendarEventContext] = None
    user_profile: Optional[UserProfileContext] = None

    def describe(self) -> str:
        event_part = f"Udalosť: {self.event.title} v {self.event.location}" if self.event else "Bez udalosti"
        return f"{event_part}; trasa {self.origin} -> {self.destination}"
