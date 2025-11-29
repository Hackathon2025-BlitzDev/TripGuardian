# 🧭 TripGuardian
TripGuardian je autonómny AI agent, ktorý ti najprv pomôže naplánovať trasu, nechá ťa ju doladiť podľa tvojich predstáv a keď na ňu vyrazíš, v reálnom čase sleduje tvoju polohu, počasie a situáciu na trase a sám navrhuje zmeny, aby bola cesta čo najlepšia.

---

## 🌍 Problém, ktorý riešime

Súčasné nástroje na plánovanie trás majú jasné limity:

- trasa je statická a nereaguje na real-time zmeny,
- AI planner väčšinou poskytne iba prvý návrh bez dynamického update,
- používateľ musí sám sledovať počasie, meškanie a rozhodovať.

Chýba niečo, čo funguje ako **digitálny spolujazdec**, nie len mapa.

---

## 💡 Riešenie – LiveRoute Agent

LiveRoute Agent funguje v dvoch hlavných režimoch:

### 1️⃣ Fáza: Plánovanie trasy

Používateľ zadá:
- **Start** a **Destination** (A → B)
- voliteľné preferencie (výhľady, rýchle zastávky, káva, atď.)

AI agent:
- vygeneruje návrh trasy a POI zastávky,
- doplní ich o krátke popisy a odporúčania,
- umožní používateľovi zastávky pridávať, mazať, meniť poradie.

Po potvrdení sa trasa uloží.

---

### 2️⃣ Fáza: Live režim (autonómny agent počas jazdy)

Po stlačení **Start** na uloženej trase:

- web app sleduje **live polohu** používateľa,
- zobrazí mapu a plánované POI,
- agent každých X minút urobí:

1. zistenie polohy  
2. predikciu počasia  
3. analýzu meškania a podmienok  
4. autonómne **generuje odporúčania**:

> „Na vyhliadke bude pršať – preskoč ju a navrhujem kaviareň v meste X.“  
> „Meškáš 25 minút – skráť zastávku Y na 10 minút.“

Používateľ môže odporúčania prijať alebo ignorovať.

---

## 🎯 MVP funkcionalita (hackathon verzia)

### Plánovanie
- formulár: Start, Destination  
- AI návrh zastávok s popismi  
- výber zastávok → uloženie trasy  

### Detail trasy
- mapa  
- zoznam zastávok  

### Live mód
- sledovanie polohy (kým je tab otvorený)  
- každých X minút: počasie + AI odporúčanie  
- zobrazenie návrhov v UI paneli

> V MVP sa trasa fyzicky neprepočítava – odporúčania sú textové.

---

## 🤖 Prečo ide o autonómny AI agent

Používateľ dá len jednoduché inštrukcie:
- „Naplánuj trasu A → B.“
- „Začni live mód.“

Agent následne:
- plánuje,  
- používa routing, počasie, geolokáciu,  
- pravidelne kontroluje realitu,  
- autonómne navrhuje zmeny.

Ide teda o skutočného **autonómneho AI spolujazdca**.

---

## 🏗️ Tech Stack

### Frontend
- **React + Vite**
- **PWA (Progressive Web App)**
- Mapová integrácia (Mapbox/Leaflet)

### Backend (serverless)
- **AWS Lambda**
- **AWS API Gateway**

### Hosting & Storage
- **S3 bucket**: `travel-guardian-webui`  
- **CloudFront distribution** (CDN)

### Auth
- **Google OAuth2**
- **AWS Cognito**

### AI
- **OpenAI API**

---
