"""
AI Consistency Service
Provides confidence scoring and normalization for AI insights.
Shows users: "AI confidence: 92% (based on 187 similar trades)"
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import json
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from database.models import (
    Trade, AIInsightVersion, AIConfidenceMetric, AITradeJudgement,
    PsychRiskSnapshot, StrategyFingerprint
)
from database.database import SessionLocal


class AIConsistencyService:
    """
    Provides AI memory normalization and confidence scoring.
    Builds trust by showing users exactly why AI is confident in its analysis.
    """
    
    # Weight factors for confidence calculation
    SAMPLE_SIZE_WEIGHT = 0.30
    CONSISTENCY_WEIGHT = 0.25
    RECENCY_WEIGHT = 0.20
    BASE_MODEL_WEIGHT = 0.25
    
    def __init__(self, db: Optional[Session] = None):
        self._db = db
    
    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def calculate_confidence(
        self, 
        user_id: str,
        insight_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate confidence score for an AI insight.
        
        Args:
            user_id: User for context
            insight_type: 'judgement', 'risk_score', 'strategy_dna', 'pattern'
            context: Context data for the insight
            
        Returns:
            Dict with confidence score, reasoning, and similar trade count
        """
        # Get user's trade history for context
        trades = self.db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.status == 'closed'
        ).order_by(desc(Trade.entry_time)).limit(500).all()
        
        # Calculate base confidence from model quality
        base_confidence = self._calculate_base_confidence(insight_type, context)
        
        # Calculate sample size boost
        similar_count = self._get_similar_trade_count(trades, context)
        sample_size_boost = self._calculate_sample_boost(similar_count)
        
        # Calculate consistency bonus
        consistency_bonus = self._calculate_consistency_bonus(user_id, insight_type)
        
        # Calculate recency factor
        recency_factor = self._calculate_recency_factor(trades)
        
        # Compute final confidence
        final_confidence = int(
            base_confidence * self.BASE_MODEL_WEIGHT +
            sample_size_boost * self.SAMPLE_SIZE_WEIGHT +
            consistency_bonus * self.CONSISTENCY_WEIGHT +
            recency_factor * self.RECENCY_WEIGHT
        )
        final_confidence = min(100, max(0, final_confidence))
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            final_confidence, similar_count, base_confidence,
            sample_size_boost, consistency_bonus, recency_factor
        )
        
        # Create version hash
        version_hash = self._create_version_hash(context)
        
        return {
            'confidence_score': final_confidence,
            'similar_trade_count': similar_count,
            'reasoning': reasoning,
            'breakdown': {
                'base_confidence': round(base_confidence, 1),
                'sample_size_boost': round(sample_size_boost, 1),
                'consistency_bonus': round(consistency_bonus, 1),
                'recency_factor': round(recency_factor, 1)
            },
            'version_hash': version_hash
        }
    
    def _calculate_base_confidence(
        self, 
        insight_type: str, 
        context: Dict[str, Any]
    ) -> float:
        """Calculate base confidence from insight type and context quality."""
        # Base confidence by insight type
        base_scores = {
            'judgement': 70,  # LLM judgements have inherent uncertainty
            'risk_score': 80,  # Mathematical calculations are more reliable
            'strategy_dna': 75,  # Clustering depends on data quality
            'pattern': 65  # Pattern detection has more variability
        }
        
        base = base_scores.get(insight_type, 60)
        
        # Adjust based on context quality
        if context.get('has_snapshot'):
            base += 10
        if context.get('has_indicators'):
            base += 5
        if context.get('trade_count', 0) > 20:
            base += 5
        
        return min(100, base)
    
    def _get_similar_trade_count(
        self, 
        trades: List[Trade], 
        context: Dict[str, Any]
    ) -> int:
        """
        Count trades similar to the current context.
        Used for "based on X similar trades" messaging.
        """
        if not trades:
            return 0
        
        target_symbol = context.get('symbol')
        target_side = context.get('side')
        target_pnl_direction = context.get('pnl_direction')  # 'positive', 'negative'
        
        similar_count = 0
        for trade in trades:
            similarity_score = 0
            
            # Same symbol
            if target_symbol and trade.symbol == target_symbol:
                similarity_score += 1
            
            # Same side
            if target_side and trade.side == target_side:
                similarity_score += 1
            
            # Same P&L direction
            if target_pnl_direction and trade.pnl:
                trade_direction = 'positive' if float(trade.pnl) > 0 else 'negative'
                if trade_direction == target_pnl_direction:
                    similarity_score += 1
            
            # Consider it similar if 2+ criteria match
            if similarity_score >= 2:
                similar_count += 1
        
        # If no specific criteria, count all trades
        if not (target_symbol or target_side or target_pnl_direction):
            similar_count = len(trades)
        
        return similar_count
    
    def _calculate_sample_boost(self, similar_count: int) -> float:
        """
        Calculate confidence boost from sample size.
        More similar trades = higher confidence.
        """
        if similar_count == 0:
            return 20
        elif similar_count < 10:
            return 40
        elif similar_count < 25:
            return 60
        elif similar_count < 50:
            return 75
        elif similar_count < 100:
            return 85
        else:
            return 95
    
    def _calculate_consistency_bonus(
        self, 
        user_id: str, 
        insight_type: str
    ) -> float:
        """
        Calculate bonus for consistent AI outputs over time.
        If AI consistently gives similar insights, confidence is higher.
        """
        # Get recent insight versions
        recent_versions = self.db.query(AIInsightVersion).filter(
            AIInsightVersion.user_id == user_id,
            AIInsightVersion.insight_type == insight_type,
            AIInsightVersion.created_at >= datetime.utcnow() - timedelta(days=30)
        ).order_by(desc(AIInsightVersion.created_at)).limit(10).all()
        
        if len(recent_versions) < 3:
            return 50  # Not enough history
        
        # Check consistency of confidence scores
        scores = [v.confidence_score for v in recent_versions]
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        
        # Low variance = high consistency
        if variance < 25:
            return 90
        elif variance < 100:
            return 70
        elif variance < 225:
            return 50
        else:
            return 30
    
    def _calculate_recency_factor(self, trades: List[Trade]) -> float:
        """
        Calculate factor based on data recency.
        More recent trades = higher confidence in current analysis.
        """
        if not trades:
            return 30
        
        # Check most recent trade
        most_recent = trades[0] if trades else None
        if not most_recent:
            return 30
        
        days_since = (datetime.utcnow() - most_recent.entry_time).days
        
        if days_since <= 1:
            return 95
        elif days_since <= 7:
            return 85
        elif days_since <= 14:
            return 70
        elif days_since <= 30:
            return 55
        else:
            return 40
    
    def _generate_reasoning(
        self,
        final_confidence: int,
        similar_count: int,
        base_confidence: float,
        sample_boost: float,
        consistency: float,
        recency: float
    ) -> str:
        """Generate human-readable confidence reasoning."""
        parts = []
        
        # Main statement
        if final_confidence >= 85:
            parts.append(f"High confidence ({final_confidence}%)")
        elif final_confidence >= 70:
            parts.append(f"Good confidence ({final_confidence}%)")
        elif final_confidence >= 50:
            parts.append(f"Moderate confidence ({final_confidence}%)")
        else:
            parts.append(f"Limited confidence ({final_confidence}%)")
        
        # Sample size reasoning
        if similar_count > 50:
            parts.append(f"based on {similar_count} similar trades")
        elif similar_count > 10:
            parts.append(f"based on {similar_count} comparable trades")
        elif similar_count > 0:
            parts.append(f"with limited comparison data ({similar_count} trades)")
        else:
            parts.append("with no similar trade history")
        
        return ", ".join(parts) + "."
    
    def _create_version_hash(self, context: Dict[str, Any]) -> str:
        """Create hash of context for version tracking."""
        # Sort keys for consistent hashing
        context_str = json.dumps(context, sort_keys=True, default=str)
        return hashlib.md5(context_str.encode()).hexdigest()[:16]
    
    def store_insight_version(
        self,
        user_id: str,
        insight_type: str,
        insight_id: str,
        confidence_result: Dict[str, Any],
        explanation_summary: str = None
    ) -> str:
        """Store an insight version with confidence metrics."""
        insight_version = AIInsightVersion(
            user_id=user_id,
            insight_type=insight_type,
            insight_id=insight_id,
            confidence_score=confidence_result['confidence_score'],
            similar_trade_count=confidence_result['similar_trade_count'],
            version_hash=confidence_result.get('version_hash'),
            explanation_summary=explanation_summary,
            reasoning=confidence_result['breakdown']
        )
        self.db.add(insight_version)
        
        # Store detailed metrics
        breakdown = confidence_result['breakdown']
        metric = AIConfidenceMetric(
            insight_version_id=insight_version.id,
            base_confidence=Decimal(str(breakdown['base_confidence'])),
            sample_size_boost=Decimal(str(breakdown['sample_size_boost'])),
            consistency_bonus=Decimal(str(breakdown['consistency_bonus'])),
            recency_factor=Decimal(str(breakdown['recency_factor'])),
            final_confidence=confidence_result['confidence_score'],
            reasoning=confidence_result['reasoning']
        )
        self.db.add(metric)
        
        try:
            self.db.commit()
            return insight_version.id
        except Exception:
            self.db.rollback()
            raise
    
    def get_insight_history(
        self,
        user_id: str,
        insight_type: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get history of AI insights with confidence scores."""
        query = self.db.query(AIInsightVersion).filter(
            AIInsightVersion.user_id == user_id
        )
        
        if insight_type:
            query = query.filter(AIInsightVersion.insight_type == insight_type)
        
        versions = query.order_by(
            desc(AIInsightVersion.created_at)
        ).limit(limit).all()
        
        return [{
            'id': v.id,
            'insight_type': v.insight_type,
            'insight_id': v.insight_id,
            'confidence_score': v.confidence_score,
            'similar_trade_count': v.similar_trade_count,
            'explanation_summary': v.explanation_summary,
            'created_at': v.created_at.isoformat() if v.created_at else None
        } for v in versions]
    
    def normalize_ai_output(self, raw_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize AI output to consistent format.
        Ensures all AI responses have standard structure.
        """
        normalized = {
            'result': raw_response.get('result', raw_response),
            'metadata': {
                'normalized_at': datetime.utcnow().isoformat(),
                'original_keys': list(raw_response.keys())
            }
        }
        
        # Extract confidence if present
        if 'confidence' in raw_response:
            normalized['confidence'] = raw_response['confidence']
        
        # Extract explanation if present
        for key in ['explanation', 'reasoning', 'summary']:
            if key in raw_response:
                normalized['explanation'] = raw_response[key]
                break
        
        return normalized
    
    def close(self):
        """Close database session if we own it."""
        if self._db:
            self._db.close()
            self._db = None
