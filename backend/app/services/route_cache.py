from __future__ import annotations

import threading
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class RouteCacheEntry:
    """Stores both summarized and raw planner outputs for reuse by other tools."""

    origin: str
    destination: str
    payload: Dict[str, Any]
    raw: Dict[str, Any]


class RouteCache:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._data: Dict[str, RouteCacheEntry] = {}

    def store(
        self,
        origin: str,
        destination: str,
        payload: Dict[str, Any],
        raw: Dict[str, Any],
        alias: Optional[str] = None,
    ) -> None:
        key = self._build_key(origin, destination)
        entry = RouteCacheEntry(origin=origin, destination=destination, payload=payload, raw=raw)
        with self._lock:
            self._data[key] = entry
            if alias:
                self._data[self._normalize(alias)] = entry

    def get(self, identifier: Optional[str]) -> Optional[RouteCacheEntry]:
        if not identifier:
            return None
        normalized = self._normalize(identifier)
        with self._lock:
            entry = self._data.get(normalized)
            if entry:
                return entry

        if "-" in identifier or ">" in identifier:
            parts = [p for p in self._split(identifier) if p]
            if len(parts) >= 2:
                key = self._build_key(parts[0], parts[-1])
                with self._lock:
                    return self._data.get(key)
        return None

    def _split(self, identifier: str) -> list[str]:
        separators = "->|/\\"
        temp = identifier
        for sep in separators:
            temp = temp.replace(sep, "-")
        return temp.split("-")

    def _normalize(self, text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text)
        ascii_only = "".join(ch for ch in normalized if not unicodedata.combining(ch))
        return "".join(ch for ch in ascii_only.lower() if ch.isalnum())

    def _build_key(self, origin: str, destination: str) -> str:
        return f"{self._normalize(origin)}__{self._normalize(destination)}"


ROUTE_CACHE = RouteCache()
