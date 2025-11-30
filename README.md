# 🧭 TripGuardian

**TripGuardian** is an autonomous multi-agent system that helps you plan routes, refine them, and intelligently adapt your journey in real time.  
It doesn’t just plan your trip - it travels with you, monitors conditions, and proactively recommends adjustments so your route is always optimal.

---

# 🌍 The Problem We Solve

Traditional navigation tools fail when real-world conditions change:

- plans are static and don’t adapt to delays or weather,
- AI planners usually stop after generating a single draft,
- the user must constantly decide whether to skip or adjust stops,
- no system behaves like an intelligent co-driver that anticipates needs.

TripGuardian fills this gap by acting as a **digital co-pilot**, not just a map.

---

# 🤖 Multi-Agent Architecture

TripGuardian consists of **three autonomous AI agents**, each responsible for a different phase of the journey:

1. **Calendar Watcher Agent** – detects upcoming trips from the user’s Google Calendar.  
2. **Trip Planner Agent** – generates and refines route drafts with meaningful stops.  
3. **Live Route Agent** – monitors the active journey and adapts it in real time.

Together, they think, plan, act, and coordinate — fulfilling the Autonomous AI Agents challenge.

---

# 📅 Calendar Watcher Agent

With the user’s consent to connect their Google Calendar, the **Calendar Watcher Agent** works quietly in the background:

- periodically scans calendar events (daily/weekly),
- detects events that imply long-distance travel,
- identifies meeting locations, out-of-town events, and trips far from the user’s home,
- generates a **Trip Opportunity** whenever it finds potential travel.

Example:

> “You have a meeting in Bratislava next Friday. Would you like me to draft a route from Kosice with meaningful stops along the way?”

The Trip Opportunity is then passed to the Trip Planner Agent.

---

# 🧠 Trip Planner Agent

The **Trip Planner Agent** begins when the user manually enters a route *or* when a trip opportunity is detected.

### User provides:
- **Start** and **Destination (A → B)**  
- optional preferences (views, nature, food, culture, quick stops)

### Agent does:
1. generates a draft route with recommended POIs along the way,  
2. adds short descriptions and weather suitability,  
3. allows the user to reorder, add, or remove stops,  
4. saves the route when the user clicks **Save Route**.

The result is a personalized and flexible travel plan.

---

# 🚗 Live Route Agent

When the user actually starts their journey:

- they open a saved route and press **Start**,  
- the web app begins **live location tracking** (browser-based),  
- the map displays the user’s current position and planned stops.

### Every X minutes, the agent autonomously:
1. reads the user's live GPS location,  
2. checks upcoming weather conditions,  
3. evaluates timing and delays,  
4. generates actionable recommendations:

Examples:

> “Rain expected at Stop 2 — consider skipping the viewpoint and visiting this café instead.”  
>  
> “You’re 30 minutes behind schedule. I recommend shortening Stop 3.”

The user may accept or ignore these suggestions — the agent handles all reasoning.

---

# 🎯 Hackathon MVP – Feature Overview

### Route Planning
- Input: Start + Destination  
- AI-generated POIs with descriptions  
- User selects final stops  
- Saved route stored locally or in DynamoDB  

### Route Details
- Map view  
- List of selected stops  
- Button to start Live Mode  

### Live Mode
- Browser-based GPS tracking  
- Periodic weather check  
- AI-powered recommendations  
- Text-only suggestions

### Calendar Integration
- Google Calendar read-only connection  
- Calendar Watcher detects possible trips  
- Suggests planning a route automatically

---

# 🧩 Why It Qualifies as an Autonomous AI System

The user gives only high-level commands:
- “Plan a route from A to B.”  
- “Start live mode.”  
- “Check my calendar for upcoming trips.”

Meanwhile, the agents autonomously:

- analyze the calendar,
- detect travel opportunities,
- create draft routes,
- monitor weather and timing,
- propose adjustments without being asked.

TripGuardian behaves as a true **autonomous multi-agent co-pilot**, not a simple chatbot.

---

# 🏗️ Tech Stack

## Frontend
- **React + Vite**  
- **Progressive Web App (PWA)**  
- **Leaflet or Mapbox** for maps  
- **Tailwind CSS** for styling  

## Backend (Serverless)
- **AWS Lambda** for logic + AI calls  
- **AWS API Gateway** for REST endpoints  
- **AWS Cognito** for Google OAuth2 login  

## Hosting & Storage
- **Amazon S3** for PWA hosting  
- **AWS CloudFront** for CDN  
- **DynamoDB** for persistent route storage (optional)  

## AI Engine
- **OpenAI API**  
  - GPT-4.1-mini for fast reasoning  
  - GPT-4.1 for high-quality route planning  

## External Integrations
- **Google Calendar API (read-only)**  
- **OpenWeather API**  
- **Map routing API** (Mapbox/Google)

---

# 🚀 Summary

TripGuardian is not just a route planner.  
It is an **autonomous, proactive, multi-agent travel companion** that:

- discovers upcoming trips from your calendar,  
- drafts personalized routes with meaningful stops,  
- monitors your journey in real time,  
- adapts your trip automatically based on weather and delays.

A travel experience that finally *thinks with you* — not after you.

---

# 🔧 Lokálne spustenie backendu

Pre rýchle testovanie AI agentov vieš backend naštartovať aj bez AWS infra:

1. `cd backend && pip install -r requirements.txt`
2. nastav kľúče (minimálne Google Places) – napr. vo Windows PowerShell:
  ```powershell
  $env:GOOGLE_PLACES_API_KEY="<tvoj_kľúč>"
  ```
  Voliteľne môžeš použiť `GOOGLE_MAPS_API_KEY` alebo `GOOGLE_API_KEY`. Ostatné nástroje využívajú verejné API (Open-Meteo, OpenStreetMap), takže nevyžadujú prihlásenie.
3. spusti server `python main.py` a otestuj `curl http://localhost:8000/health`.
4. route planner, POI aj čerpacie stanice kombinujú Google Places + Overpass, preto odporúčame bežať len zopár dopytov za sebou (dodržiavame dlhšie timeouty a jednoduchý rate-limit priamo v kóde).

Frontend (Vite) vieš pustiť nezávisle cez `cd frontend && npm install && npm run dev`. Výchozí .env smeruje na `http://localhost:8000`.
