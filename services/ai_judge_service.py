"""
AI Trade Judge Service
LLM-powered trade analysis using Google Gemini.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json
import os
from sqlalchemy.orm import Session
from database.models import Trade, TradeSnapshot, AITradeJudgement, BehaviorEvent
from database.database import SessionLocal

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if env vars are set directly

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None


class AIJudgeService:
    """
    LLM-powered trade analysis service.
    Uses Google Gemini to provide structured trade judgements.
    """
    
    def __init__(self, db: Optional[Session] = None):
        self._db = db
        self._model = None
        self._initialize_gemini()
    
    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def _initialize_gemini(self):
        """Initialize Gemini API client."""
        if not GEMINI_AVAILABLE:
            print("⚠️ Google Generative AI package not installed. Run: pip install google-generativeai")
            return
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            print("⚠️ GOOGLE_API_KEY not configured in .env file")
            return
        
        try:
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel('gemini-2.0-flash')
            print("✅ Gemini AI initialized successfully")
        except Exception as e:
            print(f"⚠️ Failed to initialize Gemini: {e}")
    
    def judge_trade(self, trade_id: str, user_id: str) -> Dict[str, Any]:
        """
        Generate AI judgement for a trade.
        Returns structured analysis with scores and explanation.
        """
        db = self.db
        
        # Check for existing judgement
        existing = db.query(AITradeJudgement).filter(
            AITradeJudgement.trade_id == trade_id
        ).first()
        
        if existing:
            return self._judgement_to_dict(existing)
        
        # Get trade
        trade = db.query(Trade).filter(Trade.id == trade_id).first()
        if not trade:
            raise ValueError(f"Trade {trade_id} not found")
        
        # Get snapshot
        snapshot = db.query(TradeSnapshot).filter(
            TradeSnapshot.trade_id == trade_id
        ).first()
        
        # Get behavior events
        behavior_events = db.query(BehaviorEvent).filter(
            BehaviorEvent.trade_id == trade_id
        ).order_by(BehaviorEvent.sequence_order).all()
        
        # Build prompt
        prompt = self._build_prompt(trade, snapshot, behavior_events)
        
        # Call LLM
        result = self._call_llm(prompt)
        
        # Create judgement record
        judgement = AITradeJudgement(
            trade_id=trade_id,
            user_id=user_id,
            logical_score=result['logical_score'],
            emotional_score=result['emotional_score'],
            discipline_score=result['discipline_score'],
            explanation=result['explanation'],
            loss_attribution=result.get('loss_attribution'),
            strengths=result.get('strengths', []),
            weaknesses=result.get('weaknesses', []),
            recommendations=result.get('recommendations', []),
            model_used=result.get('model_used', 'gemini-2.0-flash'),
            prompt_tokens=result.get('prompt_tokens'),
            completion_tokens=result.get('completion_tokens')
        )
        
        db.add(judgement)
        db.commit()
        
        return self._judgement_to_dict(judgement)
    
    def _build_prompt(self, trade: Trade, snapshot: Optional[TradeSnapshot],
                       behavior_events: list) -> str:
        """Build structured prompt for trade analysis."""
        
        pnl = float(trade.pnl) if trade.pnl else 0
        pnl_pct = float(trade.pnl_pct) if trade.pnl_pct else 0
        
        # Format behavior events
        events_text = ""
        for event in behavior_events:
            events_text += f"- {event.event_type.upper()}: {json.dumps(event.content)}\n"
        
        # Format indicators
        indicators_text = "No technical data available"
        if snapshot and snapshot.technical_indicators:
            indicators_text = json.dumps(snapshot.technical_indicators)
        
        prompt = f"""You are an expert trading psychology analyst and coach. Analyze this trade and provide a structured assessment.

## Trade Details
- Symbol: {trade.symbol}
- Side: {trade.side}
- Quantity: {float(trade.qty)}
- Entry Price: ${float(trade.entry_price):.2f}
- Exit Price: ${float(trade.exit_price) if trade.exit_price else 'Still Open'}
- P/L: ${pnl:.2f} ({pnl_pct:.2f}%)
- Holding Time: {trade.holding_time_seconds or 0} seconds
- Status: {trade.status}

## Market Context
{indicators_text}

## Behavior Chain
{events_text if events_text else "No behavior data captured"}

