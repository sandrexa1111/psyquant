from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

class TradingProvider(ABC):
    """
    Abstract Base Class for trading data and execution.
    Standardizes interaction for both Alpaca API and Local Simulation.
    """

    @abstractmethod
    def get_account(self) -> Dict[str, Any]:
        """Returns account details: cash, equity, buying_power, status."""
        pass

    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """Returns current open positions."""
        pass

    @abstractmethod
    def list_orders(self, status: str = "open", limit: int = 50) -> List[Dict[str, Any]]:
        """Returns list of orders."""
        pass

    @abstractmethod
    def submit_order(self, symbol: str, qty: float, side: str, type: str, 
                     time_in_force: str = "day", limit_price: Optional[float] = None) -> Dict[str, Any]:
        """Submits a new order."""
        pass

    @abstractmethod
    def get_portfolio_history(self, period: str = "1M", timeframe: str = "1D") -> List[Dict[str, Any]]:
        """Returns historical portfolio equity data."""
        pass
    
    @abstractmethod
    def get_bars(self, symbol: str, timeframe: str = "1Min", limit: int = 100) -> List[Dict[str, Any]]:
        """Returns market data bars (candles)."""
        pass
