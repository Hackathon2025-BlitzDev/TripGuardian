from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from app.tools.definitions import TRIP_SUMMARY

logger = logging.getLogger(__name__)

LOG_DIR = Path(__file__).resolve().parents[2] / "data" / "trip_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


class TripSummaryToolRunner:
    def __call__(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        stops = arguments.get("stops") or []
        notes = arguments.get("notes", "")
        summary = self._build_summary(stops, notes)
        record = {
            "stops": stops,
            "notes": notes,
            "summary": summary,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        file_name = self._persist(record)
        return {"summary": summary, "artifact": file_name}

    def _build_summary(self, stops: List[str], notes: str) -> str:
        if not stops:
            return "Plan bol uložený, ale neboli poskytnuté žiadne zastávky."
        itinerary = " → ".join(stops)
        base = f"Plan obsahuje {len(stops)} bodov: {itinerary}."
        if notes:
            base += f" Poznámky: {notes}"
        return base

    def _persist(self, payload: Dict[str, Any]) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        file_path = LOG_DIR / f"trip_{timestamp}.json"
        try:
            with file_path.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
        except OSError as exc:
            logger.error("Failed to store trip summary: %s", exc)
            return ""
        return file_path.name
