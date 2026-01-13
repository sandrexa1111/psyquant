"""
Behavior Event Service
Generates and analyzes behavior event chains for trades.
Chain: Emotion → Decision → Execution → Outcome → Reflection
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from sqlalchemy import func, extract
from sqlalchemy.orm import Session
from database.models import BehaviorEvent, Trade, TradeSnapshot, DetectedBias
from database.database import SessionLocal


class BehaviorEventService:
    """
    Service for generating and analyzing behavior event chains.
    Each trade generates a 5-event chain representing the psychological journey.
    """
    
    EVENT_TYPES = ['emotion', 'decision', 'execution', 'outcome', 'reflection']
    
    def __init__(self, db: Optional[Session] = None):
        self._db = db
    
    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def generate_behavior_chain(self, trade_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Generate a complete behavior event chain for a trade.
        Analyzes trade context to infer emotional and psychological states.
        """
        db = self.db
        try:
            # Get trade and snapshot
            trade = db.query(Trade).filter(Trade.id == trade_id).first()
            if not trade:
                raise ValueError(f"Trade {trade_id} not found")
            
            snapshot = db.query(TradeSnapshot).filter(TradeSnapshot.trade_id == trade_id).first()
            
            chain_id = str(uuid.uuid4())
            events = []
            
            # 1. EMOTION - Pre-trade emotional state
            emotion_event = self._generate_emotion_event(trade, snapshot, chain_id, user_id)
            events.append(emotion_event)
            
            # 2. DECISION - What decision was made and why
            decision_event = self._generate_decision_event(trade, snapshot, chain_id, user_id)
            events.append(decision_event)
            
            # 3. EXECUTION - How the trade was executed
            execution_event = self._generate_execution_event(trade, snapshot, chain_id, user_id)
            events.append(execution_event)
            
            # 4. OUTCOME - Trade result
            outcome_event = self._generate_outcome_event(trade, chain_id, user_id)
            events.append(outcome_event)
            
            # 5. REFLECTION - Lessons learned
            reflection_event = self._generate_reflection_event(trade, events, chain_id, user_id)
            events.append(reflection_event)
            
            # Persist events
            for event_data in events:
                event = BehaviorEvent(
                    id=event_data['id'],
                    user_id=user_id,
                    trade_id=trade_id,
                    chain_id=chain_id,
                    event_type=event_data['event_type'],
                    sequence_order=event_data['sequence_order'],
                    content=event_data['content']
                )
                db.add(event)
            
            db.commit()
            return events
            
        except Exception as e:
            db.rollback()
            raise e
    
    def _generate_emotion_event(self, trade: Trade, snapshot: Optional[TradeSnapshot], 
                                 chain_id: str, user_id: str) -> Dict[str, Any]:
        """Analyze pre-trade emotional state from market context."""
        
        # Analyze indicators for emotional state
        indicators = snapshot.technical_indicators if snapshot else {}
        rsi = indicators.get('rsi', 50) if isinstance(indicators, dict) else 50
        
        # Determine emotional state based on context
        if rsi > 70:
            state = "FOMO"
            intensity = min(100, int((rsi - 70) * 3 + 60))
            triggers = ["Overbought conditions", "Potential fear of missing out"]
        elif rsi < 30:
            state = "Fear"
            intensity = min(100, int((30 - rsi) * 3 + 60))
            triggers = ["Oversold conditions", "Panic selling potential"]
        else:
            state = "Neutral"
            intensity = 30
            triggers = ["Normal market conditions"]
        
        return {
            'id': str(uuid.uuid4()),
            'event_type': 'emotion',
            'sequence_order': 1,
            'chain_id': chain_id,
            'content': {
                'state': state,
                'intensity': intensity,
                'triggers': triggers,
                'market_context': {
                    'rsi': rsi,
                    'regime': snapshot.market_regime if snapshot else 'unknown'
                }
            }
        }
    
    def _generate_decision_event(self, trade: Trade, snapshot: Optional[TradeSnapshot],
                                  chain_id: str, user_id: str) -> Dict[str, Any]:
        """Analyze the decision-making process."""
        
        decision_type = "entry" if trade.side == "buy" else "exit"
        
        # Analyze decision quality based on indicators
        indicators = snapshot.technical_indicators if snapshot else {}
        
        return {
            'id': str(uuid.uuid4()),
            'event_type': 'decision',
            'sequence_order': 2,
            'chain_id': chain_id,
            'content': {
                'decision_type': decision_type,
                'symbol': trade.symbol,
                'side': trade.side,
                'quantity': float(trade.qty),
                'rationale': self._infer_rationale(trade, indicators),
                'confidence_level': self._calculate_decision_confidence(indicators)
            }
        }
    
    def _generate_execution_event(self, trade: Trade, snapshot: Optional[TradeSnapshot],
                                   chain_id: str, user_id: str) -> Dict[str, Any]:
        """Analyze trade execution quality."""
        
        return {
            'id': str(uuid.uuid4()),
            'event_type': 'execution',
            'sequence_order': 3,
            'chain_id': chain_id,
            'content': {
                'entry_price': float(trade.entry_price),
                'exit_price': float(trade.exit_price) if trade.exit_price else None,
                'entry_time': trade.entry_time.isoformat() if trade.entry_time else None,
                'exit_time': trade.exit_time.isoformat() if trade.exit_time else None,
                'holding_time_seconds': trade.holding_time_seconds,
                'execution_quality': self._assess_execution_quality(trade, snapshot)
            }
        }
    
    def _generate_outcome_event(self, trade: Trade, chain_id: str, user_id: str) -> Dict[str, Any]:
        """Record trade outcome."""
        
        pnl = float(trade.pnl) if trade.pnl else 0
        pnl_pct = float(trade.pnl_pct) if trade.pnl_pct else 0
        
        if pnl > 0:
            outcome_type = "profit"
        elif pnl < 0:
            outcome_type = "loss"
        else:
            outcome_type = "breakeven"
        
        return {
            'id': str(uuid.uuid4()),
            'event_type': 'outcome',
            'sequence_order': 4,
            'chain_id': chain_id,
            'content': {
                'outcome_type': outcome_type,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'holding_time_seconds': trade.holding_time_seconds,
                'status': trade.status
            }
        }
    
    def _generate_reflection_event(self, trade: Trade, previous_events: List[Dict],
                                    chain_id: str, user_id: str) -> Dict[str, Any]:
        """Generate reflection based on trade outcome and emotional journey."""
        
        emotion = previous_events[0]['content']
        outcome = previous_events[3]['content']
        
        lessons = []
        if emotion['state'] == 'FOMO' and outcome['outcome_type'] == 'loss':
            lessons.append("FOMO-driven entry led to loss. Consider waiting for pullback.")
        elif emotion['state'] == 'Fear' and outcome['outcome_type'] == 'profit':
            lessons.append("Trading against fear was profitable. Trust analysis over emotion.")
        elif outcome['outcome_type'] == 'profit':
            lessons.append("Trade executed well. Document what worked for future reference.")
        else:
            lessons.append("Review entry criteria and risk management for improvement.")
        
        return {
            'id': str(uuid.uuid4()),
            'event_type': 'reflection',
            'sequence_order': 5,
            'chain_id': chain_id,
            'content': {
                'lessons_learned': lessons,
                'emotion_outcome_correlation': f"{emotion['state']} -> {outcome['outcome_type']}",
                'improvement_areas': self._identify_improvement_areas(previous_events),
                'pattern_detected': self._detect_pattern(emotion, outcome)
            }
        }
    
    def _infer_rationale(self, trade: Trade, indicators: Dict) -> str:
        """Infer trading rationale from context."""
        if trade.side == "buy":
            return "Long position initiated based on market conditions"
        return "Position closed or short initiated"
    
    def _calculate_decision_confidence(self, indicators: Dict) -> int:
        """Calculate decision confidence score (0-100)."""
        if not indicators:
            return 50
        
        rsi = indicators.get('rsi', 50)
        # Higher confidence when RSI is in moderate range
        if 40 <= rsi <= 60:
            return 80
        elif 30 <= rsi <= 70:
            return 60
        return 40
    
    def _assess_execution_quality(self, trade: Trade, snapshot: Optional[TradeSnapshot]) -> str:
        """Assess execution quality."""
        if not snapshot:
            return "unknown"
        
        # In production, compare entry price to VWAP or optimal entry
        return "good"
    
    def _identify_improvement_areas(self, events: List[Dict]) -> List[str]:
        """Identify areas for improvement."""
        areas = []
        emotion = events[0]['content']
        
        if emotion['intensity'] > 70:
            areas.append("Emotional management - high intensity detected")
        
        return areas if areas else ["Continue current approach"]
    
    def _detect_pattern(self, emotion: Dict, outcome: Dict) -> Optional[str]:
        """Detect behavioral pattern."""
        if emotion['state'] == 'FOMO' and outcome['outcome_type'] == 'loss':
            return "FOMO_LOSS_PATTERN"
        elif emotion['state'] == 'Fear' and outcome['outcome_type'] == 'loss':
            return "FEAR_LOSS_PATTERN"
        return None
    
    def get_user_behavior_patterns(self, user_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get behavior patterns for a user."""
        db = self.db
        
        # Get recent behavior events
        events = db.query(BehaviorEvent).filter(
            BehaviorEvent.user_id == user_id
        ).order_by(BehaviorEvent.created_at.desc()).limit(limit * 5).all()
        
        # Group by chain
        chains = {}
        for event in events:
            if event.chain_id not in chains:
                chains[event.chain_id] = []
            chains[event.chain_id].append({
                'id': event.id,
                'event_type': event.event_type,
                'sequence_order': event.sequence_order,
                'content': event.content,
                'trade_id': event.trade_id,
                'created_at': event.created_at.isoformat() if event.created_at else None
            })
        
        # Analyze patterns
        pattern_counts = {}
        for chain_id, chain_events in chains.items():
            reflection = next((e for e in chain_events if e['event_type'] == 'reflection'), None)
            if reflection and reflection['content'].get('pattern_detected'):
                pattern = reflection['content']['pattern_detected']
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        return {
            'chains': list(chains.values())[:limit],
            'patterns': pattern_counts,
            'total_chains': len(chains)
        }

    def get_bias_heatmap(self, user_id: str) -> Dict[str, Any]:
        """
        Aggregate bias frequency by hour of day and volatility (proxy).
        """
        db = self.db
        
        # Aggregate by hour
        biases_by_hour = db.query(
            extract('hour', DetectedBias.detected_at).label('hour'),
            func.count(DetectedBias.id).label('count')
        ).filter(
            DetectedBias.user_id == user_id
        ).group_by('hour').all()
        
        # Aggregate by bias type
        biases_by_type = db.query(
            DetectedBias.bias_type,
            func.count(DetectedBias.id)
        ).filter(
            DetectedBias.user_id == user_id
        ).group_by(DetectedBias.bias_type).all()
        
        # Convert to heatmap struct
        hours_map = {h: 0 for h in range(24)}
        for h, count in biases_by_hour:
            hours_map[int(h)] = count
            
        return {
             "time_heatmap": [{"hour": h, "count": c} for h, c in hours_map.items()],
             "type_distribution": [{"type": t, "count": c} for t, c in biases_by_type]
        }
    
    def run_behavioral_backtest(self, user_id: str) -> Dict[str, Any]:
        """
        Simulate performance with and without emotional trades (Counterfactual Analysis).
        """
        db = self.db
        
        # Get all closed trades sorted by time
        trades = db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.status == 'closed'
        ).order_by(Trade.exit_time).all()
        
        if not trades:
            return {"error": "No trades found"}
            
        # Get all biases
        biases = db.query(DetectedBias).filter(
            DetectedBias.user_id == user_id
        ).all()
        biased_trade_ids = {b.trade_id for b in biases if b.severity and float(b.severity) > 50}
        
        # Calculate actual curve
        current_equity = 100000 # Start baseline
        equity_curve_actual = []
        
        filtered_equity = 100000
        equity_curve_filtered = []
        
        avoided_losses = 0
        missed_gains = 0
        
        for trade in trades:
            pnl = float(trade.pnl) if trade.pnl else 0
            
            # Actual
            current_equity += pnl
            equity_curve_actual.append({
                "time": trade.exit_time.isoformat(),
                "equity": current_equity
            })
            
            # Filtered (if NOT biased)
            if trade.id not in biased_trade_ids:
                filtered_equity += pnl
            else:
                # Track what we skipped
                if pnl < 0:
                    avoided_losses += abs(pnl)
                else:
                    missed_gains += pnl
                    
            equity_curve_filtered.append({
                "time": trade.exit_time.isoformat(),
                "equity": filtered_equity
            })
            
        return {
            "performance_comparison": {
                "actual_final_equity": current_equity,
                "filtered_final_equity": filtered_equity,
                "difference": filtered_equity - current_equity,
                "avoided_losses": avoided_losses,
                "missed_gains": missed_gains
            },
            "equity_curves": {
                "actual": equity_curve_actual,
                "filtered": equity_curve_filtered
            },
            "emotional_trades_count": len(biased_trade_ids),
            "improvement_potential_pct": ((filtered_equity - current_equity) / current_equity * 100) if current_equity > 0 else 0
        }

    def close(self):
        if self._db:
            self._db.close()
            self._db = None
