from fastapi import APIRouter, HTTPException, BackgroundTasks
import asyncio
from typing import List
from datetime import datetime
import alpaca_trade_api as tradeapi
import pandas as pd
import numpy as np

# Re-import config
from main import API_KEY, API_SECRET, BASE_URL

router = APIRouter(prefix="/algo", tags=["algo"])
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version="v2")

# Global State (In-Memory for MVP)
class BotState:
    running = False
    symbol = "SPY"
    logs = []
    last_action = None

bot = BotState()

async def trading_loop():
    """
    Simulated trading loop. Checks price vs SMA.
    """
    while bot.running:
        try:
            # 1. Fetch Data (1 min bars for speed in demo)
            bars = api.get_bars(bot.symbol, '1Min', limit=20).df
            
            if not bars.empty:
                current_price = bars.iloc[-1]['close']
                # Calculate SMA-10
                sma = bars['close'].rolling(window=10).mean().iloc[-1]
                
                log_entry = {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "price": float(current_price),
                    "sma": float(sma) if not pd.isna(sma) else 0,
                    "action": "HOLD"
                }

                # Logic: Simple Crossover
                # If Price > SMA * 1.001 -> BUY (Trend following)
                # If Price < SMA * 0.999 -> SELL
                
                # Note: This is very basic.
                if not pd.isna(sma):
                    if current_price > sma * 1.0005:
                        log_entry["action"] = "SIGNAL_BUY"
                        # Check if we should actually trade (limit to 1 position to avoid spam)
                        # MVP: Just log the signal
                    elif current_price < sma * 0.9995:
                        log_entry["action"] = "SIGNAL_SELL"
                
                bot.logs.insert(0, log_entry)
                # Keep log size small
                if len(bot.logs) > 50:
                    bot.logs.pop()
                    
        except Exception as e:
            print(f"Algo Error: {e}")
            bot.logs.insert(0, {"time": datetime.now().strftime("%H:%M:%S"), "action": "ERROR", "price": 0, "sma": 0})
        
        await asyncio.sleep(5) # Poll every 5s

@router.post("/start")
async def start_algo(background_tasks: BackgroundTasks):
    if bot.running:
        return {"status": "Already running"}
    
    bot.running = True
    bot.logs.insert(0, {"time": datetime.now().strftime("%H:%M:%S"), "action": "STARTED", "price": 0, "sma": 0})
    
    # Fastapi background task might not persist indefinitely without special handling.
    # ideally we use asyncio.create_task here for the loop
    asyncio.create_task(trading_loop())
    
    return {"status": "Started", "symbol": bot.symbol}

@router.post("/stop")
def stop_algo():
    bot.running = False
    bot.logs.insert(0, {"time": datetime.now().strftime("%H:%M:%S"), "action": "STOPPED", "price": 0, "sma": 0})
    return {"status": "Stopped"}

@router.get("/status")
def get_status():
    return {
        "running": bot.running,
        "symbol": bot.symbol,
        "logs": bot.logs
    }
