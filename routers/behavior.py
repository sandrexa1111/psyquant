"""
Behavior Intelligence API Router
Provides endpoints for behavior patterns, risk scoring, strategy DNA, and AI trade judging.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from .auth import get_current_user

from services.behavior_service import BehaviorEventService
from services.psych_risk_service import PsychRiskScoreService
from services.strategy_dna_service import StrategyDNAService
from services.ai_judge_service import AIJudgeService
from services.longitudinal_service import LongitudinalService
from services.ai_consistency_service import AIConsistencyService
from services.skill_score_service import SkillScoreService

router = APIRouter(prefix="/ai", tags=["behavior-intelligence"])


# ============================================================================
# Request/Response Models
# ============================================================================

class JudgeTradeRequest(BaseModel):
    trade_id: str


class JudgeTradeResponse(BaseModel):
    id: str
    trade_id: str
    logical_score: int
    emotional_score: int
    discipline_score: int
    explanation: str
    loss_attribution: Optional[str] = None
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommendations: List[str] = []
    model_used: Optional[str] = None
    created_at: Optional[str] = None


class RiskScoreResponse(BaseModel):
    score: int
    risk_state: str
    factors: Dict[str, float]
    trades_analyzed: int
    lookback_days: int
    history: List[Dict[str, Any]] = []


class BehaviorPatternsResponse(BaseModel):
    chains: List[Any]
    patterns: Dict[str, int]
    total_chains: int


class StrategyDNAResponse(BaseModel):
    fingerprints: List[Dict[str, Any]]
    total_strategies: int


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/judge-trade", response_model=JudgeTradeResponse)
async def judge_trade(request: JudgeTradeRequest, current_user: User = Depends(get_current_user)):
    """
    Generate AI analysis for a specific trade.
    """
    service = AIJudgeService()
    try:
        result = service.judge_trade(request.trade_id, current_user.id)
        return JudgeTradeResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.get("/judge-trade/{trade_id}", response_model=JudgeTradeResponse)
async def get_trade_judgement(trade_id: str, current_user: User = Depends(get_current_user)):
    """
    Get existing AI judgement for a trade.
    """
    service = AIJudgeService()
    try:
        result = service.get_judgement(trade_id)
        if not result:
            raise HTTPException(status_code=404, detail="No judgement found for this trade")
        return JudgeTradeResponse(**result)
    finally:
        service.close()


@router.get("/risk-score", response_model=RiskScoreResponse)
async def get_risk_score(lookback_days: int = 30, current_user: User = Depends(get_current_user)):
    """
    Calculate current Psychological Risk Score (PRS) for the user.
    """
    service = PsychRiskScoreService()
    try:
        result = service.calculate_prs(current_user.id, lookback_days)
        history = service.get_prs_history(current_user.id, limit=30)
        result['history'] = history
        return RiskScoreResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.get("/behavior-patterns", response_model=BehaviorPatternsResponse)
async def get_behavior_patterns(limit: int = 50, current_user: User = Depends(get_current_user)):
    """
    Get behavior event chains and detected patterns for the user.
    """
    service = BehaviorEventService()
    try:
        result = service.get_user_behavior_patterns(current_user.id, limit)
        return BehaviorPatternsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.post("/behavior-patterns/{trade_id}")
async def generate_behavior_chain(trade_id: str, current_user: User = Depends(get_current_user)):
    """
    Generate behavior event chain for a specific trade.
    """
    service = BehaviorEventService()
    try:
        events = service.generate_behavior_chain(trade_id, current_user.id)
        return {
            "trade_id": trade_id,
            "chain_length": len(events),
            "events": events
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.get("/strategy-dna", response_model=StrategyDNAResponse)
async def get_strategy_dna(current_user: User = Depends(get_current_user)):
    """
    Get AI-discovered strategy fingerprints for the user.
    """
    service = StrategyDNAService()
    try:
        fingerprints = service.get_fingerprints(current_user.id)
        return StrategyDNAResponse(
            fingerprints=fingerprints,
            total_strategies=len(fingerprints)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.post("/strategy-dna/rebuild")
async def rebuild_strategy_dna(min_trades: int = 5, current_user: User = Depends(get_current_user)):
    """
    Rebuild strategy fingerprints from trade history.
    """
    service = StrategyDNAService()
    try:
        fingerprints = service.build_fingerprints(current_user.id, min_trades)
        return {
            "status": "success",
            "fingerprints_created": len(fingerprints),
            "fingerprints": fingerprints
        }
    except Exception as e:
        print(f"DNA Rebuild Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.get("/summary")
async def get_intelligence_summary(current_user: User = Depends(get_current_user)):
    """
    Get a summary of all behavior intelligence metrics for the user.
    """
    prs_service = PsychRiskScoreService()
    dna_service = StrategyDNAService()
    behavior_service = BehaviorEventService()
    
    try:
        # Get PRS
        prs = prs_service.calculate_prs(current_user.id, 30)
        
        # Get Strategy DNA
        fingerprints = dna_service.get_fingerprints(current_user.id)
        
        # Get recent patterns
        patterns = behavior_service.get_user_behavior_patterns(current_user.id, 20)
        
        return {
            "psychological_risk": {
                "score": prs['score'],
                "state": prs['risk_state'],
                "factors": prs['factors']
            },
            "strategy_dna": {
                "total_strategies": len(fingerprints),
                "top_strategy": fingerprints[0] if fingerprints else None
            },
            "behavior_patterns": {
                "total_chains": patterns['total_chains'],
                "detected_patterns": patterns['patterns']
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        prs_service.close()
        dna_service.close()
        behavior_service.close()


@router.get("/evolution")
async def get_behavior_evolution(
    period_type: str = "weekly",
    lookback_periods: int = 12,
    current_user: User = Depends(get_current_user)
):
    """
    Get behavior evolution metrics over time.
    """
    if period_type not in ['daily', 'weekly', 'monthly']:
        raise HTTPException(status_code=400, detail="period_type must be daily, weekly, or monthly")
    
    service = LongitudinalService()
    try:
        result = service.calculate_behavior_evolution(
            current_user.id, 
            period_type=period_type,
            lookback_periods=lookback_periods
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.get("/strategy-drift")
async def get_strategy_drift(comparison_days: int = 30, current_user: User = Depends(get_current_user)):
    """
    Detect changes in trading strategy over time.
    """
    if comparison_days < 7 or comparison_days > 180:
        raise HTTPException(status_code=400, detail="comparison_days must be between 7 and 180")
    
    service = LongitudinalService()
    try:
        result = service.detect_strategy_drift(current_user.id, comparison_days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.get("/improvement")
async def get_improvement_narrative(days: int = 21, current_user: User = Depends(get_current_user)):
    """
    Generate personalized improvement narrative.
    """
    if days < 7 or days > 90:
        raise HTTPException(status_code=400, detail="days must be between 7 and 90")
    
    service = LongitudinalService()
    try:
        result = service.generate_improvement_narrative(current_user.id, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.get("/risk-trend")
async def get_risk_trend(days: int = 30, current_user: User = Depends(get_current_user)):
    """
    Get PRS history with trend analysis.
    """
    if days < 7 or days > 180:
        raise HTTPException(status_code=400, detail="days must be between 7 and 180")
    
    service = LongitudinalService()
    try:
        result = service.get_risk_trend(current_user.id, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.get("/confidence")
async def calculate_confidence(
    insight_type: str = "judgement",
    symbol: str = None,
    side: str = None,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate AI confidence for a given context.
    """
    if insight_type not in ['judgement', 'risk_score', 'strategy_dna', 'pattern']:
        raise HTTPException(status_code=400, detail="insight_type must be judgement, risk_score, strategy_dna, or pattern")
    
    service = AIConsistencyService()
    try:
        context = {
            'symbol': symbol,
            'side': side,
            'has_snapshot': True,
            'has_indicators': True
        }
        result = service.calculate_confidence(current_user.id, insight_type, context)
        return {
            'confidence_score': result['confidence_score'],
            'similar_trade_count': result['similar_trade_count'],
            'reasoning': result['reasoning'],
            'breakdown': result['breakdown'],
            'display_text': f"AI confidence: {result['confidence_score']}% (based on {result['similar_trade_count']} similar trades)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.get("/confidence/history")
async def get_confidence_history(
    insight_type: str = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """
    Get history of AI insights with confidence scores.
    """
    service = AIConsistencyService()
    try:
        history = service.get_insight_history(current_user.id, insight_type, limit)
        return {
            'history': history,
            'total': len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


@router.get("/skill-score")
async def get_skill_score(current_user: User = Depends(get_current_user)):
    """
    Get current Trader Skill DNA score.
    """
    service = SkillScoreService()
    try:
        score = service.calculate_score(current_user.id)
        history = service.get_history(current_user.id, limit=30)
        return {
            "current": score,
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()

@router.get("/bias-heatmap")
async def get_bias_heatmap(current_user: User = Depends(get_current_user)):
    """
    Get Cognitive Bias Heatmap data.
    """
    service = BehaviorEventService()
    try:
        data = service.get_bias_heatmap(current_user.id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()

@router.get("/backtest")
async def run_behavioral_backtest(current_user: User = Depends(get_current_user)):
    """
    Run 'What-If' analysis: Performance without emotional trades.
    """
    service = BehaviorEventService()
    try:
        results = service.run_behavioral_backtest(current_user.id)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        service.close()


