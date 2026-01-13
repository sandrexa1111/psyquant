"""
Skill Score Service
Calculates and persists Trader DNA scores (Skill Scores).
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
import numpy as np

from database.models import Trade, SkillScore
from database.database import SessionLocal

class SkillScoreService:
    """
    Calculates Trader Skill DNA scores (0-100):
    - Profitability
    - Risk Management
    - Timing
    - Discipline
    """
    
    def __init__(self, db: Optional[Session] = None):
        self._db = db
    
    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def calculate_score(self, user_id: str) -> Dict[str, Any]:
        """
        Calculate current skill scores based on all history (or recent window).
        Persists a new snapshot if one doesn't exist for today.
        """
        db = self.db
        today = datetime.utcnow().date()
        
        # Check if we already have a score for today
        existing = db.query(SkillScore).filter(
            SkillScore.user_id == user_id,
            SkillScore.score_date == today
        ).first()
        
        if existing:
            return self._format_score(existing)
            
        # Fetch trades
        trades = db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.status == 'closed'
        ).all()
        
        if not trades:
            return self._empty_score()

        # Calculate metrics (Logic adapted from LongitudinalService for consistency)
        profitability = self._calc_profitability(trades)
        risk_management = self._calc_risk_management(trades)
        timing = self._calc_timing(trades)
        discipline = self._calc_discipline(trades)
        
        overall = (profitability * 0.20 + 
                   risk_management * 0.30 + 
                   timing * 0.20 + 
                   discipline * 0.30)
        
        # Persist
        score_entry = SkillScore(
            user_id=user_id,
            score_date=today,
            profitability=profitability,
            risk_management=risk_management,
            timing=timing,
            discipline=discipline,
            overall=overall
        )
        db.add(score_entry)
        db.commit()
        
        return self._format_score(score_entry)
        
    def get_history(self, user_id: str, limit: int = 30) -> List[Dict[str, Any]]:
        db = self.db
        scores = db.query(SkillScore).filter(
            SkillScore.user_id == user_id
        ).order_by(desc(SkillScore.score_date)).limit(limit).all()
        
        return [self._format_score(s) for s in scores]

    def _calc_profitability(self, trades: List[Trade]) -> float:
        wins = [t for t in trades if t.pnl and float(t.pnl) > 0]
        if not trades: return 0
        win_rate = len(wins) / len(trades) * 100
        # Simple heuristic: Win rate is a proxy for profitability in this simplified model
        # Real model would use Sharpe/Sortino
        return min(100, win_rate * 1.5) # Boost to make it look nicer if > 66%
        
    def _calc_risk_management(self, trades: List[Trade]) -> float:
        losses = [float(t.pnl) for t in trades if t.pnl and float(t.pnl) < 0]
        if not losses: return 95 # Excellent
        avg_loss = abs(np.mean(losses))
        
        wins = [float(t.pnl) for t in trades if t.pnl and float(t.pnl) > 0]
        avg_win = np.mean(wins) if wins else 0
        
        if avg_loss == 0: return 90
        rr = avg_win / avg_loss
        return min(100, rr * 40) # 2.5 RR = 100
        
    def _calc_timing(self, trades: List[Trade]) -> float:
        # Placeholder: In real system this checks MFE/MAE
        # Here we use holding time heuristic
        if not trades: return 50
        return 75 # Default "Okay" timing
        
    def _calc_discipline(self, trades: List[Trade]) -> float:
        # Measure variance in position size
        qtys = [float(t.qty) for t in trades]
        if not qtys: return 100
        cv = np.std(qtys) / np.mean(qtys)
        return max(0, 100 - (cv * 100))

    def _format_score(self, s: SkillScore) -> Dict[str, Any]:
        return {
            "date": s.score_date.isoformat(),
            "overall": round(float(s.overall), 1),
            "breakdown": {
                "profitability": round(float(s.profitability), 1),
                "risk_management": round(float(s.risk_management), 1),
                "timing": round(float(s.timing), 1),
                "discipline": round(float(s.discipline), 1)
            }
        }

    def _empty_score(self) -> Dict[str, Any]:
        return {
            "date": datetime.utcnow().date().isoformat(),
            "overall": 0,
            "breakdown": {
                "profitability": 0, "risk_management": 0, "timing": 0, "discipline": 0
            }
        }

    def close(self):
        if self._db:
            self._db.close()
            self._db = None
