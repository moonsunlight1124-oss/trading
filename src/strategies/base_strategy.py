"""Base class for all trading strategies"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


class BaseStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, name: str, initial_capital: float = 100000):
        """
        Initialize base strategy
        
        Args:
            name: Strategy name
            initial_capital: Starting capital
        """
        self.name = name
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}  # {symbol: quantity}
        self.trades = []  # List of trade records
        self.signals = []  # List of trading signals
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals from market data
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with signals (long, short, exit)
        """
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal: Dict, data: pd.DataFrame) -> float:
        """
        Calculate position size based on signal and risk parameters
        
        Args:
            signal: Signal dictionary with entry/exit info
            data: Current market data
            
        Returns:
            Position size (quantity)
        """
        pass
    
    def update_capital(self, pnl: float):
        """Update capital after trade"""
        self.capital += pnl
    
    def get_portfolio_value(self, prices: Dict[str, float]) -> float:
        """Calculate total portfolio value"""
        total = self.capital
        for symbol, quantity in self.positions.items():
            if symbol in prices:
                total += quantity * prices[symbol]
        return total
    
    def reset(self):
        """Reset strategy state"""
        self.capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.signals = []

