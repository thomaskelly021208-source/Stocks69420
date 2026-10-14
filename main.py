import os
from datetime import datetime, timezone
from typing import Literal
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Alpha Engine API", version="1.0.0")
TRADING = "https://paper-api.alpaca.markets/v2"
DATA = "https://data.alpaca.markets/v2"
WATCHLIST = ["AAPL","MSFT","NVDA","TSLA","AMZN","GOOGL","META","AMD","XOM","CVX"]

def headers():
    return {
        "APCA-API-KEY-ID": os.getenv("ALPACA_API_KEY",""),
        "APCA-API-SECRET-KEY": os.getenv("ALPACA_API_SECRET",""),
    }

async def alpaca(method, url, **kwargs):
    async with httpx.AsyncClient(timeout=12) as c:
        r = await c.request(method, url, headers=headers(), **kwargs)
        if r.status_code >= 400:
            raise HTTPException(r.status_code, r.text)
        return r.json()

@app.get("/health")
async def health():
    return {"ok": True, "paper_mode": True, "time": datetime.now(timezone.utc).isoformat()}

@app.get("/api/account")
async def account():
    a = await alpaca("GET", f"{TRADING}/account")
    return {
        "equity": a.get("equity"),
        "cash": a.get("cash"),
        "buying_power": a.get("buying_power"),
        "portfolio_value": a.get("portfolio_value"),
        "status": a.get("status"),
    }

@app.get("/api/market")
async def market():
    data = await alpaca("GET", f"{DATA}/stocks/snapshots", params={"symbols": ",".join(WATCHLIST), "feed":"iex"})
    out=[]
    for symbol, s in data.items():
        q=s.get("latestQuote") or {}
        t=s.get("latestTrade") or {}
        d=s.get("dailyBar") or {}
        prev=s.get("prevDailyBar") or {}
        price=t.get("p") or q.get("ap")
        change=((price-prev.get("c"))/prev.get("c")*100) if price and prev.get("c") else 0
        out.append({"symbol":symbol,"price":price,"bid":q.get("bp"),"ask":q.get("ap"),"change_pct":change,"volume":d.get("v")})
    return out

@app.get("/api/world")
async def world():
    return [
      {"title":"Middle East energy risk","severity":"HIGH","chain":["Geopolitical disruption","Supply risk","Crude oil","Energy margins","Inflation"],"confidence":0.71,"status":"MONITORING","text":"Example causal monitor. Connect a news/event ingestion worker for live evidence."},
      {"title":"Agricultural supply shock","severity":"MEDIUM","chain":["Weather anomaly","Crop yield","Commodity supply","Food prices","Producers/importers"],"confidence":0.58,"status":"WATCH","text":"Example causal monitor awaiting live event evidence."},
    ]

@app.get("/api/signals")
async def signals():
    return [
      {"symbol":"XOM","action":"WATCH","score":0.63,"reason":"Energy-chain exposure; requires fresh event confirmation.","risk":"MEDIUM"},
      {"symbol":"NVDA","action":"WAIT","score":0.51,"reason":"No validated event catalyst currently connected.","risk":"HIGH"},
    ]

class Order(BaseModel):
    symbol: str
    side: Literal["buy","sell"]
    notional_usd: float

@app.post("/api/paper/order")
async def order(o: Order):
    if o.notional_usd <= 0 or o.notional_usd > 1000000:
        raise HTTPException(400, "Invalid notional")
    return await alpaca("POST", f"{TRADING}/orders", json={
        "symbol": o.symbol.upper(),
        "notional": str(round(o.notional_usd,2)),
        "side": o.side,
        "type":"market",
        "time_in_force":"day"
    })

@app.get("/api/paper/orders")
async def orders():
    return await alpaca("GET", f"{TRADING}/orders", params={"status":"all","limit":50,"direction":"desc"})

@app.delete("/api/paper/orders")
async def cancel():
    return await alpaca("DELETE", f"{TRADING}/orders")
