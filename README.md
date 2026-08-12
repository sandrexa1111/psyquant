# PsyQuant

Experimental trading-behavior application built to explore how trade history, risk rules, journaling, and simulation can be combined in one system.

This is a learning / portfolio project, not a production trading product or financial-advice system.

## What is in the repository

- FastAPI backend with separate routers and service modules
- React/Vite frontend
- local trading simulator for development and testing
- strategy-profile and behavior/risk analysis services
- journal and longitudinal-analysis components
- optional Alpaca adapter for brokerage integration
- optional AI-related services for journal/consistency analysis
- database layer with local development support

## Structure

```text
psyquant/
├── main.py                 FastAPI application
├── routers/                API routes
├── services/               trading, behavior, risk and analysis logic
├── database/               persistence layer
├── frontend/               React/Vite client
├── run_system_checks.py    project-level checks
└── requirements.txt
```

## Running locally

### Backend

```bash
git clone https://github.com/sandrexa1111/psyquant.git
cd psyquant
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The API is available locally at `http://127.0.0.1:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend is served by Vite, normally at `http://localhost:5173`.

## Configuration

Local configuration belongs in `.env`. Do not commit credentials or brokerage/API secrets.

External integrations are optional; the repository includes a local simulation path so the project can be explored without placing real trades.

## Checks

```bash
python run_system_checks.py
```

The project also contains small stress, sanity, and behavior-simulation scripts used during development.

## Notes

PsyQuant is kept public because it shows an earlier full-stack project and some of the experimentation that led to my later work on verification and reliability. The architecture and terminology are experimental and should not be read as clinical or financial claims.

## License

MIT
