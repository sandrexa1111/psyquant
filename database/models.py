from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, JSON, Date, Text, Numeric, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import uuid
from datetime import datetime

# Helper to generate UUIDs
def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    subscription_tier = Column(String, default="free")  # 'free', 'pro', 'team'
    trial_ends_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    last_login_at = Column(DateTime)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    alpaca_credentials = relationship("AlpacaCredential", back_populates="user", uselist=False)
    sandbox_account = relationship("SandboxAccount", back_populates="user", uselist=False)
    trades = relationship("Trade", back_populates="user")
    biases = relationship("DetectedBias", back_populates="user")
    strategy_clusters = relationship("StrategyCluster", back_populates="user")
    skill_scores = relationship("SkillScore", back_populates="user")
    insights = relationship("AIInsight", back_populates="user")
    chat_history = relationship("ChatHistory", back_populates="user")
    alerts = relationship("UserAlert", back_populates="user")
    # Behavior Intelligence relationships
    behavior_events = relationship("BehaviorEvent", back_populates="user")
    psych_risk_snapshots = relationship("PsychRiskSnapshot", back_populates="user")
    strategy_fingerprints = relationship("StrategyFingerprint", back_populates="user")
    ai_judgements = relationship("AITradeJudgement", back_populates="user")
    journal_entries = relationship("JournalEntry", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    experience_level = Column(String)  # 'beginner', 'intermediate', 'expert'
    # SQLAlchemy doesn't strictly support ARRAY in SQLite, so we might need JSON for compatibility if strictly using SQLite features, 
    # but for Postgres strictness we use JSON for lists if ARRAY is not preferred universally. 
    # However, Section 9 specified TEXT[], so we will use JSON which is more portable for lists in simple ORMs or ARRAY if we were sure of Postgres.
    # To be safe for SQLite/Postgres hybrid in MVP, we often use JSON for string arrays.
    trading_styles = Column(JSON)  # ['day_trading', 'swing_trading']
    risk_tolerance = Column(String)  # 'conservative', 'moderate', 'aggressive'
    goals = Column(JSON)
    preferred_ai_tone = Column(String, default='supportive')
    onboarding_completed = Column(Boolean, default=False)

    user = relationship("User", back_populates="profile")

class AlpacaCredential(Base):
    __tablename__ = "alpaca_credentials"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    api_key_id = Column(String, nullable=False)  # Encrypted
    secret_key = Column(String, nullable=False)  # Encrypted
    account_type = Column(String, default="paper")  # 'paper' or 'live'
    last_synced_at = Column(DateTime)
    sync_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="alpaca_credentials")

class SandboxAccount(Base):
    __tablename__ = "sandbox_accounts"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    starting_balance = Column(Numeric(15, 2), default=100000.00)
    current_balance = Column(Numeric(15, 2))
    unrealized_pnl = Column(Numeric(15, 2), default=0)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="sandbox_account")
    orders = relationship("SandboxOrder", back_populates="account")
    positions = relationship("SandboxPosition", back_populates="account")

class SandboxOrder(Base):
    __tablename__ = "sandbox_orders"

    id = Column(String, primary_key=True, default=generate_uuid)
    sandbox_account_id = Column(String, ForeignKey("sandbox_accounts.id"))
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # 'buy' or 'sell'
    qty = Column(Numeric(15, 4), nullable=False)
    order_type = Column(String, nullable=False)  # 'market', 'limit', 'stop', 'stop_limit'
    limit_price = Column(Numeric(15, 4))
    stop_price = Column(Numeric(15, 4))
    status = Column(String, default="pending")  # 'pending', 'filled', 'cancelled'
    filled_price = Column(Numeric(15, 4))
    filled_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

    account = relationship("SandboxAccount", back_populates="orders")

