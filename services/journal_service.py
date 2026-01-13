"""
Journal Service
Handles journal entry management and AI reflection analysis using Google Gemini.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os
import uuid
from sqlalchemy.orm import Session
from database.models import JournalEntry, User
from database.database import SessionLocal

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None


class JournalService:
    """
    Service for managing journal entries and generating AI feedback.
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
            print("⚠️ Google Generative AI package not installed.")
            return
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return
        
        try:
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            print(f"⚠️ Failed to initialize Gemini: {e}")
            
    def create_entry(self, user_id: str, title: str, content: str, tags: List[str] = None, trade_id: str = None) -> Dict[str, Any]:
        """Create a new journal entry and optionally trigger AI analysis."""
        db = self.db
        
        entry = JournalEntry(
            user_id=user_id,
            title=title,
            content=content,
            tags=tags or [],
            trade_id=trade_id
        )
        
        db.add(entry)
        db.commit()
        db.refresh(entry)
        
        # Trigger analysis automatically if enough content
        if len(content) > 20 and self._model:
            try:
                self.analyze_entry(entry.id)
                db.refresh(entry)
            except Exception as e:
                print(f"Auto-analysis failed: {e}")
                
        return self._entry_to_dict(entry)
    
    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get a journal entry by ID."""
        entry = self.db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
        if entry:
            return self._entry_to_dict(entry)
        return None
        
    def get_user_entries(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get list of journal entries for a user."""
        entries = self.db.query(JournalEntry).filter(
            JournalEntry.user_id == user_id
        ).order_by(JournalEntry.created_at.desc()).limit(limit).offset(offset).all()
        
        return [self._entry_to_dict(e) for e in entries]

    def update_entry(self, entry_id: str, title: str = None, content: str = None, tags: List[str] = None) -> Optional[Dict[str, Any]]:
        """Update a journal entry."""
        db = self.db
        entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
        if not entry:
            return None
            
        if title:
            entry.title = title
        if content:
            entry.content = content
        if tags is not None:
            entry.tags = tags
            
        entry.updated_at = datetime.now()
        db.commit()
        db.refresh(entry)
        return self._entry_to_dict(entry)

    def delete_entry(self, entry_id: str) -> bool:
        """Delete a journal entry."""
        db = self.db
        entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
        if not entry:
            return False
            
        db.delete(entry)
        db.commit()
        return True

    def analyze_entry(self, entry_id: str) -> Dict[str, Any]:
        """Run AI analysis on a journal entry."""
        db = self.db
        entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
        if not entry:
            raise ValueError("Entry not found")
            
        if not self._model:
            # Fallback mock analysis
            return self._fallback_analysis(entry)
            
        prompt = self._build_prompt(entry)
        
        try:
            analysis = self._call_llm(prompt)
            
            # Update entry
            entry.sentiment_score = analysis['sentiment_score']
            entry.ai_feedback = analysis['feedback']
            
            # Merge existing tags with detected ones
            existing_tags = set(entry.tags or [])
            new_tags = set(analysis.get('tags', []))
            entry.tags = list(existing_tags.union(new_tags))
            
            db.commit()
            return self._entry_to_dict(entry)
            
        except Exception as e:
            print(f"Analysis failed: {e}")
            return self._fallback_analysis(entry)

    def _build_prompt(self, entry: JournalEntry) -> str:
        return f"""You are an expert trading psychologist/coach. Analyze this trader's journal entry.

Title: {entry.title}
Content: "{entry.content}"

Instructions:
1. Determine the Sentiment Score (0-100, where 0=Very Negative/Fearful, 50=Neutral, 100=Very Positive/Confident).
2. Detect 1-3 key cognitive biases or emotional states (e.g., FOMO, Revenge Trading, Overconfidence, Disciplined).
3. Provide brief, constructive feedback (1-2 sentences) to help the trader improve.

Respond ONLY with valid JSON:
{{
    "sentiment_score": <int 0-100>,
    "tags": ["<tag1>", "<tag2>"],
    "feedback": "<feedback text>"
}}
"""

    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        response = self._model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])
        return json.loads(text)

    def _fallback_analysis(self, entry: JournalEntry) -> Dict[str, Any]:
        """Mock analysis for when LLM is unavailable."""
        db = self.db
        entry.sentiment_score = 50
        entry.ai_feedback = "AI analysis unavailable. Please check your API key."
        db.commit()
        return self._entry_to_dict(entry)

    def _entry_to_dict(self, entry: JournalEntry) -> Dict[str, Any]:
        return {
            "id": entry.id,
            "user_id": entry.user_id,
            "title": entry.title,
            "content": entry.content,
            "tags": entry.tags,
            "sentiment_score": float(entry.sentiment_score) if entry.sentiment_score is not None else None,
            "ai_feedback": entry.ai_feedback,
            "trade_id": entry.trade_id,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
            "updated_at": entry.updated_at.isoformat() if entry.updated_at else None
        }

    def close(self):
        if self._db:
            self._db.close()
            self._db = None
