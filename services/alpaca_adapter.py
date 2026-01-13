from .trading_provider import TradingProvider
import alpaca_trade_api as tradeapi
from typing import List, Dict, Any, Optional

class AlpacaAdapter(TradingProvider):
    def __init__(self, api_key: str, api_secret: str, base_url: str):
        self.api = tradeapi.REST(api_key, api_secret, base_url, api_version="v2")
        # Validate connection immediately
        try:
            self.api.get_account()
        except Exception as e:
            raise ValueError(f"Invalid Alpaca Credentials: {e}")

    def get_account(self) -> Dict[str, Any]:
        account = self.api.get_account()
        return {
            "status": account.status,
            "buying_power": float(account.buying_power),
            "cash": float(account.cash),
            "portfolio_value": float(account.portfolio_value),
            "currency": account.currency,
            "daytrade_count": account.daytrade_count,
            "equity": float(account.equity)
        }

    def get_positions(self) -> List[Dict[str, Any]]:
        positions = self.api.list_positions()
        return [
            {
                "symbol": p.symbol,
                "qty": float(p.qty),
                "side": p.side,
                "market_value": float(p.market_value),
                "avg_entry_price": float(p.avg_entry_price),
                "current_price": float(p.current_price),
                "unrealized_pl": float(p.unrealized_pl),
                "unrealized_plpc": float(p.unrealized_plpc)
            } for p in positions
        ]

    def list_orders(self, status: str = "open", limit: int = 50) -> List[Dict[str, Any]]:
        orders = self.api.list_orders(status=status, limit=limit)
        return [
            {
                "id": str(o.id),
                "symbol": o.symbol,
                "qty": float(o.qty) if o.qty else 0,
                "side": o.side,
                "type": o.type,
                "status": o.status,
                "created_at": o.created_at.isoformat(),
                "filled_qty": float(o.filled_qty) if o.filled_qty else 0
            } for o in orders
        ]

    def submit_order(self, symbol: str, qty: float, side: str, type: str, 
                     time_in_force: str = "day", limit_price: Optional[float] = None) -> Dict[str, Any]:
        args = {
            "symbol": symbol.upper(),
            "qty": qty,
            "side": side.lower(),
            "type": type.lower(),
            "time_in_force": time_in_force.lower()
        }
        if limit_price is not None:
            args["limit_price"] = limit_price

        order = self.api.submit_order(**args)
        return {
            "id": str(order.id),
            "status": order.status,
            "symbol": order.symbol,
            "side": order.side,
            "qty": float(order.qty) if order.qty else 0.0
        }

    def get_portfolio_history(self, period: str = "1M", timeframe: str = "1D") -> List[Dict[str, Any]]:
        history = self.api.get_portfolio_history(period=period, timeframe=timeframe).df
        
        data = []
        if not history.empty:
            for index, row in history.iterrows():
                # Alpaca often returns 'equity' but user might want returns calculation handling here
                # Keeping it raw for now as per original map
                data.append({
                     "time": index.isoformat(),
                     "equity": row['equity'],
                     "profit_loss": row['profit_loss'],
                     "profit_loss_pct": row['profit_loss_pct'],
                     "returns": row.get('returns', 0) # Fallback if calculated elsewhere
                })
        return data

    def get_bars(self, symbol: str, timeframe: str = "1Min", limit: int = 100) -> List[Dict[str, Any]]:
        # Map timeframe string to Alpaca constants if needed, for now assuming string pass-through works or simple map
        tf_map = {
            "1Min": tradeapi.TimeFrame.Minute,
            "15Min": tradeapi.TimeFrame.Minute, # Logic handled by caller for now? Or just fetch minutes
             "1Hour": tradeapi.TimeFrame.Hour,
             "1Day": tradeapi.TimeFrame.Day
        }
        # Default to Minute if not found (simplified for now)
        tf = tf_map.get(timeframe, tradeapi.TimeFrame.Minute)
        
        bars = self.api.get_bars(symbol, tf, limit=limit).df
        data = []
        if not bars.empty:
            for index, row in bars.iterrows():
                data.append({
                    "time": index.isoformat(),
                    "open": row['open'],
                    "high": row['high'],
                    "low": row['low'],
                    "close": row['close'],
                    "volume": row['volume']
                })
        return data