class SandboxPosition(Base):
    __tablename__ = "sandbox_positions"

    id = Column(String, primary_key=True, default=generate_uuid)
    sandbox_account_id = Column(String, ForeignKey("sandbox_accounts.id"))
    symbol = Column(String, nullable=False)
    qty = Column(Numeric(15, 4), nullable=False)
    avg_entry_price = Column(Numeric(15, 4), nullable=False)
    current_price = Column(Numeric(15, 4))
    unrealized_pnl = Column(Numeric(15, 2))
    updated_at = Column(DateTime, default=func.now())

    account = relationship("SandboxAccount", back_populates="positions")

class Trade(Base):
    __tablename__ = "trades"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    source = Column(String, nullable=False)  # 'alpaca' or 'sandbox'
    external_id = Column(String)
    symbol = Column(String, nullable=False, index=True)
    side = Column(String, nullable=False)
    qty = Column(Numeric(15, 4), nullable=False)
    entry_price = Column(Numeric(15, 4), nullable=False)
    exit_price = Column(Numeric(15, 4))
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime)
    pnl = Column(Numeric(15, 2))
    pnl_pct = Column(Numeric(10, 4))
    holding_time_seconds = Column(Integer)
    status = Column(String, default="open")  # 'open' or 'closed'
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="trades")
    snapshot = relationship("TradeSnapshot", back_populates="trade", uselist=False)
    analysis = relationship("TradeAnalysis", back_populates="trade", uselist=False)
    biases = relationship("DetectedBias", back_populates="trade")

class TradeSnapshot(Base):
    __tablename__ = "trade_snapshots"

    trade_id = Column(String, ForeignKey("trades.id"), primary_key=True)
    ohlcv_data = Column(JSON)  # Candlestick data ±2 hours
    technical_indicators = Column(JSON)  # RSI, MACD, etc.
    news_headlines = Column(JSON)  # [{time, headline, source}]
    market_regime = Column(String)  # 'trending_up', 'ranging', 'volatile'
    created_at = Column(DateTime, default=func.now())

    trade = relationship("Trade", back_populates="snapshot")

class TradeAnalysis(Base):
    __tablename__ = "trade_analysis"

    trade_id = Column(String, ForeignKey("trades.id"), primary_key=True)
    why_failed = Column(Text)
    why_succeeded = Column(Text)
    pattern_match = Column(Text)
    counterfactual = Column(Text)
    actionable_fix = Column(Text)
    generated_at = Column(DateTime, default=func.now())

    trade = relationship("Trade", back_populates="analysis")

class DetectedBias(Base):
    __tablename__ = "detected_biases"

    id = Column(String, primary_key=True, default=generate_uuid)
    trade_id = Column(String, ForeignKey("trades.id"))
    user_id = Column(String, ForeignKey("users.id"))
    bias_type = Column(String, nullable=False)  # 'FOMO', 'Overtrading', 'Hesitation'
    severity = Column(Numeric(5, 2))  # 0-100 score
    confidence = Column(Numeric(5, 2))  # 0-1 confidence
    evidence = Column(JSON)  # {run_up_pct: 0.15, rsi: 73}
    detected_at = Column(DateTime, default=func.now())

    trade = relationship("Trade", back_populates="biases")
    user = relationship("User", back_populates="biases")

class StrategyCluster(Base):
    __tablename__ = "strategy_clusters"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    strategy_name = Column(String, nullable=False)
    trade_ids = Column(JSON)  # Array of trade IDs
    characteristics = Column(JSON)
    performance_stats = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="strategy_clusters")

class SkillScore(Base):
    __tablename__ = "skill_scores"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    score_date = Column(Date, nullable=False)
    profitability = Column(Numeric(5, 2))
    risk_management = Column(Numeric(5, 2))
    timing = Column(Numeric(5, 2))
    discipline = Column(Numeric(5, 2))
    overall = Column(Numeric(5, 2))
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="skill_scores")

class AIInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    insight_text = Column(Text, nullable=False)
    insight_type = Column(String)  # 'warning', 'opportunity', 'learning'
    priority = Column(Integer, default=50)
    generated_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)

    user = relationship("User", back_populates="insights")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    embedded_data = Column(JSON)
    suggested_actions = Column(JSON)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="chat_history")

