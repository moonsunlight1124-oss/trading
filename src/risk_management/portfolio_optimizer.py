"""Portfolio optimization using modern portfolio theory"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import List, Optional, Dict


class PortfolioOptimizer:
    """
    Portfolio optimizer using Markowitz Mean-Variance Optimization
    """
    
    def __init__(self, risk_free_rate: float = 0.0):
        """
        Initialize portfolio optimizer
        
        Args:
            risk_free_rate: Risk-free rate (annualized)
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        """Calculate returns from prices"""
        return prices.pct_change().dropna()
    
    def calculate_covariance_matrix(self, returns: pd.DataFrame) -> pd.DataFrame:
        """Calculate covariance matrix of returns"""
        return returns.cov() * 252  # Annualized
    
    def calculate_expected_returns(self, returns: pd.DataFrame) -> pd.Series:
        """Calculate expected returns"""
        return returns.mean() * 252  # Annualized
    
    def portfolio_performance(self, weights: np.ndarray, expected_returns: np.ndarray, 
                            cov_matrix: np.ndarray) -> tuple:
        """Calculate portfolio return and volatility"""
        portfolio_return = np.sum(expected_returns * weights)
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)
        return portfolio_return, portfolio_volatility
    
    def negative_sharpe(self, weights: np.ndarray, expected_returns: np.ndarray, 
                       cov_matrix: np.ndarray) -> float:
        """Negative Sharpe ratio for minimization"""
        portfolio_return, portfolio_volatility = self.portfolio_performance(
            weights, expected_returns, cov_matrix
        )
        sharpe = (portfolio_return - self.risk_free_rate) / portfolio_volatility
        return -sharpe
    
    def optimize_max_sharpe(
        self,
        returns: pd.DataFrame,
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        Optimize portfolio for maximum Sharpe ratio
        
        Args:
            returns: DataFrame of asset returns
            constraints: Optional constraints dictionary
            
        Returns:
            Dictionary with optimal weights and performance metrics
        """
        expected_returns = self.calculate_expected_returns(returns).values
        cov_matrix = self.calculate_covariance_matrix(returns).values
        
        n_assets = len(expected_returns)
        
        # Initial guess: equal weights
        initial_weights = np.array([1.0 / n_assets] * n_assets)
        
        # Constraints: weights sum to 1
        constraints_opt = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        
        # Bounds: weights between 0 and 1 (long-only)
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Optimize
        result = minimize(
            self.negative_sharpe,
            initial_weights,
            args=(expected_returns, cov_matrix),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints_opt
        )
        
        optimal_weights = result.x
        
        # Calculate performance
        portfolio_return, portfolio_volatility = self.portfolio_performance(
            optimal_weights, expected_returns, cov_matrix
        )
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
        
        return {
            'weights': pd.Series(optimal_weights, index=returns.columns),
            'expected_return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': sharpe_ratio
        }
    
    def optimize_min_volatility(
        self,
        returns: pd.DataFrame
    ) -> Dict:
        """
        Optimize portfolio for minimum volatility
        
        Returns:
            Dictionary with optimal weights and performance metrics
        """
        expected_returns = self.calculate_expected_returns(returns).values
        cov_matrix = self.calculate_covariance_matrix(returns).values
        
        n_assets = len(expected_returns)
        initial_weights = np.array([1.0 / n_assets] * n_assets)
        
        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        result = minimize(
            portfolio_volatility,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_weights = result.x
        portfolio_return, portfolio_volatility = self.portfolio_performance(
            optimal_weights, expected_returns, cov_matrix
        )
        
        return {
            'weights': pd.Series(optimal_weights, index=returns.columns),
            'expected_return': portfolio_return,
            'volatility': portfolio_volatility
        }
    
    def risk_parity_weights(self, returns: pd.DataFrame) -> pd.Series:
        """
        Calculate risk parity weights (equal risk contribution)
        """
        cov_matrix = self.calculate_covariance_matrix(returns).values
        inv_cov = np.linalg.inv(cov_matrix)
        
        # Risk parity: weights proportional to inverse volatility
        vols = np.sqrt(np.diag(cov_matrix))
        inv_vols = 1.0 / vols
        weights = inv_vols / np.sum(inv_vols)
        
        return pd.Series(weights, index=returns.columns)

