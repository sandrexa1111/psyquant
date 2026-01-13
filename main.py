from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import alpaca_trade_api as tradeapi
import os
from pydantic import BaseModel
from typing import List, Optional
from routers.auth import get_current_user
from database.models import User
from fastapi import Depends, Header

# Demo user ID for unauthenticated access (simulation mode)
DEMO_USER_ID = "00000000-0000-0000-0000-000000000000"

# Configuration (Hardcoded for this demo based on test.py)
# Exporting these for routers to use
# Configuration
# Configuration
from config import api
from database import models
from database.database import engine

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quant Dashboard API")

# Setup CORS to allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
# Note: We need to do this after creating 'app' or just include them
# To avoid circular imports if routers import 'api' from main, we really should have a config file.
# But for now, we will do a local import or rely on the file existence.
try:
    from routers import analytics
    app.include_router(analytics.router)
except ImportError:
    print("Analytics router not found or dependency missing.")

try:
    from routers import market
    app.include_router(market.router)
except ImportError:
    print("Market router not found or dependency missing.")

try:
    from routers import trade
    app.include_router(trade.router)
except ImportError:
    print("Trade router not found or dependency missing.")

try:
    from routers import algo
    app.include_router(algo.router)
except ImportError:
    print("Algo router not found or dependency missing.")

try:
    from routers import ai
    app.include_router(ai.router)
except ImportError:
    print("AI router not found or dependency missing.")

try:
    from routers import settings
    app.include_router(settings.router)
except ImportError:
    print("Settings router not found or dependency missing.")

try:
    from routers import auth
    app.include_router(auth.router)
except ImportError:
    print("Auth router not found.")

try:
    from routers import users
    app.include_router(users.router)
except ImportError:
    print("Users router not found.")

try:
    from routers import alerts
    app.include_router(alerts.router)
except ImportError:
    print("Alerts router not found.")

try:
    from routers import behavior
    app.include_router(behavior.router)
except ImportError:
    print("Behavior Intelligence router not found.")

try:
    from routers import pattern_alerts
    app.include_router(pattern_alerts.router)
except ImportError:
    print("Pattern Alerts router not found.")

try:
    from routers import journal
    app.include_router(journal.router)
except ImportError:
    print("Journal router not found.")



@app.get("/")
def read_root():
    return {"message": "Quant Dashboard API is running"}

@app.get("/account")
def get_account(authorization: Optional[str] = Header(None)):
    try:
        # Use demo user if no auth token provided (for development/simulation)
        user_id = DEMO_USER_ID
        if authorization:
            # TODO: Properly validate token and extract user_id
            pass
        
        # Pass user_id to adapter if supported
        if hasattr(api, 'get_account') and 'user_id' in api.get_account.__code__.co_varnames:
             account = api.get_account(user_id=user_id)
        else:
             account = api.get_account()
             
        return {
            "status": account["status"],
            "buying_power": float(account["buying_power"]),
            "cash": float(account["cash"]),
            "portfolio_value": float(account["portfolio_value"]),
            "currency": account["currency"],
            "daytrade_count": account["daytrade_count"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/positions")
def get_positions(authorization: Optional[str] = Header(None)):
    try:
        # Use demo user if no auth token provided (for development/simulation)
        user_id = DEMO_USER_ID
        if authorization:
            # TODO: Properly validate token and extract user_id
            pass
            
        if hasattr(api, 'get_positions') and 'user_id' in api.get_positions.__code__.co_varnames:
            positions = api.get_positions(user_id=user_id)
        else:
            positions = api.get_positions()
        return [
            {
                "symbol": p["symbol"],
                "qty": float(p["qty"]),
                "side": p["side"],
                "market_value": float(p["market_value"]),
                "avg_entry_price": float(p["avg_entry_price"]),
                "current_price": float(p["current_price"]),
                "unrealized_pl": float(p["unrealized_pl"]),
                "unrealized_plpc": float(p["unrealized_plpc"])
            } for p in positions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-data/{symbol}")
def get_market_data(symbol: str):
    try:
        # Get last 100 bars for the symbol (15Min timeframe)
        # Adapter returns list of dicts, no .df
        bars = api.get_bars(symbol, timeframe="1Min", limit=100)
        
        # Simple serialization for the frontend
        data = bars # Already in correct format from adapter
        return {"symbol": symbol, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history():
    try:
        # Get portfolio history for the last 30 days roughly (1A = 1 year, we can use 1M)
        # timeframe='1D' gives daily close
        history = api.get_portfolio_history(period="1M", timeframe="1D")
        
        # Adapter returns list of dicts already formatted mostly
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