class UserAlert(Base):
    __tablename__ = "user_alerts"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    alert_type = Column(String, nullable=False)  # 'bias_warning', 'daily_loss_limit'
    trigger_conditions = Column(JSON)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="alerts")
    notifications = relationship("AlertNotification", back_populates="alert")

class AlertNotification(Base):
    __tablename__ = "alert_notifications"

    id = Column(String, primary_key=True, default=generate_uuid)
    alert_id = Column(String, ForeignKey("user_alerts.id"))
    triggered_at = Column(DateTime, default=func.now())
    message = Column(Text, nullable=False)
    was_read = Column(Boolean, default=False)

    alert = relationship("UserAlert", back_populates="notifications")


# ============================================================================
# BEHAVIOR INTELLIGENCE MODELS
# ============================================================================

class BehaviorEvent(Base):
    """
    Represents a single event in the behavior chain:
    Emotion → Decision → Execution → Outcome → Reflection
    """
    __tablename__ = "behavior_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    trade_id = Column(String, ForeignKey("trades.id"), nullable=True, index=True)
    chain_id = Column(String, nullable=False, index=True)  # Groups events in a chain
    
    event_type = Column(String, nullable=False)  # 'emotion', 'decision', 'execution', 'outcome', 'reflection'
    sequence_order = Column(Integer, nullable=False)  # 1-5 for the chain
    
    # Event content
    content = Column(JSON, nullable=False)  # {state, intensity, triggers, notes, metrics}
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="behavior_events")
    trade = relationship("Trade", backref="behavior_events")


class PsychRiskSnapshot(Base):
    """
    Psychological Risk Score (PRS) snapshot.
    Score 0-100 with risk state classification.
    """
    __tablename__ = "psych_risk_snapshots"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    score = Column(Integer, nullable=False)  # 0-100
    risk_state = Column(String, nullable=False)  # 'low', 'moderate', 'high', 'critical'
    
    # Factor breakdown
    factors = Column(JSON, nullable=False)  # {loss_streak, position_deviation, frequency_change, holding_anomaly}
    
    # Context
    trade_window_start = Column(DateTime)  # Analysis period start
    trade_window_end = Column(DateTime)  # Analysis period end
    trades_analyzed = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="psych_risk_snapshots")


class StrategyFingerprint(Base):
    """
    AI-discovered strategy DNA profile.
    Clusters trades into distinct strategy fingerprints.
    """
    __tablename__ = "strategy_fingerprints"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    strategy_name = Column(String, nullable=False)  # AI-generated name
    
    # Strategy characteristics
    entry_style = Column(String)  # 'momentum', 'mean_reversion', 'breakout', 'scalping'
    holding_time_avg = Column(Integer)  # Average seconds
    volatility_preference = Column(String)  # 'low', 'medium', 'high'
    
    # Performance metrics
    win_rate = Column(Numeric(5, 2))  # 0-100
    risk_reward_ratio = Column(Numeric(5, 2))
    avg_pnl = Column(Numeric(15, 2))
    total_pnl = Column(Numeric(15, 2))
    trade_count = Column(Integer, default=0)
    
    # Trade clustering
    trade_ids = Column(JSON)  # List of trade IDs in this cluster
    feature_vector = Column(JSON)  # Normalized features for clustering
    
    # Active status
    is_active = Column(Boolean, default=True)
    last_trade_at = Column(DateTime)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="strategy_fingerprints")


