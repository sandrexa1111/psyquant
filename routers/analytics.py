from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np
import alpaca_trade_api as tradeapi

router = APIRouter(prefix="/analytics", tags=["analytics"])

# We might want to inject the API client or initialize it here if shared
# For now, let's assume we can re-init or pass data. 
# Re-init is safer for valid scope if we move to dependencies later.
from config import api

def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    if len(returns) < 2:
        return 0.0
    excess_returns = returns - risk_free_rate
    if returns.std() == 0:
        return 0.0
    return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

def calculate_max_drawdown(equity_curve):
    if len(equity_curve) < 1:
        return 0.0
    
    # Calculate running maximum
    running_max = np.maximum.accumulate(equity_curve)
    # Ensure no division by zero if running_max is 0 (unlikely for equity)
    running_max[running_max == 0] = 1 
    
    drawdown = (equity_curve - running_max) / running_max
    return drawdown.min()

@router.get("/metrics")
def get_portfolio_metrics(period: str = "1A"):
    """
    Calculate institutional metrics: Sharpe, Max Drawdown, Win Rate, Beta (simplified).
    """
    try:
        # Fetch history (Daily bars)
        # Fetch history (Daily bars) via adapter (returns list of dicts)
        history_list = api.get_portfolio_history(period=period, timeframe="1D")
        
        if not history_list:
             return {
                "summary": {
                    "total_equity": 0.0,
                    "total_return": 0.0,
                    "sharpe_ratio": 0.0,
                    "max_drawdown": 0.0,
                    "win_rate": 0.0,
                },
                "equity_curve": [],
                "allocation": _get_allocation_data()
            }

        # Convert to DataFrame for analytics calculations
        history = pd.DataFrame(history_list)
        # Ensure 'time' is datetime if needed, or set index
        if 'time' in history.columns:
            history['time'] = pd.to_datetime(history['time'])
            history.set_index('time', inplace=True)

        # Calculate Returns
        # 'equity' is the total account value
        history['returns'] = history['equity'].pct_change().fillna(0)
        
        # 1. Sharpe Ratio
        sharpe = calculate_sharpe_ratio(history['returns'])
        
        # 2. Max Drawdown
        max_dd = calculate_max_drawdown(history['equity'].values)
        
        # 3. Win Rate (Days)
        winning_days = len(history[history['returns'] > 0])
        total_days = len(history)
        win_rate = winning_days / total_days if total_days > 0 else 0
        
        # 4. Total Return
        start_equity = history['equity'].iloc[0]
        end_equity = history['equity'].iloc[-1]
        total_return = (end_equity - start_equity) / start_equity if start_equity > 0 else 0

        return {
            "summary": {
                "total_equity": float(end_equity),
                "total_return": float(round(total_return * 100, 2)),
                "sharpe_ratio": 0.0 if np.isnan(sharpe) or np.isinf(sharpe) else float(round(sharpe, 2)),
                "max_drawdown": float(round(max_dd * 100, 2)),
                "win_rate": float(round(win_rate * 100, 2)),
            },
            "equity_curve": [
                {"time": t.strftime('%Y-%m-%d'), "value": float(v)} 
                for t, v in zip(history.index, history['equity'])
            ],
            "allocation": _get_allocation_data()
        }
    except Exception as e:
        print(f"ERROR IN METRICS: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

def _get_allocation_data():
    try:
        positions = api.get_positions() # Returns list of dicts
        account = api.get_account() # Returns dict
        total_equity = float(account['equity'])
        
        allocation = []
        for p in positions:
            market_value = float(p['market_value'])
            allocation.append({
                "symbol": p['symbol'],
                "value": market_value,
                "percentage": round((market_value / total_equity) * 100, 2)
            })
            
        # Sort by weight
        allocation.sort(key=lambda x: x['percentage'], reverse=True)
        return allocation
    except Exception:
        return []
