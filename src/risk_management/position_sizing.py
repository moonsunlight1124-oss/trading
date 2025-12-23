"""Position sizing algorithms"""

import numpy as np
import pandas as pd
from typing import Optional


class PositionSizer:
    """Base class for position sizing algorithms"""
    
    def calculate_size(
        self,
        capital: float,
        price: float,
        volatility: Optional[float] = None,
        expected_return: Optional[float] = None
    ) -> float:
        """
        Calculate position size
        
        Args:
            capital: Available capital
            price: Asset price
            volatility: Asset volatility (annualized)
            expected_return: Expected return (annualized)
            
        Returns:
            Position quantity
        """
        raise NotImplementedError


class KellyCriterion(PositionSizer):
    """
    Kelly Criterion for optimal position sizing
    f* = (p * b - q) / b
    where p = win probability, q = loss probability, b = win/loss ratio
    """
    
    def __init__(self, fraction: float = 0.25):
        """
        Initialize Kelly Criterion
        
        Args:
            fraction: Fraction of full Kelly to use (0.25 = quarter Kelly, safer)
        """
        self.fraction = fraction
    
    def calculate_size(
        self,
        capital: float,
        price: float,
        volatility: Optional[float] = None,
        expected_return: Optional[float] = None,
        win_probability: float = 0.5,
        win_loss_ratio: float = 1.0
    ) -> float:
        """
        Calculate position size using Kelly Criterion
        
        Args:
            win_probability: Probability of winning trade
            win_loss_ratio: Average win / average loss
        """
        if expected_return is not None and volatility is not None:
            # Alternative: f* = expected_return / variance
            if volatility > 0:
                kelly_fraction = expected_return / (volatility ** 2)
                kelly_fraction = np.clip(kelly_fraction * self.fraction, 0, 0.5)
            else:
                kelly_fraction = 0
        else:
            # Standard Kelly formula
            q = 1 - win_probability  # Loss probability
            if win_loss_ratio > 0:
                kelly_fraction = (win_probability * win_loss_ratio - q) / win_loss_ratio
                kelly_fraction = max(0, kelly_fraction)  # No negative positions
                kelly_fraction = min(kelly_fraction, 0.5)  # Cap at 50%
                kelly_fraction *= self.fraction
            else:
                kelly_fraction = 0
        
        position_value = capital * kelly_fraction
        return position_value / price


class RiskParity(PositionSizer):
    """
    Risk Parity position sizing
    Equalizes risk contribution across positions
    """
    
    def __init__(self, target_volatility: float = 0.15):
        """
        Initialize Risk Parity
        
        Args:
            target_volatility: Target portfolio volatility (annualized)
        """
        self.target_volatility = target_volatility
    
    def calculate_size(
        self,
        capital: float,
        price: float,
        volatility: Optional[float] = None,
        expected_return: Optional[float] = None,
        portfolio_volatility: Optional[float] = None
    ) -> float:
        """
        Calculate position size to achieve target volatility
        """
        if volatility is None or volatility == 0:
            return 0.0
        
        # Convert annualized volatility to position-level
        daily_vol = volatility / np.sqrt(252)
        
        # Calculate position size to target volatility
        if portfolio_volatility is not None and portfolio_volatility > 0:
            # Adjust based on current portfolio volatility
            vol_ratio = self.target_volatility / portfolio_volatility
        else:
            vol_ratio = 1.0
        
        # Position size inversely proportional to volatility
        risk_weight = (1.0 / daily_vol) * vol_ratio
        position_value = capital * risk_weight * 0.1  # Scale factor
        
        return position_value / price


class FixedFractional(PositionSizer):
    """Fixed fractional position sizing"""
    
    def __init__(self, fraction: float = 0.1):
        """
        Initialize fixed fractional sizing
        
        Args:
            fraction: Fraction of capital per position
        """
        self.fraction = fraction
    
    def calculate_size(
        self,
        capital: float,
        price: float,
        volatility: Optional[float] = None,
        expected_return: Optional[float] = None
    ) -> float:
        """Calculate fixed fractional position size"""
        position_value = capital * self.fraction
        return position_value / price