class AITradeJudgement(Base):
    """
    LLM-generated trade analysis and scoring.
    Provides logical, emotional, and discipline scores with explanation.
    """
    __tablename__ = "ai_trade_judgements"

    id = Column(String, primary_key=True, default=generate_uuid)
    trade_id = Column(String, ForeignKey("trades.id"), nullable=False, unique=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Scores (0-100)
    logical_score = Column(Integer, nullable=False)
    emotional_score = Column(Integer, nullable=False)
    discipline_score = Column(Integer, nullable=False)
    
    # AI explanation
    explanation = Column(Text, nullable=False)
    
    # Loss attribution classification
    loss_attribution = Column(String)  # 'market_noise', 'strategy_flaw', 'psychological_error', 'none'
    
    # Structured analysis
    strengths = Column(JSON)  # List of identified strengths
    weaknesses = Column(JSON)  # List of identified weaknesses
    recommendations = Column(JSON)  # Actionable recommendations
    
    # LLM metadata
    model_used = Column(String)  # 'gemini-pro', 'gpt-4', etc.
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    trade = relationship("Trade", backref="ai_judgement", uselist=False)
    user = relationship("User", back_populates="ai_judgements")


# ============================================================================
# LONGITUDINAL INTELLIGENCE MODELS
# ============================================================================

class BehaviorEvolution(Base):
    """
    Tracks behavior metrics over time for trend analysis.
    Enables "Your discipline improved 34% in 21 days" narratives.
    """
    __tablename__ = "behavior_evolution"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Metric being tracked
    metric_type = Column(String, nullable=False)  # 'discipline', 'risk_management', 'consistency', 'profitability', 'timing'
    
    # Score for this period
    score = Column(Numeric(5, 2), nullable=False)  # 0-100
    
    # Time period
    period_type = Column(String, nullable=False)  # 'daily', 'weekly', 'monthly'
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Change tracking
    previous_score = Column(Numeric(5, 2))
    change_pct = Column(Numeric(6, 2))  # Percentage change vs previous period
    trend_direction = Column(String)  # 'improving', 'declining', 'stable'
    
    # Supporting data
    trades_analyzed = Column(Integer, default=0)
    contributing_factors = Column(JSON)  # Factors that influenced the score
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", backref="behavior_evolution")


class StrategyDrift(Base):
    """
    Detects and tracks changes in strategy DNA over time.
    Alerts users when their trading style shifts significantly.
    """
    __tablename__ = "strategy_drift"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    fingerprint_id = Column(String, ForeignKey("strategy_fingerprints.id"), nullable=True)
    
    # Drift measurement
    drift_score = Column(Numeric(5, 2), nullable=False)  # 0-100 (high = significant change)
    drift_severity = Column(String)  # 'minor', 'moderate', 'significant', 'major'
    
    # What changed
    old_characteristics = Column(JSON)  # Previous strategy traits
    new_characteristics = Column(JSON)  # Current strategy traits
    changed_dimensions = Column(JSON)  # List of specific changes
    
    # Context
    comparison_period_days = Column(Integer, default=30)
    trades_before = Column(Integer)
    trades_after = Column(Integer)
    
    # Interpretation
    interpretation = Column(Text)  # AI-generated explanation of drift
    is_positive = Column(Boolean)  # Is this drift an improvement?
    
    detected_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", backref="strategy_drifts")
    fingerprint = relationship("StrategyFingerprint", backref="drifts")


# ============================================================================
# AI CONSISTENCY LAYER MODELS
# ============================================================================

class AIInsightVersion(Base):
    """
    Tracks AI insight versions for consistency and transparency.
    Shows users: "AI confidence: 92% (based on 187 similar trades)"
    """
    __tablename__ = "ai_insight_versions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # What type of insight
    insight_type = Column(String, nullable=False)  # 'judgement', 'risk_score', 'strategy_dna', 'pattern'
    insight_id = Column(String, index=True)  # Reference to the specific insight
    
    # Confidence scoring
    confidence_score = Column(Integer, nullable=False)  # 0-100
    similar_trade_count = Column(Integer, default=0)  # Number of similar trades analyzed
    
    # Version tracking
    version_hash = Column(String)  # Hash of input data for change detection
    
    # Explanation data
    explanation_summary = Column(Text)  # Condensed explanation
    reasoning = Column(JSON)  # Detailed reasoning breakdown
    
    # Optional embedding for similarity search
    embedding_vector = Column(JSON)  # Store as JSON array for SQLite compatibility
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", backref="ai_insight_versions")


class AIConfidenceMetric(Base):
    """
    Stores confidence calculation breakdown for AI insights.
    Enables transparency: showing users exactly how confidence was calculated.
    """
    __tablename__ = "ai_confidence_metrics"

    id = Column(String, primary_key=True, default=generate_uuid)
    insight_version_id = Column(String, ForeignKey("ai_insight_versions.id"), nullable=False, index=True)
    
    # Confidence components
    base_confidence = Column(Numeric(5, 2))  # Base score from model
    sample_size_boost = Column(Numeric(5, 2))  # Bonus from large sample
    consistency_bonus = Column(Numeric(5, 2))  # Bonus from consistent patterns
    recency_factor = Column(Numeric(5, 2))  # Weight based on data recency
    
    # Final calculation
    final_confidence = Column(Integer, nullable=False)  # Computed final score
    
    # Reasoning
    reasoning = Column(Text)  # Human-readable explanation
    contributing_factors = Column(JSON)  # List of factors that influenced score
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    insight_version = relationship("AIInsightVersion", backref="confidence_metrics")


# ============================================================================
# BEHAVIORAL ALERTS ENGINE MODELS
# ============================================================================

class BehaviorPattern(Base):
    """
    Detected personal behavioral patterns.
    Examples:
    - "You usually overtrade after 2 losses"
    - "Your worst trades happen when RSI is between 40-50"
    - "You break rules mostly after profitable streaks"
    """
    __tablename__ = "behavior_patterns"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Pattern identification
    pattern_type = Column(String, nullable=False)  # 'overtrade_after_loss', 'break_rules_after_win', 'rsi_blind_spot', 'time_of_day_weakness'
    pattern_name = Column(String, nullable=False)  # Human-readable name
    pattern_description = Column(Text, nullable=False)  # Full description
    
    # Trigger conditions
    trigger_conditions = Column(JSON, nullable=False)  # {losses_before: 2, typically_within_hours: 1}
    
    # Pattern statistics
    confidence = Column(Numeric(5, 2), nullable=False)  # 0-100 confidence in pattern
    occurrence_count = Column(Integer, default=0)  # How many times detected
    accuracy_rate = Column(Numeric(5, 2))  # Historical accuracy of predictions
    
    # Example trades
    example_trade_ids = Column(JSON)  # Trade IDs that demonstrate pattern
    
    # Status
    is_active = Column(Boolean, default=True)
    severity = Column(String, default='moderate')  # 'info', 'warning', 'critical'
    
    last_triggered_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="detected_patterns")
    alerts = relationship("PatternAlert", back_populates="pattern")


