# TripGuardian backend (agents)

Short overview of what the backend agents do and how to run them locally.

## What the agent can do
- `/agent/query` drives the main `AgentBrain` with three modes:
  - `planner`: builds a draft route and nearby POI suggestions (RoutePlannerTool + POINearRouteTool).
  - `calendar`: evaluates a calendar event and proposes a draft trip.
  - `live`: tracks an active trip, checks weather, fuel stops, nearby POI and returns recommendations.
- Input accepts `structured_trip` (start, destination, stops, preferences including budget), `current_location`, `active_route_id`, `delay_minutes`, and optional `calendar_event` / `user_profile`.
- `/health` returns a simple status JSON.

## Quick start
1) `cd backend`
2) `pip install -r requirements.txt`
3) Set keys (at least OpenAI + Google Places), e.g. in PowerShell:
   ```powershell
   $env:OPENAI_API_KEY="sk-..."
   $env:OPENAI_MODEL="gpt-5.1"
   $env:GOOGLE_PLACES_API_KEY="<your_places_key>"
   ```
4) Run the server:
   ```powershell
   python main.py
   ```
5) Smoke test:
   ```powershell
   curl http://localhost:8000/health
   ```

## Example request (live mode)
Readable JSON payload:
```json
{
  "query": "monitor weather",
  "mode": "live",
  "current_location": "Zvolen",
  "active_route_id": "Kosice-Bratislava",
  "delay_minutes": 15,
  "structured_trip": {
    "start": "Kosice",
    "destination": "Bratislava",
    "stops": ["Spissky hrad", "Oravska galeria"],
    "startDate": "2025-12-01T00:00:00Z",
    "endDate": "2025-12-04T00:00:00Z",
    "preferences": {
      "categories": ["Culture", "Food"],
      "transport": "car",
      "budget": 500,
      "notes": "Culture-focused stops only."
    }
  }
}
```
