# Alpha Engine — Paper Trading App

A polished Android cockpit for a causal, event-driven market research and paper-trading engine.

## Current release
- Android Jetpack Compose UI
- Portfolio dashboard
- Live market snapshots through backend
- World/event intelligence UI
- Causal chain visualization
- Signal cards with evidence/confidence
- Paper BUY/SELL execution
- Order history
- GitHub Actions APK build
- Alpaca paper trading only

## Run backend
Copy `backend/.env.example` to `backend/.env`, add Alpaca paper credentials, then:
`cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0`

## Android
Local emulator backend is `http://10.0.2.2:8000`.

## Important
This release does not place real-money trades. Alpaca paper trading is used as the simulated execution layer.
