# 🧭 TripGuardian
TripGuardian is an autonomous AI agent that helps you plan a route, refine it to your preferences, and once you start your journey, it monitors your location, weather, and conditions in real time - proactively suggesting adjustments to ensure your trip is as smooth and enjoyable as possible.

---

## 🌍 The Problem We Solve

Traditional navigation tools can plan a route, but they fail when conditions change:

- the plan is static and doesn’t adapt to delays or weather,
- AI planners usually stop after the first suggestion,
- the user must constantly think about whether to skip, shorten, or change something.

There is no tool that behaves like a **digital co-driver**, not just a map.

---

## 💡 The Solution – LiveRoute Agent

LiveRoute Agent operates in two phases:

### 1️⃣ Planning Phase

The user enters:
- **Start** and **Destination (A → B)**  
- optional preferences (scenic views, quick stops, coffee/food, etc.)

The AI agent:
- generates the first draft of a route with recommended POIs,  
- adds short descriptions and recommendations,  
- allows the user to add, remove, or reorder stops.

When satisfied, the user hits **Save Route**.

---

### 2️⃣ Live Mode – Autonomous Agent on the Road

When the user starts the trip:

- they click **Start** on a saved route,
- the web app begins **live location tracking**,
- shows the user on the map along with the planned route.

Every X minutes, the agent:

1. reads the current location,  
2. fetches weather for upcoming points,  
3. analyzes timing, delays, and conditions,  
4. autonomously generates actionable suggestions:

> “Rain is expected at Stop 3. I recommend skipping the viewpoint and visiting a café in City X.”  
> “You’re running behind schedule. Consider shortening Stop Y to 10 minutes.”

The user can accept or ignore the suggestions.  
The agent handles all reasoning autonomously.

---

## 🎯 MVP Features (Hackathon Version)

### Route Planning
- Form: Start, Destination  
- AI-generated POIs with descriptions  
- User selects final stops → route is saved  

### Route Details
- map display  
- list of stops  

### Live Mode
- browser-based live tracking  
- periodic (every X minutes) weather + analysis  
- text-based recommendations displayed in UI  

> No automatic map re-routing in MVP — suggestions are text-only, which is perfect for a hackathon proof-of-concept.

---

## 🤖 Why It Qualifies as an Autonomous AI Agent

The user provides only high-level goals:
- “Plan a route from A to B.”  
- “Start live mode.”

The agent then autonomously:
- plans and adjusts the route,
- uses routing, weather, geolocation, and AI reasoning,
- monitors conditions periodically,
- generates decisions and suggestions without being asked.

It behaves like a **digital co-pilot**, not a chatbot.

---

## 🏗️ Tech Stack

### Frontend
- **React + Vite**
- **PWA (Progressive Web App)**
- Map integration (Mapbox / Leaflet)

### Backend (Serverless)
- **AWS Lambda**
- **AWS API Gateway**

### Hosting & Storage
- **Amazon S3**: `travel-guardian-webui`  
- **AWS CloudFront** (CDN distribution)

### Authentication
- **Google OAuth2**
- **AWS Cognito**

### AI
- **OpenAI API**

---
