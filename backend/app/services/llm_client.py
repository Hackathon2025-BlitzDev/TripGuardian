from __future__ import annotations

import logging
from functools import lru_cache

from openai import OpenAI

from app.config import AGENT_CONFIG

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    """Create a singleton OpenAI client using env credentials."""

    logger.info("Initializing OpenAI client for model %s", AGENT_CONFIG.model)
    return OpenAI(organization=AGENT_CONFIG.organization)
