from .trading_provider import TradingProvider
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import pandas as pd
import random
import json
import os

import yfinance as yf
from datetime import timedelta

SIM_DATA_FILE = "sim_data.json"

class LocalSimAdapter(TradingProvider):
    def __init__(self, initial_cash: float = 100000.0, user_id: Optional[str] = None):
        self.cash = initial_cash
        self.start_cash = initial_cash
        self.positions: Dict[str, Dict] = {} # symbol -> {qty, avg_entry_price, current_price}
        self.orders: List[Dict] = []
        self.portfolio_history: List[Dict] = [] 
        
        self.default_user_id = "00000000-0000-0000-0000-000000000000"
        
        self._price_cache: Dict[str, Dict] = {} # {symbol: {price, timestamp}}
        self.snapshots: Dict[str, Dict] = {} # order_id -> snapshot_data
        
        # Load accumulated state
        self._load_state(user_id)
    
    @property
    def db(self):
        # Lazy load DB session
        from database.database import SessionLocal
        return SessionLocal()

    def reset_account(self, balance: float, user_id: Optional[str] = None):
        target_uid = user_id or self.default_user_id
        
        # Clear in-memory state if focusing on single user instance (Naive for now)
        # Ideally we load state per request but since this is an Adapter Singleton we might have issues
        # For now, let's assume one main user or we reload.
        self.cash = balance
        self.start_cash = balance
        self.positions = {}
        self.orders = []
        self.snapshots = {}
        self.portfolio_history = []
        
        # Reset DB state
        from database.models import SandboxAccount, SandboxOrder, SandboxPosition, Trade, User
        session = self.db
        try:
            # Find account
            account = session.query(SandboxAccount).filter(SandboxAccount.user_id == target_uid).first()
            if account:
                # Delete related items
                session.query(SandboxOrder).filter(SandboxOrder.sandbox_account_id == account.id).delete()
                session.query(SandboxPosition).filter(SandboxPosition.sandbox_account_id == account.id).delete()
                # Also delete Trades for consistency if source=sandbox
                session.query(Trade).filter(Trade.user_id == target_uid, Trade.source == 'sandbox').delete()
                
                account.starting_balance = balance
                account.current_balance = balance
                account.unrealized_pnl = 0
            else:
                 account = SandboxAccount(
                     user_id=target_uid,
                     starting_balance=balance,
                     current_balance=balance
                 )
                 session.add(account)
            
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"DB Reset Error: {e}")
        finally:
            session.close()
            
        print(f"🔄 Simulation Reset for {target_uid}. Balance: ${balance:,.2f}")

    def _load_state(self, user_id: Optional[str] = None):
        target_uid = user_id or self.default_user_id
        
        # Load from DB
        from database.models import SandboxAccount, SandboxOrder, SandboxPosition
        session = self.db
        try:
            account = session.query(SandboxAccount).filter(SandboxAccount.user_id == target_uid).first()
            
            if account:
                self.cash = float(account.current_balance) if account.current_balance is not None else float(account.starting_balance)
                self.start_cash = float(account.starting_balance)
                
                # Load Positions
                db_positions = session.query(SandboxPosition).filter(SandboxPosition.sandbox_account_id == account.id).all()
                self.positions = {}
                for p in db_positions:
                    self.positions[p.symbol] = {
                        "qty": float(p.qty),
                        "avg_entry_price": float(p.avg_entry_price)
                        # current_price calc happens live
                    }
                    
                # Load Orders (open only for memory efficiency, or all)
                db_orders = session.query(SandboxOrder).filter(SandboxOrder.sandbox_account_id == account.id).all()
                self.orders = []
                for o in db_orders:
                    self.orders.append({
                        "id": o.id,
                        "symbol": o.symbol,
                        "qty": float(o.qty),
                        "side": o.side,
                        "type": o.order_type,
                        "status": o.status,
                        "limit_price": float(o.limit_price) if o.limit_price else None,
                        "created_at": o.created_at.isoformat() if o.created_at else None,
                        "filled_qty": float(o.qty) if o.status == 'filled' else 0, # Simplified
                        "filled_avg_price": float(o.filled_price) if o.filled_price else 0
                    })
                
                print(f"✅ Loaded Simulation State for {target_uid}. Cash: ${self.cash:,.2f}")
            else:
                self.reset_account(100000.0, user_id=target_uid) # Create initial
                
        except Exception as e:
            print(f"⚠️ Failed to load simulation state from DB: {e}")
            import traceback
            traceback.print_exc()
        finally:
            session.close()

    def _save_state(self, user_id: Optional[str] = None):
        target_uid = user_id or self.default_user_id
        
        # Save to DB - In a real event-sourced system we wouldn't dump state like this
        # We would insert events. But for mimicking implementation:
        from database.models import SandboxAccount, SandboxOrder, SandboxPosition, Trade
        session = self.db
        try:
             account = session.query(SandboxAccount).filter(SandboxAccount.user_id == target_uid).first()
             if not account: return # Should exist
             
             # Update Account
             account.current_balance = self.cash
             
             # Sync Positions (Upsert)
             # Naive strategy: delete all positions for account and re-insert (easiest for sync)
             session.query(SandboxPosition).filter(SandboxPosition.sandbox_account_id == account.id).delete()
             for sym, pos in self.positions.items():
                 db_pos = SandboxPosition(
                     sandbox_account_id=account.id,
                     symbol=sym,
                     qty=pos['qty'],
                     avg_entry_price=pos['avg_entry_price']
                 )
                 session.add(db_pos)

             # Sync Orders
             session.query(SandboxOrder).filter(SandboxOrder.sandbox_account_id == account.id).delete()
             for o in self.orders:
                 db_order = SandboxOrder(
                     id=o['id'],
                     sandbox_account_id=account.id,
                     symbol=o['symbol'],
                     side=o['side'],
                     qty=o['qty'],
                     order_type=o['type'],
                     limit_price=o.get('limit_price'),
                     status=o['status'],
                     filled_price=o.get('filled_avg_price'),
                     filled_at=datetime.fromisoformat(o['filled_at']) if o.get('filled_at') else None,
                     created_at=datetime.fromisoformat(o['created_at']) if o.get('created_at') else datetime.now()
                 )
                 session.add(db_order)
                 
             session.commit()
        except Exception as e:
            session.rollback()
            print(f"⚠️ Failed to save simulation state to DB: {e}")
        finally:
            session.close()

    def _get_price(self, symbol: str) -> float:
        # Check cache (15 seconds TTL)
        now = datetime.now()
        cache = self._price_cache.get(symbol)
        if cache and (now - cache['timestamp']).total_seconds() < 15:
            return cache['price']

        try:
            # Fetch Real Price
            ticker = yf.Ticker(symbol)
            # fast_info is faster than history
            price = ticker.fast_info['last_price']
            
            if price is None:
                 raise ValueError("Price not found")
                 
            self._price_cache[symbol] = {'price': price, 'timestamp': now}
            return price
        except Exception:
            # Fallback for offline/error
            print(f"⚠️ Price fetch failed for {symbol}. Using mock.")
            return self._price_cache.get(symbol, {}).get('price', 100.0 + random.uniform(-1, 1))

    def _match_orders(self):
        # Lazy matching engine: Check pending orders against current prices
        # In a real engine, this runs on tick data. Here, we run on "read" operations.
        
        dirty = False
        for order in self.orders:
            if order['status'] != 'new':
                continue
                
            symbol = order['symbol']
            price = self._get_price(symbol)
            qty = order['qty']
            side = order['side']
            type = order['type']
            limit_price = order.get('limit_price') # Should be stored
            
            # Logic
            triggered = False
            
            if type == "limit":
                if side == "buy" and price <= limit_price:
                    triggered = True
                elif side == "sell" and price >= limit_price:
                    triggered = True
                    
            # Execute fill if triggered
            if triggered:
                cost = qty * price
                if side == "buy":
                    if self.cash >= cost:
                        self.cash -= cost
                        self._update_position(symbol, qty, price)
                        order['status'] = 'filled'
                        order['filled_avg_price'] = price
                        order['filled_qty'] = qty
                        order['filled_at'] = datetime.now().isoformat()
                        self._record_trade(order, price)
                        dirty = True
                    else:
                        order['status'] = 'rejected' # NSF
                        dirty = True
                elif side == "sell":
                    # Check position
                    pos = self.positions.get(symbol, {'qty': 0})
                    if pos['qty'] >= qty:
                        self.cash += cost
                        self._update_position(symbol, -qty, price)
                        order['status'] = 'filled'
                        order['filled_avg_price'] = price
                        order['filled_qty'] = qty
                        order['filled_at'] = datetime.now().isoformat()
                        self._record_trade(order, price)
                        dirty = True
                    else:
                        order['status'] = 'rejected'
                        dirty = True
                        
        if dirty:
            self._save_state(user_id=self.default_user_id) # Default for random background matching

    def _record_trade(self, order, fill_price):
        """
        Record filled order as a Trade in DB + Snapshot
        """
        from database.models import Trade, TradeSnapshot
        session = self.db
        try:
             user_id = "00000000-0000-0000-0000-000000000000"
             
             # Create Trade record
             trade = Trade(
                 id=order['id'], # Use order ID or new UUID? Re-use order ID for simplicity
                 user_id=user_id,
                 source='sandbox',
                 symbol=order['symbol'],
                 side=order['side'],
                 qty=order['qty'],
                 entry_price=fill_price,
                 entry_time=datetime.fromisoformat(order['filled_at']),
                 status='open' # Logic for closing trades is complex (FIFO), treating all as entries or simple
             )
             session.add(trade)
             
             # Capture Snapshot
             snapshot_data = self._capture_snapshot_data(order['id'], order['symbol'], fill_price)
             
             snapshot = TradeSnapshot(
                 trade_id=trade.id,
                 ohlcv_data=snapshot_data['ohlcv'],
                 technical_indicators=snapshot_data['indicators'],
                 news_headlines=snapshot_data['news'],
                 market_regime="trending" # Mock
             )
             session.add(snapshot)
             
             session.commit()
             # Cache snapshot in memory for fast replay access if needed
             self.snapshots[order['id']] = snapshot_data
        except Exception as e:
            session.rollback()
            print(f"Failed to record trade: {e}")
        finally:
            session.close()

    def get_account(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        
        # If user_id provided, ensure we load THAT state
        target_uid = user_id or self.default_user_id
        # In a real system, we'd use a per-request context or something.
        # But for this simple adapter, let's just make sure we load the right state if it differs
        # This is inefficient (reloading on every call) but safe for multi-user demo
        self._load_state(target_uid) 
        
        self._match_orders() # Run matching engine before generating snapshot
        
        equity = self.cash
        for sym, pos in self.positions.items():
            current_price = self._get_price(sym)
            equity += pos['qty'] * current_price
            
        return {
            "status": "ACTIVE",
            "buying_power": self.cash * 4,
            "cash": self.cash,
            "portfolio_value": equity,
            "currency": "USD",
            "daytrade_count": 0,
            "equity": equity
        }

    def get_positions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        target_uid = user_id or self.default_user_id
        self._load_state(target_uid)
        
        self._match_orders() # Run matching
        pos_list = []
        for sym, pos in self.positions.items():
            if pos['qty'] == 0:
                continue
                
            current_price = self._get_price(sym)
            market_value = pos['qty'] * current_price
            cost_basis = pos['qty'] * pos['avg_entry_price']
            unrealized_pl = market_value - cost_basis
            unrealized_plpc = (unrealized_pl / cost_basis) if cost_basis != 0 else 0
            
            pos_list.append({
                "symbol": sym,
                "qty": pos['qty'],
                "side": "long" if pos['qty'] > 0 else "short",
                "market_value": market_value,
                "avg_entry_price": pos['avg_entry_price'],
                "current_price": current_price,
                "unrealized_pl": unrealized_pl,
                "unrealized_plpc": unrealized_plpc
            })
        return pos_list

    def list_orders(self, status: str = "all", limit: int = 50, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        target_uid = user_id or self.default_user_id
        self._load_state(target_uid)
        
        # This memory store is simple, just return reversed list
        filtered = [o for o in self.orders if status == 'all' or o['status'] == status]
        return sorted(filtered, key=lambda x: x['created_at'], reverse=True)[:limit]

    def submit_order(self, symbol: str, qty: float, side: str, type: str, 
                     time_in_force: str = "day", limit_price: Optional[float] = None,
                     user_id: Optional[str] = None) -> Dict[str, Any]:
        
        # Ensure we have the correct user's state loaded
        target_uid = user_id or self.default_user_id
        self._load_state(target_uid)
        
        order_id = str(uuid.uuid4())
        created_at = datetime.now()
        price = self._get_price(symbol)
        
        # Simple Execution Engine: Market orders fill immediately
        status = "new"
        filled_qty = 0.0
        filled_avg_price = 0.0
        
        # Validate buying power for buys
        if side == "buy":
             cost = qty * price
             if cost > self.cash:
                 raise ValueError(f"Insufficient buying power. Required: ${cost:.2f}, Available: ${self.cash:.2f}")

        if type == "market":
            # Slippage Simulation: 0.1% to 0.5% against the trader
            # Buy: Price goes UP. Sell: Price goes DOWN.
            slippage_pct = random.uniform(0.001, 0.005) 
            if side == "buy":
                price = price * (1 + slippage_pct)
            else:
                price = price * (1 - slippage_pct)
            
            # Execute immediately
            status = "filled"
            filled_qty = qty
            filled_avg_price = price
            filled_at_str = created_at.isoformat()
            
            cost = qty * price
            
            if side == "buy":
                if self.cash >= cost:
                    self.cash -= cost
                    self._update_position(symbol, qty, price)
                    # Capture Snapshot for immediate fill
                    # self._capture_snapshot(order_id, symbol, price) -> Moved to _record_trade
                else:
                    status = "rejected" # Not enough cash
            elif side == "sell":
                 curr_pos = self.positions.get(symbol, {"qty": 0, "avg_entry_price": 0})
                 if curr_pos["qty"] >= qty:
                     self.cash += cost
                     self._update_position(symbol, -qty, price)
                 else:
                     status = "rejected" 
        else:
            # Pending Order (Limit/Stop)
            status = "new"
            # Logic handled in _match_orders

        order = {
            "id": order_id,
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": type,
            "limit_price": limit_price,
            "status": status,
            "created_at": created_at.isoformat(),
            "filled_qty": filled_qty,
            "filled_avg_price": filled_avg_price,
            "filled_at": filled_at_str if status == 'filled' else None
        }
        self.orders.append(order)
        
        if status == 'filled':
             self._record_trade(order, filled_avg_price)
        
        self._save_state(target_uid) # Persist after order for correct user
        return order
        
    def _update_position(self, symbol: str, qty_delta: float, price: float):
        if symbol not in self.positions:
            self.positions[symbol] = {"qty": 0.0, "avg_entry_price": 0.0}
            
        pos = self.positions[symbol]
        new_qty = pos["qty"] + qty_delta
        
        if new_qty == 0:
            del self.positions[symbol]
            return

        # FIFO/Weighted Average Cost Basis implementation is complex. 
        # Using Weighted Average for simplicity on BUYs.
        if qty_delta > 0: # Buy
            total_current_cost = pos["qty"] * pos["avg_entry_price"]
            new_cost = qty_delta * price
            pos["avg_entry_price"] = (total_current_cost + new_cost) / new_qty
            
        pos["qty"] = new_qty
        # On sell, average entry price doesn't change, just quantity reduces (and realize P&L logic normally happens here)

    def get_portfolio_history(self, period: str = "1M", timeframe: str = "1D") -> List[Dict[str, Any]]:
        # Mock history for simulation
        # In a real app, we would snapshot equity daily
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        base_equity = self.start_cash
        
        data = []
        for i, date in enumerate(dates):
            # Mock random equity curve
            equity = base_equity * (1 + (random.uniform(-0.05, 0.05) * (i/30)))
            data.append({
                "time": date.isoformat(),
                "equity": equity,
                "profit_loss": equity - self.start_cash,
                "profit_loss_pct": (equity - self.start_cash) / self.start_cash,
                "returns": random.uniform(-0.01, 0.01)
            })
        return data

    def get_bars(self, symbol: str, timeframe: str = "1Min", limit: int = 100) -> List[Dict[str, Any]]:
        # Try to get real data from yfinance first
        try:
            # Map timeframe to yfinance interval
            interval_map = {
                "1Min": "1m",
                "5Min": "5m",
                "15Min": "15m",
                "1H": "1h",
                "1D": "1d"
            }
            interval = interval_map.get(timeframe, "1m")
            
            # Fetch data
            ticker = yf.Ticker(symbol)
            # Fetch slightly more to ensure we have enough after filtering/processing if needed
            # For 'limit', yfinance history allows period argument, but to get exact limit lines 
            # we might need to fetch a period and tail it.
            # 1m data is limited to 7d usually.
            period = "5d" if timeframe == "1Min" else "1mo"
            df = ticker.history(period=period, interval=interval)
            
            if not df.empty:
                # Take the last 'limit' rows
                df = df.tail(limit)
                
                data = []
                for index, row in df.iterrows():
                    data.append({
                        "time": index.isoformat(),
                        "open": row['Open'],
                        "high": row['High'],
                        "low": row['Low'],
                        "close": row['Close'],
                        "volume": row['Volume']
                    })
                return data
                
        except Exception as e:
            print(f"⚠️ Failed to fetch real history for {symbol}: {e}. Falling back to mock.")

        # Fallback: Mock Bar Generator
        now = datetime.now()
        time_delta = pd.Timedelta(minutes=1) # Default to 1m for mock
        
        start_time = now - (time_delta * limit)
        dates = pd.date_range(start=start_time, periods=limit, freq='T')
        
        base_price = self._get_price(symbol)
        data = []
        
        current = base_price
        for date in dates:
            o = current
            c = current * (1 + random.uniform(-0.002, 0.002))
            h = max(o, c) * (1 + random.uniform(0, 0.001))
            l = min(o, c) * (1 - random.uniform(0, 0.001))
            v = random.randint(100, 10000)
            
            data.append({
                "time": date.isoformat(),
                "open": o,
                "high": h,
                "low": l,
                "close": c,
                "volume": v
            })
            current = c
            
        return data
            
    
    def _capture_snapshot_data(self, order_id: str, symbol: str, fill_price: float):
        """
        Captures market state at the moment of fill for Replay Engine.
        Returns the snapshot dict.
        """
        snapshot = {
            "order_id": order_id,
            "symbol": symbol,
            "fill_price": fill_price,
            "timestamp": datetime.now().isoformat(),
            "ohlcv": self.get_bars(symbol, limit=20), # Store last 20 bars context
            "indicators": {
                "rsi": random.uniform(30, 70), # Mocked for now
                "macd": {"line": 0.5, "signal": 0.4, "hist": 0.1}
            },
            "news": [
                {"headline": "Market moving on Fed news", "source": "Bloomberg", "time": "10:00 AM"},
                {"headline": "Tech sector rally continues", "source": "Reuters", "time": "10:15 AM"}
            ]
        }
        return snapshot

    def get_trade_snapshot(self, order_id: str) -> Dict[str, Any]:
        return self.snapshots.get(order_id, {})
