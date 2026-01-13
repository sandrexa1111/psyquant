"""
Behavioral Alerts Engine Service
Detects personal behavioral patterns and provides real-time warnings.
Examples:
- "You usually overtrade after 2 losses"
- "Your worst trades happen when RSI is between 40-50"
- "You break rules mostly after profitable streaks"
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import numpy as np

from database.models import (
    Trade, BehaviorPattern, PatternAlert, TradeSnapshot, DetectedBias
)
from database.database import SessionLocal


class BehaviorAlertsService:
    """
    Pattern detection engine for personalized behavioral defense.
    Analyzes trading history to find repeating negative patterns.
    """
    
    # Minimum occurrences to establish a pattern
    MIN_PATTERN_OCCURRENCES = 3
    
    # Pattern type definitions
    PATTERN_TYPES = {
        'overtrade_after_loss': {
            'name': 'Overtrading After Losses',
            'severity': 'warning',
            'description_template': "You tend to execute {count}+ trades within {hours} hours after {losses} consecutive losses."
        },
        'break_rules_after_win': {
            'name': 'Rule Breaking After Wins',
            'severity': 'warning', 
            'description_template': "You tend to break your position sizing rules after {wins} consecutive profitable trades."
        },
        'rsi_blind_spot': {
            'name': 'RSI Blind Spot',
            'severity': 'info',
            'description_template': "Your worst-performing trades occur when RSI is between {rsi_low} and {rsi_high}."
        },
        'time_of_day_weakness': {
            'name': 'Time of Day Weakness',
            'severity': 'info',
            'description_template': "You tend to make poor decisions during {time_range}."
        },
        'revenge_trading': {
            'name': 'Revenge Trading Pattern',
            'severity': 'critical',
            'description_template': "After losses, you increase position sizes by {pct}% on average, leading to larger losses."
        }
    }
    
    def __init__(self, db: Optional[Session] = None):
        self._db = db
    
    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def detect_all_patterns(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Run all pattern detection algorithms for a user.
        Returns list of newly detected or updated patterns.
        """
        # Get trade history
        trades = self.db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.status == 'closed'
        ).order_by(Trade.entry_time).all()
        
        if len(trades) < 10:
            return []  # Need minimum data
        
        detected = []
        
        # Run each detection algorithm
        pattern = self._detect_overtrade_after_loss(trades, user_id)
        if pattern:
            detected.append(pattern)
        
        pattern = self._detect_revenge_trading(trades, user_id)
        if pattern:
            detected.append(pattern)
        
        pattern = self._detect_time_weakness(trades, user_id)
        if pattern:
            detected.append(pattern)
        
        pattern = self._detect_rsi_blind_spot(trades, user_id)
        if pattern:
            detected.append(pattern)
        
        return detected
    
    def _detect_overtrade_after_loss(
        self, 
        trades: List[Trade], 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Detect pattern: User overtrades after consecutive losses.
        """
        # Find sequences of losses followed by rapid trading
        loss_streak_trades = []
        current_streak = 0
        
        for i, trade in enumerate(trades):
            if trade.pnl and float(trade.pnl) < 0:
                current_streak += 1
            else:
                # Check if after 2+ losses, user made many rapid trades
                if current_streak >= 2 and i + 1 < len(trades):
                    # Count trades in next 2 hours
                    window_end = trade.entry_time + timedelta(hours=2)
                    rapid_trades = sum(
                        1 for t in trades[i+1:] 
                        if t.entry_time <= window_end
                    )
                    if rapid_trades >= 3:
                        loss_streak_trades.append({
                            'losses': current_streak,
                            'rapid_trades': rapid_trades,
                            'trade_id': trade.id
                        })
                current_streak = 0
        
        if len(loss_streak_trades) >= self.MIN_PATTERN_OCCURRENCES:
            avg_losses = np.mean([x['losses'] for x in loss_streak_trades])
            avg_rapid = np.mean([x['rapid_trades'] for x in loss_streak_trades])
            
            return self._create_or_update_pattern(
                user_id=user_id,
                pattern_type='overtrade_after_loss',
                confidence=min(95, 60 + len(loss_streak_trades) * 5),
                trigger_conditions={
                    'losses_before': int(avg_losses),
                    'trades_within_hours': 2,
                    'typical_trades': int(avg_rapid)
                },
                example_trades=[x['trade_id'] for x in loss_streak_trades[:5]],
                occurrences=len(loss_streak_trades)
            )
        
        return None
    
    def _detect_revenge_trading(
        self, 
        trades: List[Trade], 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Detect pattern: User increases position size after losses (revenge trading).
        """
        revenge_instances = []
        
        for i in range(1, len(trades)):
            prev = trades[i-1]
            curr = trades[i]
            
            # If previous was a loss and current position is significantly larger
            if prev.pnl and float(prev.pnl) < 0:
                if float(curr.qty) > float(prev.qty) * 1.5:  # 50% larger
                    # Check if this larger trade also lost
                    if curr.pnl and float(curr.pnl) < 0:
                        size_increase = (float(curr.qty) / float(prev.qty) - 1) * 100
                        revenge_instances.append({
                            'trade_id': curr.id,
                            'size_increase_pct': size_increase,
                            'loss': float(curr.pnl)
                        })
        
        if len(revenge_instances) >= self.MIN_PATTERN_OCCURRENCES:
            avg_increase = np.mean([x['size_increase_pct'] for x in revenge_instances])
            
            return self._create_or_update_pattern(
                user_id=user_id,
                pattern_type='revenge_trading',
                confidence=min(95, 65 + len(revenge_instances) * 5),
                trigger_conditions={
                    'after_loss': True,
                    'size_increase_pct': round(avg_increase, 0),
                    'results_in_loss': True
                },
                example_trades=[x['trade_id'] for x in revenge_instances[:5]],
                occurrences=len(revenge_instances)
            )
        
        return None
    
    def _detect_time_weakness(
        self, 
        trades: List[Trade], 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Detect pattern: User performs poorly during specific times of day.
        """
        # Group trades by hour
        hour_performance = {}
        for trade in trades:
            if trade.pnl and trade.entry_time:
                hour = trade.entry_time.hour
                if hour not in hour_performance:
                    hour_performance[hour] = []
                hour_performance[hour].append(float(trade.pnl))
        
        # Find worst-performing hours
        worst_hours = []
        for hour, pnls in hour_performance.items():
            if len(pnls) >= 3:
                avg_pnl = np.mean(pnls)
                win_rate = sum(1 for p in pnls if p > 0) / len(pnls)
                if avg_pnl < 0 and win_rate < 0.4:
                    worst_hours.append({
                        'hour': hour,
                        'avg_pnl': avg_pnl,
                        'win_rate': win_rate,
                        'trades': len(pnls)
                    })
        
        if worst_hours:
            # Find contiguous ranges
            worst_hours.sort(key=lambda x: x['avg_pnl'])
            worst = worst_hours[0]
            
            time_range = f"{worst['hour']:02d}:00 - {(worst['hour']+1)%24:02d}:00"
            
            return self._create_or_update_pattern(
                user_id=user_id,
                pattern_type='time_of_day_weakness',
                confidence=min(90, 50 + worst['trades'] * 3),
                trigger_conditions={
                    'hour_start': worst['hour'],
                    'hour_end': (worst['hour'] + 1) % 24,
                    'avg_win_rate': round(worst['win_rate'] * 100, 1)
                },
                example_trades=[],
                occurrences=worst['trades'],
                custom_description=f"You tend to make poor decisions during {time_range} (win rate: {worst['win_rate']*100:.0f}%)."
            )
        
        return None
    
    def _detect_rsi_blind_spot(
        self, 
        trades: List[Trade], 
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Detect pattern: Poor performance when RSI is in a specific range.
        """
        # Get trades with snapshots containing RSI
        rsi_performance = []
        
        for trade in trades:
            if trade.snapshot and trade.snapshot.technical_indicators:
                indicators = trade.snapshot.technical_indicators
                if isinstance(indicators, dict) and 'RSI' in indicators:
                    rsi = indicators['RSI']
                    if rsi and trade.pnl:
                        rsi_performance.append({
                            'rsi': rsi,
                            'pnl': float(trade.pnl),
                            'trade_id': trade.id
                        })
        
        if len(rsi_performance) < 10:
            return None
        
        # Bucket RSI into ranges and find worst
        buckets = {
            '0-20': [], '20-40': [], '40-60': [], '60-80': [], '80-100': []
        }
        
        for item in rsi_performance:
            rsi = item['rsi']
            if rsi < 20:
                buckets['0-20'].append(item)
            elif rsi < 40:
                buckets['20-40'].append(item)
            elif rsi < 60:
                buckets['40-60'].append(item)
            elif rsi < 80:
                buckets['60-80'].append(item)
            else:
                buckets['80-100'].append(item)
        
        # Find worst bucket
        worst_bucket = None
        worst_avg = float('inf')
        
        for bucket, items in buckets.items():
            if len(items) >= 5:
                avg = np.mean([i['pnl'] for i in items])
                if avg < worst_avg:
                    worst_avg = avg
                    worst_bucket = bucket
        
        if worst_bucket and worst_avg < 0:
            rsi_low, rsi_high = map(int, worst_bucket.split('-'))
            trades_in_bucket = buckets[worst_bucket]
            
            return self._create_or_update_pattern(
                user_id=user_id,
                pattern_type='rsi_blind_spot',
                confidence=min(85, 50 + len(trades_in_bucket) * 2),
                trigger_conditions={
                    'rsi_low': rsi_low,
                    'rsi_high': rsi_high,
                    'avg_loss': round(worst_avg, 2)
                },
                example_trades=[t['trade_id'] for t in trades_in_bucket[:5]],
                occurrences=len(trades_in_bucket)
            )
        
        return None
    
    def _create_or_update_pattern(
        self,
        user_id: str,
        pattern_type: str,
        confidence: float,
        trigger_conditions: Dict,
        example_trades: List[str],
        occurrences: int,
        custom_description: str = None
    ) -> Dict[str, Any]:
        """Create or update a behavior pattern in the database."""
        # Check if pattern already exists
        existing = self.db.query(BehaviorPattern).filter(
            BehaviorPattern.user_id == user_id,
            BehaviorPattern.pattern_type == pattern_type
        ).first()
        
        pattern_def = self.PATTERN_TYPES.get(pattern_type, {})
        
        if custom_description:
            description = custom_description
        else:
            description = pattern_def.get('description_template', '').format(**trigger_conditions)
        
        if existing:
            # Update existing pattern
            existing.confidence = Decimal(str(confidence))
            existing.trigger_conditions = trigger_conditions
            existing.occurrence_count = occurrences
            existing.example_trade_ids = example_trades
            existing.pattern_description = description
            existing.updated_at = datetime.utcnow()
            
            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
            
            return self._pattern_to_dict(existing)
        else:
            # Create new pattern
            pattern = BehaviorPattern(
                user_id=user_id,
                pattern_type=pattern_type,
                pattern_name=pattern_def.get('name', pattern_type),
                pattern_description=description,
                trigger_conditions=trigger_conditions,
                confidence=Decimal(str(confidence)),
                occurrence_count=occurrences,
                severity=pattern_def.get('severity', 'warning'),
                example_trade_ids=example_trades
            )
            self.db.add(pattern)
            
            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise
            
            return self._pattern_to_dict(pattern)
    
    def _pattern_to_dict(self, pattern: BehaviorPattern) -> Dict[str, Any]:
        """Convert pattern to dictionary."""
        return {
            'id': pattern.id,
            'pattern_type': pattern.pattern_type,
            'pattern_name': pattern.pattern_name,
            'description': pattern.pattern_description,
            'trigger_conditions': pattern.trigger_conditions,
            'confidence': float(pattern.confidence) if pattern.confidence else 0,
            'occurrence_count': pattern.occurrence_count,
            'severity': pattern.severity,
            'is_active': pattern.is_active,
            'created_at': pattern.created_at.isoformat() if pattern.created_at else None
        }
    
    def get_user_patterns(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all detected patterns for a user."""
        patterns = self.db.query(BehaviorPattern).filter(
            BehaviorPattern.user_id == user_id,
            BehaviorPattern.is_active == True
        ).order_by(desc(BehaviorPattern.confidence)).all()
        
        return [self._pattern_to_dict(p) for p in patterns]
    
    def get_active_alerts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get unacknowledged alerts for a user."""
        alerts = self.db.query(PatternAlert).filter(
            PatternAlert.user_id == user_id,
            PatternAlert.acknowledged == False
        ).order_by(desc(PatternAlert.triggered_at)).all()
        
        return [{
            'id': a.id,
            'pattern_id': a.pattern_id,
            'alert_type': a.alert_type,
            'message': a.alert_message,
            'severity': a.severity,
            'context': a.triggering_context,
            'triggered_at': a.triggered_at.isoformat() if a.triggered_at else None
        } for a in alerts]
    
    def acknowledge_alert(self, alert_id: str, feedback: str = None) -> bool:
        """Mark an alert as acknowledged."""
        alert = self.db.query(PatternAlert).filter(
            PatternAlert.id == alert_id
        ).first()
        
        if alert:
            alert.acknowledged = True
            alert.acknowledged_at = datetime.utcnow()
            if feedback:
                alert.user_feedback = feedback
            
            try:
                self.db.commit()
                return True
            except Exception:
                self.db.rollback()
        
        return False
    
    def check_pre_trade_warning(
        self, 
        user_id: str, 
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Check if current conditions match any known patterns.
        Call this before trade execution to warn user.
        """
        # Get user's patterns
        patterns = self.db.query(BehaviorPattern).filter(
            BehaviorPattern.user_id == user_id,
            BehaviorPattern.is_active == True
        ).all()
        
        if not patterns:
            return None
        
        # Get recent trades
        recent_trades = self.db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.entry_time >= datetime.utcnow() - timedelta(hours=4)
        ).order_by(desc(Trade.entry_time)).limit(10).all()
        
        # Check each pattern
        warnings = []
        
        for pattern in patterns:
            match = self._check_pattern_match(pattern, context, recent_trades)
            if match:
                # Create alert
                alert = PatternAlert(
                    user_id=user_id,
                    pattern_id=pattern.id,
                    alert_type='pre_trade_warning',
                    alert_message=f"Warning: {pattern.pattern_name}. {pattern.pattern_description}",
                    severity=pattern.severity,
                    triggering_context=context,
                    expires_at=datetime.utcnow() + timedelta(hours=1)
                )
                self.db.add(alert)
                
                warnings.append({
                    'pattern_name': pattern.pattern_name,
                    'message': pattern.pattern_description,
                    'severity': pattern.severity,
                    'confidence': float(pattern.confidence)
                })
        
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
        
        if warnings:
            return {
                'has_warning': True,
                'warnings': warnings,
                'highest_severity': max(w['severity'] for w in warnings)
            }
        
        return {'has_warning': False, 'warnings': []}
    
    def _check_pattern_match(
        self, 
        pattern: BehaviorPattern, 
        context: Dict, 
        recent_trades: List[Trade]
    ) -> bool:
        """Check if current context matches a pattern's trigger conditions."""
        conditions = pattern.trigger_conditions or {}
        
        if pattern.pattern_type == 'overtrade_after_loss':
            # Check if recently had consecutive losses
            consecutive_losses = 0
            for trade in recent_trades:
                if trade.pnl and float(trade.pnl) < 0:
                    consecutive_losses += 1
                else:
                    break
            
            required_losses = conditions.get('losses_before', 2)
            return consecutive_losses >= required_losses
        
        elif pattern.pattern_type == 'revenge_trading':
            # Check if last trade was a loss
            if recent_trades and recent_trades[0].pnl:
                return float(recent_trades[0].pnl) < 0
        
        elif pattern.pattern_type == 'time_of_day_weakness':
            # Check if current time is in danger zone
            current_hour = datetime.utcnow().hour
            hour_start = conditions.get('hour_start', 0)
            hour_end = conditions.get('hour_end', 24)
            return hour_start <= current_hour < hour_end
        
        elif pattern.pattern_type == 'rsi_blind_spot':
            # Check if provided RSI is in danger zone
            rsi = context.get('rsi')
            if rsi:
                rsi_low = conditions.get('rsi_low', 0)
                rsi_high = conditions.get('rsi_high', 100)
                return rsi_low <= rsi <= rsi_high
        
        return False
    
    def close(self):
        """Close database session if we own it."""
        if self._db:
            self._db.close()
            self._db = None
