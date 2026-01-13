from typing import List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class AIEngine:
    """
    Core Intelligence Layer for Trading Analysis.
    Implements Skill Scoring and Bias Detection.
    """
    
    def analyze_skills(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a Skill Profile (0-100) based on trade history.
        """
        if not trades:
            return self._empty_skill_profile()
            
        df = pd.DataFrame(trades)
        
        # 1. Profitability Score (0-100)
        # Based on Win Rate and Risk/Reward
        win_rate = len(df[df['profit_loss'] > 0]) / len(df) if len(df) > 0 else 0
        avg_win = df[df['profit_loss'] > 0]['profit_loss'].mean() if not df[df['profit_loss'] > 0].empty else 0
        avg_loss = abs(df[df['profit_loss'] < 0]['profit_loss'].mean()) if not df[df['profit_loss'] < 0].empty else 1
        profit_factor = avg_win / avg_loss if avg_loss != 0 else 0
        
        profitability_score = min(100, (win_rate * 50) + (min(profit_factor, 3) * 16))
        
        # 2. Risk Management Score (0-100)
        # Penalize large losses (> 2x avg loss)
        risk_score = 100
        if not df.empty:
            large_losses = len(df[df['profit_loss'] < -2 * avg_loss])
            risk_score = max(0, 100 - (large_losses * 10))
            
        # 3. Consistency/Timing Score (0-100)
        # Simplified: Penalize holding losers too long vs winners
        # (Mock logic since we might not have exact hold times in basic history list yet)
        timing_score = 75 # Baseline
        
        overall_score = (profitability_score * 0.4) + (risk_score * 0.4) + (timing_score * 0.2)
        
        return {
            "overall_score": round(overall_score),
            "breakdown": {
                "profitability": round(profitability_score),
                "risk_management": round(risk_score),
                "timing": round(timing_score),
                "discipline": 80 # Placeholder
            },
            "history": self._generate_mock_skill_history(overall_score) # For charts
        }

    def detect_biases(self, trades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scans trade history for cognitive biases.
        """
        if not trades:
            return []
            
        biases = []
        df = pd.DataFrame(trades)
        # Ensure timestamps are datetime
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])
            df = df.sort_values('time')
        
        # 1. Overtrading Detection
        # Rule: > 5 trades in 1 hour with negative P&L result
        if len(df) > 5:
            # Group by hour? Simplified check: Rolling window
            # Just checking recent density for MVP
            recent_trades = df.tail(10)
            if not recent_trades.empty:
                time_span = recent_trades['time'].max() - recent_trades['time'].min()
                if time_span < timedelta(hours=1) and len(recent_trades) >= 5:
                     net_pl = recent_trades['profit_loss'].sum()
                     if net_pl < 0:
                         biases.append({
                             "name": "Overtrading",
                             "severity": "High",
                             "description": "High frequency of trades in short period resulting in losses.",
                             "recommendation": "Take a 30-minute break. Review your setup criteria."
                         })

        # 2. Revenge Trading
        # Rule: Trade size increases after a loss
        if len(df) >= 3:
            last_trade = df.iloc[-1]
            prev_trade = df.iloc[-2]
            
            # Simple assumption: market_value available or roughly implied by result
            # We don't have position size in plain 'profit_loss' history usually, but let's assume we pass full trade objects
            # If we only have P&L history, we can infer risk appetite changes
            
            if prev_trade['profit_loss'] < 0:
                 # Check if volume/size increased? 
                 # We need 'qty' or 'exposure' in history. Assuming we might parse it or have it.
                 pass

        # 3. FOMO (Fear Of Missing Out)
        # Rule: Entering trades after large price moves (requires market context, simplified here)
        # Placeholder for MVP
        
        return biases

    def _empty_skill_profile(self):
        return {
            "overall_score": 0,
            "breakdown": {
                "profitability": 0,
                "risk_management": 0,
                "timing": 0,
                "discipline": 0
            },
            "history": []
        }
        
    def _generate_mock_skill_history(self, current_score):
        # Generate a realistic looking improvement curve ending at current_score
        history = []
        days = 30
        start_score = max(0, current_score - 15)
        
        for i in range(days):
            # Slow drift upwards with noise
            progress = i / days
            score = start_score + (progress * 15) + np.random.normal(0, 2)
            history.append({
                "date": (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d"),
                "score": round(min(100, max(0, score)))
            })
        return history
