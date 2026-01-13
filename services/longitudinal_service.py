"""
Longitudinal Intelligence Service
Tracks behavior evolution, strategy drift, and generates improvement narratives.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import numpy as np

from database.models import (
    Trade, BehaviorEvolution, StrategyDrift, StrategyFingerprint,
    PsychRiskSnapshot, AITradeJudgement, SkillScore
)
from database.database import SessionLocal


class LongitudinalService:
    """
    Provides time-aware behavioral intelligence:
    - Behavior evolution tracking
    - Strategy DNA drift detection
    - Personalized improvement narratives
    - Risk score trend analysis
    """
    
    # Metric weights for composite scoring
    METRIC_WEIGHTS = {
        'discipline': 0.25,
        'risk_management': 0.25,
        'consistency': 0.20,
        'profitability': 0.20,
        'timing': 0.10
    }
    
    def __init__(self, db: Optional[Session] = None):
        self._db = db
    
    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def calculate_behavior_evolution(
        self, 
        user_id: str, 
        period_type: str = 'weekly',
        lookback_periods: int = 12
    ) -> Dict[str, Any]:
        """
        Calculate behavior metric evolution over time.
        
        Args:
            user_id: User to analyze
            period_type: 'daily', 'weekly', or 'monthly'
            lookback_periods: Number of periods to analyze
            
        Returns:
            Dict with metrics, trends, and evolution data
        """
        # Determine period duration
        period_days = {'daily': 1, 'weekly': 7, 'monthly': 30}[period_type]
        
        now = datetime.utcnow()
        evolution_data = []
        
        for i in range(lookback_periods):
            period_end = now - timedelta(days=i * period_days)
            period_start = period_end - timedelta(days=period_days)
            
            # Get trades for this period
            trades = self.db.query(Trade).filter(
                Trade.user_id == user_id,
                Trade.entry_time >= period_start,
                Trade.entry_time < period_end,
                Trade.status == 'closed'
            ).all()
            
            if not trades:
                continue
            
            # Calculate metrics for this period
            metrics = self._calculate_period_metrics(trades, user_id, period_start, period_end)
            
            evolution_data.append({
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat(),
                'period_label': self._get_period_label(period_start, period_type),
                'trades_count': len(trades),
                'metrics': metrics
            })
        
        # Reverse to chronological order
        evolution_data.reverse()
        
        # Calculate trends
        trends = self._calculate_trends(evolution_data)
        
        # Store latest evolution records
        if evolution_data:
            self._store_evolution_records(user_id, evolution_data[-1], period_type)
        
        return {
            'user_id': user_id,
            'period_type': period_type,
            'periods_analyzed': len(evolution_data),
            'evolution': evolution_data,
            'trends': trends,
            'overall_direction': self._determine_overall_direction(trends)
        }
    
    def _calculate_period_metrics(
        self, 
        trades: List[Trade], 
        user_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, float]:
        """Calculate all behavior metrics for a period."""
        
        if not trades:
            return {m: 0 for m in self.METRIC_WEIGHTS.keys()}
        
        # Discipline: Based on position sizing consistency and rule following
        discipline = self._calc_discipline_score(trades)
        
        # Risk Management: Based on loss sizing and stop adherence
        risk_management = self._calc_risk_management_score(trades)
        
        # Consistency: Trade frequency and timing patterns
        consistency = self._calc_consistency_score(trades)
        
        # Profitability: Win rate and risk-reward
        profitability = self._calc_profitability_score(trades)
        
        # Timing: Entry/exit quality
        timing = self._calc_timing_score(trades, user_id, period_start, period_end)
        
        return {
            'discipline': round(discipline, 1),
            'risk_management': round(risk_management, 1),
            'consistency': round(consistency, 1),
            'profitability': round(profitability, 1),
            'timing': round(timing, 1),
            'composite': round(
                discipline * 0.25 + risk_management * 0.25 + 
                consistency * 0.20 + profitability * 0.20 + timing * 0.10, 
                1
            )
        }
    
    def _calc_discipline_score(self, trades: List[Trade]) -> float:
        """
        Discipline = consistent position sizing + avoiding impulsive trades.
        """
        if len(trades) < 2:
            return 50.0
        
        # Position size consistency
        qtys = [float(t.qty) for t in trades]
        mean_qty = np.mean(qtys)
        std_qty = np.std(qtys)
        cv = std_qty / mean_qty if mean_qty > 0 else 0
        
        # Lower coefficient of variation = more disciplined
        size_score = max(0, 100 - cv * 100)
        
        # Check for revenge trading patterns (big trades after losses)
        revenge_penalty = 0
        for i in range(1, len(trades)):
            if trades[i-1].pnl and float(trades[i-1].pnl) < 0:
                if float(trades[i].qty) > mean_qty * 1.5:
                    revenge_penalty += 10
        
        return max(0, min(100, size_score - revenge_penalty))
    
    def _calc_risk_management_score(self, trades: List[Trade]) -> float:
        """
        Risk Management = controlled losses + good risk/reward.
        """
        if not trades:
            return 50.0
        
        losses = [t for t in trades if t.pnl and float(t.pnl) < 0]
        wins = [t for t in trades if t.pnl and float(t.pnl) > 0]
        
        if not losses:
            return 90.0  # No losses is excellent risk management
        
        # Average loss vs average win
        avg_loss = abs(np.mean([float(t.pnl) for t in losses])) if losses else 0
        avg_win = np.mean([float(t.pnl) for t in wins]) if wins else 0
        
        # Risk/reward ratio
        rr_ratio = avg_win / avg_loss if avg_loss > 0 else 2.0
        rr_score = min(100, rr_ratio * 30)  # 3:1 or better = 90+
        
        # Loss size consistency (avoiding blowups)
        if len(losses) > 1:
            loss_values = [abs(float(t.pnl)) for t in losses]
            max_loss = max(loss_values)
            avg_loss_val = np.mean(loss_values)
            blowup_ratio = max_loss / avg_loss_val if avg_loss_val > 0 else 1
            blowup_penalty = max(0, (blowup_ratio - 2) * 20)  # Penalty if max > 2x average
        else:
            blowup_penalty = 0
        
        return max(0, min(100, rr_score - blowup_penalty))
    
    def _calc_consistency_score(self, trades: List[Trade]) -> float:
        """
        Consistency = regular trading rhythm without erratic patterns.
        """
        if len(trades) < 3:
            return 50.0
        
        # Time between trades
        sorted_trades = sorted(trades, key=lambda t: t.entry_time)
        gaps = []
        for i in range(1, len(sorted_trades)):
            gap = (sorted_trades[i].entry_time - sorted_trades[i-1].entry_time).total_seconds() / 3600
            gaps.append(gap)
        
        if not gaps:
            return 50.0
        
        mean_gap = np.mean(gaps)
        std_gap = np.std(gaps)
        cv = std_gap / mean_gap if mean_gap > 0 else 0
        
        # Lower variance = more consistent
        return max(0, min(100, 100 - cv * 30))
    
    def _calc_profitability_score(self, trades: List[Trade]) -> float:
        """
        Profitability = win rate + total P&L performance.
        """
        if not trades:
            return 0.0
        
        wins = sum(1 for t in trades if t.pnl and float(t.pnl) > 0)
        win_rate = wins / len(trades) * 100
        
        total_pnl = sum(float(t.pnl) for t in trades if t.pnl)
        
        # Win rate component (50% weight)
        win_rate_score = win_rate
        
        # P&L component (50% weight) - scaled
        pnl_score = 50 + min(50, max(-50, total_pnl / 100))
        
        return min(100, (win_rate_score * 0.5 + pnl_score * 0.5))
    
    def _calc_timing_score(
        self, 
        trades: List[Trade], 
        user_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> float:
        """
        Timing = quality of entries/exits based on AI judgements.
        """
        # Get AI judgements for these trades
        trade_ids = [t.id for t in trades]
        if not trade_ids:
            return 50.0
        
        judgements = self.db.query(AITradeJudgement).filter(
            AITradeJudgement.trade_id.in_(trade_ids)
        ).all()
        
        if not judgements:
            # Fallback: use holding time analysis
            holding_times = [t.holding_time_seconds for t in trades if t.holding_time_seconds]
            if not holding_times:
                return 50.0
            
            # Moderate holding times are good (not too short, not too long)
            avg_hold = np.mean(holding_times)
            if 300 <= avg_hold <= 3600:  # 5 min to 1 hour
                return 70.0
            elif avg_hold < 60:  # Very short = scalping, may be impulsive
                return 40.0
            else:
                return 55.0
        
        # Use logical scores from AI judgements
        logical_scores = [j.logical_score for j in judgements]
        return np.mean(logical_scores)
    
    def _calculate_trends(self, evolution_data: List[Dict]) -> Dict[str, Any]:
        """Calculate trends for each metric."""
        if len(evolution_data) < 2:
            return {}
        
        trends = {}
        metrics = ['discipline', 'risk_management', 'consistency', 'profitability', 'timing', 'composite']
        
        for metric in metrics:
            values = [e['metrics'].get(metric, 0) for e in evolution_data]
            
            if len(values) >= 2:
                # Simple linear trend
                first_half = np.mean(values[:len(values)//2])
                second_half = np.mean(values[len(values)//2:])
                
                change = second_half - first_half
                change_pct = (change / first_half * 100) if first_half > 0 else 0
                
                if change_pct > 5:
                    direction = 'improving'
                elif change_pct < -5:
                    direction = 'declining'
                else:
                    direction = 'stable'
                
                trends[metric] = {
                    'current': values[-1] if values else 0,
                    'previous': values[-2] if len(values) > 1 else None,
                    'change_pct': round(change_pct, 1),
                    'direction': direction,
                    'values': values
                }
        
        return trends
    
    def _determine_overall_direction(self, trends: Dict) -> str:
        """Determine overall improvement direction."""
        if not trends:
            return 'insufficient_data'
        
        improving = sum(1 for t in trends.values() if t.get('direction') == 'improving')
        declining = sum(1 for t in trends.values() if t.get('direction') == 'declining')
        
        if improving > declining + 1:
            return 'improving'
        elif declining > improving + 1:
            return 'declining'
        else:
            return 'stable'
    
    def _get_period_label(self, dt: datetime, period_type: str) -> str:
        """Generate human-readable period label."""
        if period_type == 'daily':
            return dt.strftime('%b %d')
        elif period_type == 'weekly':
            return f"Week of {dt.strftime('%b %d')}"
        else:
            return dt.strftime('%B %Y')
    
    def _store_evolution_records(
        self, 
        user_id: str, 
        period_data: Dict, 
        period_type: str
    ):
        """Store evolution records in database."""
        for metric, score in period_data['metrics'].items():
            if metric == 'composite':
                continue
            
            evolution = BehaviorEvolution(
                user_id=user_id,
                metric_type=metric,
                score=Decimal(str(score)),
                period_type=period_type,
                period_start=datetime.fromisoformat(period_data['period_start']),
                period_end=datetime.fromisoformat(period_data['period_end']),
                trades_analyzed=period_data['trades_count']
            )
            self.db.add(evolution)
        
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
    
    def detect_strategy_drift(
        self, 
        user_id: str, 
        comparison_days: int = 30
    ) -> Dict[str, Any]:
        """
        Detect changes in trading strategy over time.
        
        Compares recent trading patterns to historical norms.
        """
        now = datetime.utcnow()
        midpoint = now - timedelta(days=comparison_days)
        
        # Get "before" and "after" trades
        old_trades = self.db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.entry_time < midpoint,
            Trade.entry_time >= midpoint - timedelta(days=comparison_days),
            Trade.status == 'closed'
        ).all()
        
        new_trades = self.db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.entry_time >= midpoint,
            Trade.status == 'closed'
        ).all()
        
        if len(old_trades) < 5 or len(new_trades) < 5:
            return {
                'drift_detected': False,
                'reason': 'insufficient_data',
                'old_trades': len(old_trades),
                'new_trades': len(new_trades),
                'min_required': 5
            }
        
        # Calculate characteristics for each period
        old_chars = self._extract_trading_characteristics(old_trades)
        new_chars = self._extract_trading_characteristics(new_trades)
        
        # Calculate drift score
        drift_score, changed_dimensions = self._calculate_drift_score(old_chars, new_chars)
        
        # Classify severity
        if drift_score < 20:
            severity = 'minor'
        elif drift_score < 40:
            severity = 'moderate'
        elif drift_score < 60:
            severity = 'significant'
        else:
            severity = 'major'
        
        # Determine if drift is positive
        old_pnl = sum(float(t.pnl) for t in old_trades if t.pnl)
        new_pnl = sum(float(t.pnl) for t in new_trades if t.pnl)
        is_positive = new_pnl > old_pnl
        
        # Generate interpretation
        interpretation = self._generate_drift_interpretation(
            old_chars, new_chars, changed_dimensions, is_positive
        )
        
        # Store drift record
        drift = StrategyDrift(
            user_id=user_id,
            drift_score=Decimal(str(drift_score)),
            drift_severity=severity,
            old_characteristics=old_chars,
            new_characteristics=new_chars,
            changed_dimensions=changed_dimensions,
            comparison_period_days=comparison_days,
            trades_before=len(old_trades),
            trades_after=len(new_trades),
            interpretation=interpretation,
            is_positive=is_positive
        )
        self.db.add(drift)
        
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
        
        return {
            'drift_detected': drift_score > 15,
            'drift_score': round(drift_score, 1),
            'severity': severity,
            'is_positive': is_positive,
            'old_characteristics': old_chars,
            'new_characteristics': new_chars,
            'changed_dimensions': changed_dimensions,
            'interpretation': interpretation,
            'comparison_period_days': comparison_days,
            'trades_analyzed': {
                'before': len(old_trades),
                'after': len(new_trades)
            }
        }
    
    def _extract_trading_characteristics(self, trades: List[Trade]) -> Dict[str, Any]:
        """Extract key trading characteristics from a set of trades."""
        if not trades:
            return {}
        
        # Basic stats
        qtys = [float(t.qty) for t in trades]
        holding_times = [t.holding_time_seconds for t in trades if t.holding_time_seconds]
        pnls = [float(t.pnl) for t in trades if t.pnl]
        
        wins = sum(1 for p in pnls if p > 0)
        
        return {
            'avg_position_size': round(np.mean(qtys), 2),
            'position_size_std': round(np.std(qtys), 2),
            'avg_holding_time_mins': round(np.mean(holding_times) / 60, 1) if holding_times else 0,
            'holding_time_std': round(np.std(holding_times) / 60, 1) if holding_times else 0,
            'win_rate': round(wins / len(pnls) * 100, 1) if pnls else 0,
            'avg_pnl': round(np.mean(pnls), 2) if pnls else 0,
            'trades_per_day': round(len(trades) / max(1, (trades[-1].entry_time - trades[0].entry_time).days), 1),
            'symbols_traded': len(set(t.symbol for t in trades))
        }
    
    def _calculate_drift_score(
        self, 
        old_chars: Dict, 
        new_chars: Dict
    ) -> tuple:
        """Calculate drift score and identify changed dimensions."""
        changed = []
        total_drift = 0
        
        dimensions = [
            ('avg_position_size', 'Position Size', 30),
            ('avg_holding_time_mins', 'Holding Time', 30),
            ('win_rate', 'Win Rate', 20),
            ('trades_per_day', 'Trade Frequency', 20)
        ]
        
        for key, label, weight in dimensions:
            old_val = old_chars.get(key, 0)
            new_val = new_chars.get(key, 0)
            
            if old_val > 0:
                pct_change = abs(new_val - old_val) / old_val * 100
                if pct_change > 20:  # 20% change is significant
                    changed.append({
                        'dimension': label,
                        'old_value': old_val,
                        'new_value': new_val,
                        'change_pct': round(pct_change, 1),
                        'direction': 'increased' if new_val > old_val else 'decreased'
                    })
                    total_drift += min(100, pct_change) * (weight / 100)
        
        return total_drift, changed
    
    def _generate_drift_interpretation(
        self, 
        old_chars: Dict, 
        new_chars: Dict,
        changed: List[Dict],
        is_positive: bool
    ) -> str:
        """Generate human-readable interpretation of drift."""
        if not changed:
            return "Your trading style has remained consistent."
        
        parts = []
        for c in changed[:3]:  # Top 3 changes
            parts.append(
                f"{c['dimension']} has {c['direction']} by {c['change_pct']:.0f}% "
                f"(from {c['old_value']:.1f} to {c['new_value']:.1f})"
            )
        
        outcome = "which has improved your results" if is_positive else "which may need attention"
        
        return f"Your trading has evolved: {'; '.join(parts)}. This change {outcome}."
    
    def generate_improvement_narrative(
        self, 
        user_id: str, 
        days: int = 21
    ) -> Dict[str, Any]:
        """
        Generate personalized improvement narrative.
        
        "Your discipline has improved 34% in 21 days."
        """
        evolution = self.calculate_behavior_evolution(
            user_id, 
            period_type='weekly',
            lookback_periods=max(3, days // 7)
        )
        
        trends = evolution.get('trends', {})
        narratives = []
        
        for metric, data in trends.items():
            if data.get('direction') == 'improving' and data.get('change_pct', 0) > 10:
                narratives.append({
                    'metric': metric.replace('_', ' ').title(),
                    'change_pct': data['change_pct'],
                    'message': f"Your {metric.replace('_', ' ')} has improved {data['change_pct']:.0f}% in the last {days} days!"
                })
            elif data.get('direction') == 'declining' and data.get('change_pct', 0) < -10:
                narratives.append({
                    'metric': metric.replace('_', ' ').title(),
                    'change_pct': data['change_pct'],
                    'message': f"Your {metric.replace('_', ' ')} has declined {abs(data['change_pct']):.0f}% recently. Consider reviewing your approach."
                })
        
        # Sort by absolute change
        narratives.sort(key=lambda x: abs(x['change_pct']), reverse=True)
        
        # Generate headline
        if narratives:
            top = narratives[0]
            if top['change_pct'] > 0:
                headline = f"Great progress! {top['message']}"
            else:
                headline = f"Attention needed: {top['message']}"
        else:
            headline = "Your trading behavior has been stable recently."
        
        return {
            'headline': headline,
            'narratives': narratives,
            'period_days': days,
            'overall_direction': evolution.get('overall_direction', 'stable'),
            'evolution_summary': evolution
        }
    
    def get_risk_trend(
        self, 
        user_id: str, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get PRS history with trend analysis."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        snapshots = self.db.query(PsychRiskSnapshot).filter(
            PsychRiskSnapshot.user_id == user_id,
            PsychRiskSnapshot.created_at >= cutoff
        ).order_by(PsychRiskSnapshot.created_at).all()
        
        if not snapshots:
            return {
                'has_data': False,
                'history': [],
                'trend': None
            }
        
        history = [{
            'date': s.created_at.isoformat(),
            'score': s.score,
            'state': s.risk_state,
            'factors': s.factors
        } for s in snapshots]
        
        # Calculate trend
        scores = [s.score for s in snapshots]
        if len(scores) >= 2:
            first_half = np.mean(scores[:len(scores)//2])
            second_half = np.mean(scores[len(scores)//2:])
            change = second_half - first_half
            
            if change > 5:
                trend = 'increasing_risk'
            elif change < -5:
                trend = 'decreasing_risk'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'has_data': True,
            'history': history,
            'current_score': scores[-1] if scores else 0,
            'average_score': round(np.mean(scores), 1),
            'trend': trend,
            'days_analyzed': days
        }
    
    def close(self):
        """Close database session if we own it."""
        if self._db:
            self._db.close()
            self._db = None
