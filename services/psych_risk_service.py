"""
Psychological Risk Score (PRS) Service
Calculates risk score based on trading behavior patterns.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
import numpy as np
from database.models import Trade, PsychRiskSnapshot
from database.database import SessionLocal


class PsychRiskScoreService:
    """
    Calculates Psychological Risk Score (PRS) from 0-100.
    
    Factors:
    - Loss streak severity
    - Position sizing deviation from norm
    - Trade frequency changes
    - Holding time anomalies
    """
    
    RISK_STATES = {
        (0, 25): 'low',
        (25, 50): 'moderate', 
        (50, 75): 'high',
        (75, 100): 'critical'
    }
    
    def __init__(self, db: Optional[Session] = None):
        self._db = db
    
    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def calculate_prs(self, user_id: str, lookback_days: int = 30) -> Dict[str, Any]:
        """
        Calculate the current Psychological Risk Score for a user.
        """
        db = self.db
        
        # Get trades in lookback window
        cutoff = datetime.now() - timedelta(days=lookback_days)
        trades = db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.created_at >= cutoff
        ).order_by(desc(Trade.created_at)).all()
        
        if not trades:
            return self._empty_prs_result()
        
        # Calculate individual factors (each 0-100)
        loss_streak_factor = self._calc_loss_streak_factor(trades)
        position_deviation_factor = self._calc_position_deviation_factor(trades)
        frequency_change_factor = self._calc_frequency_change_factor(trades, cutoff)
        holding_anomaly_factor = self._calc_holding_anomaly_factor(trades)
        
        # Weighted combination
        weights = {
            'loss_streak': 0.35,
            'position_deviation': 0.25,
            'frequency_change': 0.20,
            'holding_anomaly': 0.20
        }
        
        score = int(
            loss_streak_factor * weights['loss_streak'] +
            position_deviation_factor * weights['position_deviation'] +
            frequency_change_factor * weights['frequency_change'] +
            holding_anomaly_factor * weights['holding_anomaly']
        )
        
        score = max(0, min(100, score))
        risk_state = self._classify_risk_state(score)
        
        # Create snapshot
        factors = {
            'loss_streak': loss_streak_factor,
            'position_deviation': position_deviation_factor,
            'frequency_change': frequency_change_factor,
            'holding_anomaly': holding_anomaly_factor
        }
        
        snapshot = PsychRiskSnapshot(
            user_id=user_id,
            score=score,
            risk_state=risk_state,
            factors=factors,
            trade_window_start=cutoff,
            trade_window_end=datetime.now(),
            trades_analyzed=len(trades)
        )
        
        db.add(snapshot)
        db.commit()
        
        return {
            'score': score,
            'risk_state': risk_state,
            'factors': factors,
            'trades_analyzed': len(trades),
            'lookback_days': lookback_days,
            'snapshot_id': snapshot.id
        }
    
    def _calc_loss_streak_factor(self, trades: List[Trade]) -> float:
        """
        Calculate risk factor from consecutive losses.
        More consecutive losses = higher risk.
        """
        if not trades:
            return 0.0
        
        current_streak = 0
        max_streak = 0
        
        for trade in trades:
            pnl = float(trade.pnl) if trade.pnl else 0
            if pnl < 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        # Check if currently in a loss streak
        recent_streak = 0
        for trade in trades[:5]:  # Check last 5 trades
            pnl = float(trade.pnl) if trade.pnl else 0
            if pnl < 0:
                recent_streak += 1
            else:
                break
        
        # Score: 0 streak = 0, 3+ streak = 60-100
        streak_score = min(100, recent_streak * 25)
        max_streak_penalty = min(40, max_streak * 8)
        
        return min(100, streak_score + max_streak_penalty * 0.3)
    
    def _calc_position_deviation_factor(self, trades: List[Trade]) -> float:
        """
        Calculate risk from position size deviations.
        Sudden large positions after losses indicate revenge trading.
        """
        if len(trades) < 3:
            return 0.0
        
        position_sizes = [float(t.qty) * float(t.entry_price) for t in trades]
        
        if not position_sizes:
            return 0.0
        
        mean_size = np.mean(position_sizes)
        std_size = np.std(position_sizes) if len(position_sizes) > 1 else 0
        
        if mean_size == 0 or std_size == 0:
            return 0.0
        
        # Check for deviation in recent trades
        recent_sizes = position_sizes[:5]
        recent_mean = np.mean(recent_sizes)
        
        deviation_ratio = abs(recent_mean - mean_size) / mean_size if mean_size > 0 else 0
        
        # 50% deviation = 50 score, 100%+ = 100
        return min(100, deviation_ratio * 100)
    
    def _calc_frequency_change_factor(self, trades: List[Trade], 
                                       cutoff: datetime) -> float:
        """
        Calculate risk from trading frequency changes.
        Sudden increase in trading often indicates emotional trading.
        """
        if len(trades) < 5:
            return 0.0
        
        # Split into recent and historical
        mid_point = len(trades) // 2
        recent_trades = trades[:mid_point]
        older_trades = trades[mid_point:]
        
        if not recent_trades or not older_trades:
            return 0.0
        
        # Calculate trades per day
        def trades_per_day(trade_list: List[Trade]) -> float:
            if len(trade_list) < 2:
                return 0
            times = [t.created_at for t in trade_list if t.created_at]
            if len(times) < 2:
                return 0
            span = (max(times) - min(times)).days or 1
            return len(trade_list) / span
        
        recent_freq = trades_per_day(recent_trades)
        older_freq = trades_per_day(older_trades)
        
        if older_freq == 0:
            return 0.0
        
        # Increase in frequency indicates risk
        freq_increase = (recent_freq - older_freq) / older_freq if older_freq > 0 else 0
        
        # 50% increase = 50 score
        return min(100, max(0, freq_increase * 100))
    
    def _calc_holding_anomaly_factor(self, trades: List[Trade]) -> float:
        """
        Calculate risk from holding time anomalies.
        Cutting winners short and holding losers long is a risk indicator.
        """
        if len(trades) < 3:
            return 0.0
        
        winning_hold_times = []
        losing_hold_times = []
        
        for trade in trades:
            pnl = float(trade.pnl) if trade.pnl else 0
            hold_time = trade.holding_time_seconds or 0
            
            if pnl > 0:
                winning_hold_times.append(hold_time)
            elif pnl < 0:
                losing_hold_times.append(hold_time)
        
        if not winning_hold_times or not losing_hold_times:
            return 0.0
        
        avg_win_hold = np.mean(winning_hold_times)
        avg_loss_hold = np.mean(losing_hold_times)
        
        # Holding losers longer than winners is bad
        if avg_win_hold == 0:
            return 0.0
        
        hold_ratio = avg_loss_hold / avg_win_hold if avg_win_hold > 0 else 1
        
        # Ratio > 2 means holding losers 2x longer = high risk
        if hold_ratio > 1:
            return min(100, (hold_ratio - 1) * 50)
        
        return 0.0
    
    def _classify_risk_state(self, score: int) -> str:
        """Classify score into risk state."""
        for (low, high), state in self.RISK_STATES.items():
            if low <= score < high:
                return state
        return 'critical'
    
    def _empty_prs_result(self) -> Dict[str, Any]:
        """Return empty result when no trades."""
        return {
            'score': 0,
            'risk_state': 'low',
            'factors': {
                'loss_streak': 0,
                'position_deviation': 0,
                'frequency_change': 0,
                'holding_anomaly': 0
            },
            'trades_analyzed': 0,
            'lookback_days': 30,
            'snapshot_id': None
        }
    
    def get_prs_history(self, user_id: str, limit: int = 30) -> List[Dict[str, Any]]:
        """Get historical PRS snapshots."""
        db = self.db
        
        snapshots = db.query(PsychRiskSnapshot).filter(
            PsychRiskSnapshot.user_id == user_id
        ).order_by(desc(PsychRiskSnapshot.created_at)).limit(limit).all()
        
        return [
            {
                'id': s.id,
                'score': s.score,
                'risk_state': s.risk_state,
                'factors': s.factors,
                'trades_analyzed': s.trades_analyzed,
                'created_at': s.created_at.isoformat() if s.created_at else None
            }
            for s in snapshots
        ]
    
    def close(self):
        if self._db:
            self._db.close()
            self._db = None
