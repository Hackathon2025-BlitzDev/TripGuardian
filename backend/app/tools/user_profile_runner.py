from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

from app.tools.definitions import USER_PROFILE

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "user_profiles.json"


class UserProfileToolRunner:
    def __call__(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        user_id = arguments.get("user_id") or "demo-user"
        profile = self._load_profiles().get(user_id)
        if not profile:
            logger.info("Profile %s not found, returning default", user_id)
            return USER_PROFILE.mock_response
        return {"preferences": profile}

    def _load_profiles(self) -> Dict[str, Any]:
        if not DATA_FILE.exists():
            logger.warning("User profile file missing at %s", DATA_FILE)
            return {}
        try:
            with DATA_FILE.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse user profile file: %s", exc)
            return {}
