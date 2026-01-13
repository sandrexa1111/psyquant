# PsyQuant - Behavioral Intelligence Trading Platform

PsyQuant is a next-generation trading platform that focuses on the **trader** rather than just the charts. By integrating behavioral psychology metrics, AI-driven strategy analysis, and real-time risk management, PsyQuant helps traders identify and eliminate emotional decision-making.

## 🚀 Key Features

*   **🧬 Strategy DNA Engine**: Automatically analyzes your trade history to identify your unique trading fingerprints (e.g., "Momentum Scalper", "Swing Reversal"). Detects when you deviate from your proven strategies.
*   **🛡️ Psychological Risk Firewall**: A real-time "circuit breaker" that monitors your trading behavior for signs of "tilt" or emotional distress and can block high-risk trades before they happen.
*   **🧠 AI Reflection Journal**: An intelligent journaling system that analyzes your entries for cognitive biases and emotional keywords, providing constructive feedback using LLMs.
*   **backtrack Trade Replay**: Replay your past trades with full market context (Price, RSI, Indicators) at the exact moment of execution to review your decision-making process.
*   **Simulation Mode**: Built-in local execution simulator for risk-free practice and strategy validation.

## 🛠️ Architecture

*   **Backend**: Python (FastAPI), SQLAlchemy, Pydantic
*   **Frontend**: React, Vite, TailwindCSS, Recharts
*   **Database**: SQLite (Dev), Supabase (Prod)
*   **AI/LLM**: Google Gemini (Integration ready)
*   **Brokerage**: Alpaca (Paper/Live)

## 📦 Installation

### Prerequisites
*   Python 3.10+
*   Node.js 18+

### Backend Setup
1.  Clone the repository:
    ```bash
    git clone https://github.com/sandrexa1111/psyquant.git
    cd psyquant
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure environment variables in `.env` (see `.env.example`).
5.  Run the server:
    ```bash
    python main.py
    # API available at http://127.0.0.1:8000
    ```

### Frontend Setup
1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    # UI available at http://localhost:5173
    ```

## 🧪 Testing & Verification

The project includes a suite of system checks to verify component isolation and logic:
```bash
python run_system_checks.py
```
This script verifies:
*   Strategy Alignment Logic
*   Psychological Firewall Triggers
*   Multi-tenant Isolation
*   Authentication Security

## 📝 Usage

1.  Open the dashboard at `http://localhost:5173`.
2.  The system defaults to **Simulation Mode** with a demo account.
3.  Go to **Settings** to reset your simulation balance.
4.  Navigate to **Trade** to place orders.
5.  View **Analytics** to see your Strategy DNA and Risk Score evolve.

## 📄 License
MIT
