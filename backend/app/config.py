import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Always try to load the shared root .env so running from backend/ still works.
load_dotenv(PROJECT_ROOT / ".env")
# Allow local overrides from the active working directory if needed.
load_dotenv()


@dataclass(frozen=True)
class AgentConfig:
    """Holds defaults for the OpenAI-powered agent."""

    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature: float = 0.3
    max_output_tokens: int = 5000
    organization: Optional[str] = os.getenv("OPENAI_ORG")


@dataclass(frozen=True)
class AppConfig:
    project_name: str = "TripGuardian Agent API"
    version: str = "0.1.0"


AGENT_CONFIG = AgentConfig()
APP_CONFIG = AppConfig()
