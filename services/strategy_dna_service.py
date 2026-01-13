"""
Strategy DNA Service
Auto-clusters trades into strategy fingerprints.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
import numpy as np
from collections import defaultdict
from database.models import Trade, TradeSnapshot, StrategyFingerprint
from database.database import SessionLocal


class StrategyDNAService:
    """
    Clusters trades into distinct strategy profiles (fingerprints).
    Uses feature extraction and simple clustering to identify trading patterns.
    """
    
    ENTRY_STYLES = ['momentum', 'mean_reversion', 'breakout', 'scalping', 'swing']
    VOLATILITY_PREFS = ['low', 'medium', 'high']
    
    def __init__(self, db: Optional[Session] = None):
        self._db = db
    
    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def build_fingerprints(self, user_id: str, min_trades: int = 5) -> List[Dict[str, Any]]:
        """
        Build strategy fingerprints from user's trade history.
        Clusters similar trades and generates strategy profiles.
        """
        db = self.db
        
        # Get all closed trades
        trades = db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.status == 'closed'
        ).all()
        
        if len(trades) < min_trades:
            return []
        
        # Extract features for each trade
        trade_features = []
        for trade in trades:
            features = self._extract_trade_features(trade)
            if features:
                trade_features.append({
                    'trade': trade,
                    'features': features
                })
        
        if len(trade_features) < min_trades:
            return []
        
        # Cluster trades
        clusters = self._cluster_trades(trade_features)
        
        # Generate fingerprint for each cluster
        fingerprints = []
        
        # Clear old fingerprints for this user
        db.query(StrategyFingerprint).filter(
            StrategyFingerprint.user_id == user_id
        ).delete()
        
        for i, cluster in enumerate(clusters):
            if len(cluster) < 3:  # Skip tiny clusters
                continue
            
            fingerprint = self._generate_fingerprint(cluster, user_id, i)
            
            # Persist
            fp = StrategyFingerprint(
                user_id=user_id,
                strategy_name=fingerprint['strategy_name'],
                entry_style=fingerprint['entry_style'],
                holding_time_avg=fingerprint['holding_time_avg'],
                volatility_preference=fingerprint['volatility_preference'],
                win_rate=fingerprint['win_rate'],
                risk_reward_ratio=fingerprint['risk_reward_ratio'],
                avg_pnl=fingerprint['avg_pnl'],
                total_pnl=fingerprint['total_pnl'],
                trade_count=fingerprint['trade_count'],
                trade_ids=fingerprint['trade_ids'],
                feature_vector=fingerprint['feature_vector'],
                is_active=True,
                last_trade_at=fingerprint['last_trade_at']
            )
            db.add(fp)
            fingerprints.append(fingerprint)
        
        db.commit()
        return fingerprints
    
    def _extract_trade_features(self, trade: Trade) -> Optional[Dict[str, float]]:
        """
        Extract normalized features from a trade for clustering.
        """
        try:
            pnl = float(trade.pnl) if trade.pnl else 0
            pnl_pct = float(trade.pnl_pct) if trade.pnl_pct else 0
            hold_time = trade.holding_time_seconds or 0
            qty = float(trade.qty)
            entry_price = float(trade.entry_price)
            
            # Get snapshot for indicators
            snapshot = trade.snapshot
            indicators = snapshot.technical_indicators if snapshot else {}
            
            rsi = indicators.get('rsi', 50) if isinstance(indicators, dict) else 50
            
            # Normalize features
            return {
                # Holding time category (0=scalp, 1=day, 2=swing)
                'hold_time_cat': self._categorize_hold_time(hold_time),
                # P/L direction (-1, 0, 1)
                'pnl_direction': 1 if pnl > 0 else (-1 if pnl < 0 else 0),
                # Position size relative (0-1 normalized)
                'position_value': qty * entry_price,
                # RSI at entry (30-70 range)
                'entry_rsi': rsi,
                # Side (0=sell, 1=buy)
                'side': 1 if trade.side == 'buy' else 0,
                # Time of day (0-23)
                'entry_hour': trade.entry_time.hour if trade.entry_time else 12
            }
        except Exception:
            return None
    
    def _categorize_hold_time(self, seconds: int) -> int:
        """Categorize holding time."""
        if seconds < 300:  # < 5 min
            return 0  # Scalping
        elif seconds < 3600:  # < 1 hour
            return 1  # Day trading
        elif seconds < 86400:  # < 1 day
            return 2  # Swing
        else:
            return 3  # Position
    
    def _cluster_trades(self, trade_features: List[Dict]) -> List[List[Dict]]:
        """
        Simple clustering based on key features.
        Uses rule-based clustering for interpretability.
        """
        clusters = defaultdict(list)
        
        for tf in trade_features:
            features = tf['features']
            
            # Create cluster key based on main characteristics
            hold_cat = features['hold_time_cat']
            
            # Determine entry style from RSI
            rsi = features['entry_rsi']
            if rsi > 60:
                entry_style = 'momentum'
            elif rsi < 40:
                entry_style = 'mean_reversion'
            elif hold_cat == 0:
                entry_style = 'scalping'
            else:
                entry_style = 'breakout'
            
            # Cluster key
            key = f"{hold_cat}_{entry_style}"
            clusters[key].append(tf)
        
        return list(clusters.values())
    
    def _generate_fingerprint(self, cluster: List[Dict], user_id: str, 
                               cluster_idx: int) -> Dict[str, Any]:
        """
        Generate a strategy fingerprint from a cluster of trades.
        """
        trades = [tf['trade'] for tf in cluster]
        features = [tf['features'] for tf in cluster]
        
        # Calculate metrics
        pnls = [float(t.pnl) if t.pnl else 0 for t in trades]
        winning_trades = len([p for p in pnls if p > 0])
        losing_trades = len([p for p in pnls if p < 0])
        
        win_rate = (winning_trades / len(trades)) * 100 if trades else 0
        
        avg_win = np.mean([p for p in pnls if p > 0]) if winning_trades else 0
        avg_loss = abs(np.mean([p for p in pnls if p < 0])) if losing_trades else 1
        risk_reward = avg_win / avg_loss if avg_loss > 0 else 0
        
        avg_hold_time = np.mean([t.holding_time_seconds or 0 for t in trades])
        
        # Determine entry style
        avg_rsi = np.mean([f['entry_rsi'] for f in features])
        if avg_rsi > 60:
            entry_style = 'momentum'
        elif avg_rsi < 40:
            entry_style = 'mean_reversion'
        elif avg_hold_time < 300:
            entry_style = 'scalping'
        elif avg_hold_time < 3600:
            entry_style = 'breakout'
        else:
            entry_style = 'swing'
        
        # Determine volatility preference from position values
        position_values = [f['position_value'] for f in features]
        avg_position = np.mean(position_values)
        if avg_position > 50000:
            vol_pref = 'high'
        elif avg_position > 10000:
            vol_pref = 'medium'
        else:
            vol_pref = 'low'
        
        # Generate name
        strategy_name = self._generate_strategy_name(entry_style, win_rate, avg_hold_time)
        
        return {
            'strategy_name': strategy_name,
            'entry_style': entry_style,
            'holding_time_avg': int(avg_hold_time),
            'volatility_preference': vol_pref,
            'win_rate': round(win_rate, 2),
            'risk_reward_ratio': round(risk_reward, 2),
            'avg_pnl': round(np.mean(pnls), 2),
            'total_pnl': round(sum(pnls), 2),
            'trade_count': len(trades),
            'trade_ids': [t.id for t in trades],
            'feature_vector': {
                'avg_rsi': round(avg_rsi, 2),
                'avg_position_value': round(avg_position, 2),
                'avg_hold_time': round(avg_hold_time, 2)
            },
            'last_trade_at': max(t.created_at for t in trades if t.created_at)
        }
    
    def _generate_strategy_name(self, entry_style: str, win_rate: float, 
                                 hold_time: float) -> str:
        """Generate human-readable strategy name."""
        
        # Performance tier
        if win_rate >= 60:
            tier = "Strong"
        elif win_rate >= 45:
            tier = "Balanced"
        else:
            tier = "Developing"
        
        # Time frame
        if hold_time < 300:
            timeframe = "Scalp"
        elif hold_time < 3600:
            timeframe = "Intraday"
        elif hold_time < 86400:
            timeframe = "Swing"
        else:
            timeframe = "Position"
        
        style_map = {
            'momentum': 'Momentum',
            'mean_reversion': 'Mean Reversion',
            'breakout': 'Breakout',
            'scalping': 'Scalping',
            'swing': 'Trend Following'
        }
        
        return f"{tier} {timeframe} {style_map.get(entry_style, entry_style)}"
    
    def get_fingerprints(self, user_id: str) -> List[Dict[str, Any]]:
        """Get existing fingerprints for a user."""
        db = self.db
        
        fingerprints = db.query(StrategyFingerprint).filter(
            StrategyFingerprint.user_id == user_id,
            StrategyFingerprint.is_active == True
        ).order_by(desc(StrategyFingerprint.trade_count)).all()
        
        return [
            {
                'id': fp.id,
                'strategy_name': fp.strategy_name,
                'entry_style': fp.entry_style,
                'holding_time_avg': fp.holding_time_avg,
                'volatility_preference': fp.volatility_preference,
                'win_rate': float(fp.win_rate) if fp.win_rate else 0,
                'risk_reward_ratio': float(fp.risk_reward_ratio) if fp.risk_reward_ratio else 0,
                'avg_pnl': float(fp.avg_pnl) if fp.avg_pnl else 0,
                'total_pnl': float(fp.total_pnl) if fp.total_pnl else 0,
                'trade_count': fp.trade_count,
                'trade_ids': fp.trade_ids,
                'feature_vector': fp.feature_vector,
                'last_trade_at': fp.last_trade_at.isoformat() if fp.last_trade_at else None,
                'created_at': fp.created_at.isoformat() if fp.created_at else None
            }
            for fp in fingerprints
        ]
    
    def check_order_compatibility(
        self, 
        user_id: str, 
        symbol: str, 
        side: str, 
        order_type: str,
        qty: float,
        current_time_hour: int = None
    ) -> Dict[str, Any]:
        """
        Check if a proposed order is compatible with user's Strategy DNA.
        Uses Cosine Similarity between proposed trade vector and fingerprint vectors.
        """
        fingerprints = self.get_fingerprints(user_id)
        
        if not fingerprints:
            return {
                "is_compatible": True,
                "compatibility_score": 100,
                "warning": None,
                "matched_strategy": None
            }
        
        # 1. Fetch Market Context (RSI, Price)
        try:
            # We need current price to calc Position Value, and RSI for Strategy Type
            context = self._fetch_market_context(symbol)
            current_rsi = context.get('rsi', 50)
            current_price = context.get('price', 100)
            
            # 2. Construct Trade Vector
            # Vector: [RSI_Normalized, Position_Log_Normalized]
            # RSI is 0-100. Position can be 100 - 1M. Log scale helps.
            
            position_value = qty * current_price
            
            # Normalize inputs roughly to 0-1 or similar scale for simple distance
            # RSI: 0-100.
            # Position: We'll use Log10(pos_value) which is approx 3-6. Multiply by 15 to get ~45-90 range?
            # actually better to just compare RSI vs RSI and Pos vs Pos separately or use normalized distance.
            
            # Simple Euclidean distance for MVP stability
            # Distance = sqrt( (rsi1-rsi2)^2 + w*(pos1-pos2)^2 )
            
        except Exception as e:
            print(f"Error fetching context for compatibility: {e}")
            # Fallback if market data fails
            return {
                "is_compatible": True,
                "compatibility_score": 100,
                "warning": "Market data unavailable for check",
                "matched_strategy": None
            }

        scores = []
        
        for fp in fingerprints:
            # Extract fingerprint features
            fp_rsi = fp['feature_vector'].get('avg_rsi', 50)
            fp_pos = fp['feature_vector'].get('avg_position_value', 0)
            
            # 1. RSI Similarity (100 - delta)
            rsi_diff = abs(current_rsi - fp_rsi)
            rsi_score = max(0, 100 - (rsi_diff * 1.5)) # Penalize deviation
            
            # 2. Position Sizing Similarity
            # Use ratio: min/max
            if fp_pos > 0 and position_value > 0:
                pos_ratio = min(fp_pos, position_value) / max(fp_pos, position_value)
                pos_score = pos_ratio * 100
            else:
                pos_score = 50 # Default if 0
                
            # Weighted Score: RSI (Entry Logic) matters more (70%) than size (30%)
            final_score = (rsi_score * 0.7) + (pos_score * 0.3)
            
            scores.append({
                "strategy_name": fp['strategy_name'],
                "score": final_score,
                "details": f"RSI: {current_rsi:.1f} vs {fp_rsi:.1f}, Size: ${int(position_value)} vs ${int(fp_pos)}"
            })
            
        # Select best match
        best_match = max(scores, key=lambda x: x['score'])
        
        # Threshold
        is_compatible = best_match['score'] > 60
        
        return {
            "is_compatible": is_compatible,
            "compatibility_score": int(best_match['score']),
            "warning": None if is_compatible else f"Does not match '{best_match['strategy_name']}' (Score: {int(best_match['score'])})",
            "matched_strategy": best_match['strategy_name'],
            "analysis": best_match['details']
        }

    def _fetch_market_context(self, symbol: str) -> Dict[str, float]:
        """Fetch current price and calculate 14-period RSI."""
        import yfinance as yf
        import pandas as pd
        import pandas_ta as ta  # Assuming pandas_ta is installed, else manual calculation
        
        try:
            # Fetch 1mo hourly data to allow RSI calc
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1mo", interval="1h")
            
            if df.empty:
                return {}
                
            current_price = df['Close'].iloc[-1]
            
            # Calculate RSI Manual (Dependency-free fallback)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_series = 100 - (100 / (1 + rs))
            current_rsi = rsi_series.iloc[-1]
            
            if pd.isna(current_rsi): # if not enough data
                 current_rsi = 50

            return {
                "price": current_price,
                "rsi": current_rsi
            }
        except Exception as e:
            print(f"Data fetch error: {e}")
            return {}


    def close(self):
        if self._db:
            self._db.close()
            self._db = None
