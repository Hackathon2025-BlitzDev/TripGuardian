from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException

from app.agent.brain import AgentBrain
from app.api.schemas import AgentContext, QueryRequest, QueryResponse, SubAgentReport
from app.config import APP_CONFIG
from app.logging_config import setup_logging
from app.services.tool_registry import ToolRegistry
from app.tools.definitions import TOOL_DEFINITIONS

setup_logging()
logger = logging.getLogger(__name__)

# Global singletons for the lightweight skeleton deployment.
tool_registry = ToolRegistry(TOOL_DEFINITIONS)
agent_brain = AgentBrain(tool_registry=tool_registry)

app = FastAPI(title=APP_CONFIG.project_name, version=APP_CONFIG.version)


@app.post("/agent/query", response_model=QueryResponse)
async def agent_query(payload: QueryRequest) -> QueryResponse:
    logger.info("Received agent query (%d chars)", len(payload.query))
    try:
        agent_result = await agent_brain.process_request(payload)
    except Exception as exc:  # pragma: no cover - FastAPI will handle logging
        logger.exception("Agent processing failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    context_model = AgentContext(
        mode=agent_result.context["mode"],
        scenario=agent_result.context["scenario"],
        sub_agents=[
            SubAgentReport(
                agent=report["agent"],
                summary=report["summary"],
                artifacts=report["artifacts"],
            )
            for report in agent_result.context["sub_agents"]
        ],
    )

    logger.info("Completed agent query using %s mode", context_model.mode)
    return QueryResponse(text=agent_result.text, context=context_model)


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    logger.debug("Healthcheck pinged")
    return {"status": "ok"}