## Instructions
Analyze this trade and respond ONLY with valid JSON in this exact format:
{{
    "logical_score": <0-100 integer>,
    "emotional_score": <0-100 integer, higher = more emotional/less controlled>,
    "discipline_score": <0-100 integer>,
    "explanation": "<2-3 sentence analysis>",
    "loss_attribution": "<ONLY if P/L is negative: 'market_noise', 'strategy_flaw', or 'psychological_error'>",
    "strengths": ["<list of 1-3 strengths identified>"],
    "weaknesses": ["<list of 1-3 weaknesses identified>"],
    "recommendations": ["<list of 1-3 actionable recommendations>"]
}}

Scoring Guide:
- logical_score: How well-reasoned was the trade decision? (100 = perfect logic)
- emotional_score: How emotionally-driven was this trade? (0 = cool/calculated, 100 = highly emotional)
- discipline_score: Did the trader follow good risk management? (100 = perfect discipline)

Respond ONLY with the JSON object, no other text."""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """Call Gemini API and parse response."""
        
        if not self._model:
            return self._fallback_analysis(prompt)
        
        try:
            response = self._model.generate_content(prompt)
            
            # Extract text from response
            response_text = response.text.strip()
            
            # Clean up response (remove markdown code blocks if present)
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])
            
            # Parse JSON
            result = json.loads(response_text)
            
            # Validate required fields
            required = ['logical_score', 'emotional_score', 'discipline_score', 'explanation']
            for field in required:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure scores are within range
            for score_field in ['logical_score', 'emotional_score', 'discipline_score']:
                result[score_field] = max(0, min(100, int(result[score_field])))
            
            result['model_used'] = 'gemini-2.0-flash'
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse LLM response as JSON: {e}")
            return self._fallback_analysis(prompt)
        except Exception as e:
            print(f"⚠️ LLM call failed: {e}")
            return self._fallback_analysis(prompt)
    
    def _fallback_analysis(self, prompt: str) -> Dict[str, Any]:
        """
        Fallback analysis when LLM is not available.
        Uses rule-based scoring from prompt context.
        """
        # Extract basic info from prompt for heuristic scoring
        is_loss = "P/L: $-" in prompt or "P/L: -" in prompt
        
        return {
            'logical_score': 60,
            'emotional_score': 40,
            'discipline_score': 65,
            'explanation': "AI analysis temporarily unavailable. Please configure GOOGLE_API_KEY to enable full LLM analysis.",
            'loss_attribution': 'market_noise' if is_loss else None,
            'strengths': ["Trade was executed"],
            'weaknesses': ["Unable to perform deep analysis without LLM"],
            'recommendations': ["Configure API key for full analysis"],
            'model_used': 'fallback_heuristic'
        }
    
    def _judgement_to_dict(self, judgement: AITradeJudgement) -> Dict[str, Any]:
        """Convert judgement model to dictionary."""
        return {
            'id': judgement.id,
            'trade_id': judgement.trade_id,
            'user_id': judgement.user_id,
            'logical_score': judgement.logical_score,
            'emotional_score': judgement.emotional_score,
            'discipline_score': judgement.discipline_score,
            'explanation': judgement.explanation,
            'loss_attribution': judgement.loss_attribution,
            'strengths': judgement.strengths or [],
            'weaknesses': judgement.weaknesses or [],
            'recommendations': judgement.recommendations or [],
            'model_used': judgement.model_used,
            'created_at': judgement.created_at.isoformat() if judgement.created_at else None
        }
    
    def get_judgement(self, trade_id: str) -> Optional[Dict[str, Any]]:
        """Get existing judgement for a trade."""
        db = self.db
        
        judgement = db.query(AITradeJudgement).filter(
            AITradeJudgement.trade_id == trade_id
        ).first()
        
        if judgement:
            return self._judgement_to_dict(judgement)
        return None
    
    def get_user_judgements(self, user_id: str, limit: int = 20) -> list:
        """Get recent judgements for a user."""
        db = self.db
        
        judgements = db.query(AITradeJudgement).filter(
            AITradeJudgement.user_id == user_id
        ).order_by(AITradeJudgement.created_at.desc()).limit(limit).all()
        
        return [self._judgement_to_dict(j) for j in judgements]
    
    def close(self):
        if self._db:
            self._db.close()
            self._db = None
