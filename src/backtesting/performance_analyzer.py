"""Performance analysis and visualization"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Optional


class PerformanceAnalyzer:
    """Analyze and visualize backtest performance"""
    
    def __init__(self, results: pd.DataFrame):
        """
        Initialize performance analyzer
        
        Args:
            results: Backtest results DataFrame
        """
        self.results = results
    
    def plot_equity_curve(self, ax: Optional[plt.Axes] = None) -> plt.Axes:
        """Plot equity curve"""
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 6))
        
        equity = self.results.get('equity_curve', self.results.get('portfolio_value'))
        if equity is not None:
            ax.plot(equity.index, equity.values, linewidth=2, label='Portfolio Value')
            ax.set_title('Equity Curve', fontsize=14, fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Portfolio Value ($)')
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        return ax
    
    def plot_drawdown(self, ax: Optional[plt.Axes] = None) -> plt.Axes:
        """Plot drawdown"""
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 4))
        
        equity = self.results.get('equity_curve', self.results.get('portfolio_value'))
        if equity is not None:
            running_max = equity.expanding().max()
            drawdown = (equity - running_max) / running_max * 100
            
            ax.fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
            ax.plot(drawdown.index, drawdown.values, color='darkred', linewidth=1.5)
            ax.set_title('Drawdown', fontsize=14, fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Drawdown (%)')
            ax.grid(True, alpha=0.3)
        
        return ax
    
    def plot_returns_distribution(self, ax: Optional[plt.Axes] = None) -> plt.Axes:
        """Plot returns distribution"""
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
        
        returns = self.results.get('returns', pd.Series())
        if len(returns) > 0:
            returns_clean = returns.dropna()
            ax.hist(returns_clean * 100, bins=50, alpha=0.7, edgecolor='black')
            ax.axvline(returns_clean.mean() * 100, color='red', linestyle='--', 
                      linewidth=2, label=f'Mean: {returns_clean.mean()*100:.2f}%')
            ax.set_title('Returns Distribution', fontsize=14, fontweight='bold')
            ax.set_xlabel('Daily Return (%)')
            ax.set_ylabel('Frequency')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        return ax
    
    def generate_report(self, metrics: Dict) -> str:
        """Generate text report of performance metrics"""
        report = "\n" + "="*60 + "\n"
        report += "BACKTEST PERFORMANCE REPORT\n"
        report += "="*60 + "\n\n"
        
        report += f"Total Return:        {metrics.get('total_return', 0):.2f}%\n"
        report += f"Annual Return:       {metrics.get('annual_return', 0)*100:.2f}%\n"
        report += f"Volatility:          {metrics.get('volatility', 0)*100:.2f}%\n"
        report += f"Sharpe Ratio:        {metrics.get('sharpe_ratio', 0):.2f}\n"
        report += f"Sortino Ratio:       {metrics.get('sortino_ratio', 0):.2f}\n"
        report += f"Max Drawdown:        {metrics.get('max_drawdown', 0)*100:.2f}%\n"
        report += f"Calmar Ratio:        {metrics.get('calmar_ratio', 0):.2f}\n"
        report += f"VaR (95%):           {metrics.get('var_95', 0)*100:.2f}%\n"
        report += f"CVaR (95%):          {metrics.get('cvar_95', 0)*100:.2f}%\n"
        report += f"Number of Trades:    {metrics.get('num_trades', 0)}\n"
        report += f"Win Rate:            {metrics.get('win_rate', 0)*100:.2f}%\n"
        
        report += "\n" + "="*60 + "\n"
        
        return report