class PatternAlert(Base):
    """
    Alerts triggered when a behavior pattern is about to happen or has happened.
    Provides personalized behavioral defense.
    """
    __tablename__ = "pattern_alerts"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    pattern_id = Column(String, ForeignKey("behavior_patterns.id"), nullable=False, index=True)
    
    # Alert content
    alert_type = Column(String, nullable=False)  # 'pre_trade_warning', 'post_trade_review', 'pattern_emerging'
    alert_message = Column(Text, nullable=False)
    severity = Column(String, default='warning')  # 'info', 'warning', 'critical'
    
    # Context
    triggering_context = Column(JSON)  # What conditions matched
    related_trade_ids = Column(JSON)  # Trades that triggered this
    
    # User interaction
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime)
    user_feedback = Column(String)  # 'helpful', 'not_helpful', 'false_alarm'
    
    # Timing
    triggered_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)  # When alert is no longer relevant
    
    # Relationships
    user = relationship("User", backref="pattern_alerts")
    pattern = relationship("BehaviorPattern", back_populates="alerts")



class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(JSON)  # ["FOMO", "Win", "Strategy Loophole"]
    sentiment_score = Column(Numeric(5, 2))  # -1.0 to 1.0 (or 0-100 normalized)
    ai_feedback = Column(Text)
    trade_id = Column(String, ForeignKey("trades.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="journal_entries")
    trade = relationship("Trade")
