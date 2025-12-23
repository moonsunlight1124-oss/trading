"""Risk metrics calculation"""

import numpy as np
import pandas as pd
from typing import Union


def calculate_var(returns: Union[pd.Series, np.ndarray], confidence_level: float = 0.95) -> float:
    """
    Calculate Value at Risk (VaR)
    
    Args:
        returns: Series or array of returns
        confidence_level: Confidence level (e.g., 0.95 for 95% VaR)
        
    Returns:
        VaR value (positive number)
    """
    if isinstance(returns, pd.Series):
        returns = returns.dropna().values
    
    if len(returns) == 0:
        return 0.0
    
    return abs(np.percentile(returns, (1 - confidence_level) * 100))


def calculate_cvar(returns: Union[pd.Series, np.ndarray], confidence_level: float = 0.95) -> float:
    """
    Calculate Conditional Value at Risk (CVaR) / Expected Shortfall
    
    Args:
        returns: Series or array of returns
        confidence_level: Confidence level
        
    Returns:
        CVaR value (positive number)
    """
    if isinstance(returns, pd.Series):
        returns = returns.dropna().values
    
    if len(returns) == 0:
        return 0.0
    
    var = calculate_var(returns, confidence_level)
    threshold = -var  # Negative for losses
    tail_losses = returns[returns <= threshold]
    
    if len(tail_losses) == 0:
        return var
    
    return abs(tail_losses.mean())


class RiskMetrics:
    """Comprehensive risk metrics calculator"""
    
    def __init__(self, returns: pd.Series):
        """
        Initialize risk metrics calculator
        
        Args:
            returns: Series of portfolio returns
        """
        self.returns = returns.dropna()
        
    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
        """Calculate Sharpe ratio"""
        if len(self.returns) == 0:
            return 0.0
        
        excess_returns = self.returns - risk_free_rate / periods_per_year
        if excess_returns.std() == 0:
            return 0.0
        
        return np.sqrt(periods_per_year) * excess_returns.mean() / excess_returns.std()
    
    def calculate_sortino_ratio(self, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
        """Calculate Sortino ratio (downside deviation only)"""
        if len(self.returns) == 0:
            return 0.0
        
        excess_returns = self.returns - risk_free_rate / periods_per_year
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        
        downside_std = np.sqrt(periods_per_year) * downside_returns.std()
        if downside_std == 0:
            return 0.0
        
        return np.sqrt(periods_per_year) * excess_returns.mean() / downside_std
    
    def calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        if len(self.returns) == 0:
            return 0.0
        
        cumulative = (1 + self.returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        return abs(drawdown.min())
    
    def calculate_calmar_ratio(self, periods_per_year: int = 252) -> float:
        """Calculate Calmar ratio (return / max drawdown)"""
        if len(self.returns) == 0:
            return 0.0
        
        annual_return = self.returns.mean() * periods_per_year
        max_dd = self.calculate_max_drawdown()
        
        if max_dd == 0:
            return 0.0
        
        return annual_return / max_dd
    
    def calculate_var(self, confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk"""
        return calculate_var(self.returns, confidence_level)
    
    def calculate_cvar(self, confidence_level: float = 0.95) -> float:
        """Calculate Conditional Value at Risk"""
        return calculate_cvar(self.returns, confidence_level)
    
    def get_all_metrics(self, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> dict:
        """Get all risk metrics"""
        return {
            'sharpe_ratio': self.calculate_sharpe_ratio(risk_free_rate, periods_per_year),
            'sortino_ratio': self.calculate_sortino_ratio(risk_free_rate, periods_per_year),
            'max_drawdown': self.calculate_max_drawdown(),
            'calmar_ratio': self.calculate_calmar_ratio(periods_per_year),
            'var_95': self.calculate_var(0.95),
            'cvar_95': self.calculate_cvar(0.95),
            'volatility': self.returns.std() * np.sqrt(periods_per_year),
            'annual_return': self.returns.mean() * periods_per_year
        }

