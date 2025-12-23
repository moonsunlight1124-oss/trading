"""Backtesting engine"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from ..strategies.base_strategy import BaseStrategy
from ..risk_management.risk_metrics import RiskMetrics


class Backtester:
    """
    Backtesting engine for trading strategies
    """
    
    def __init__(
        self,
        strategy: BaseStrategy,
        initial_capital: float = 100000,
        commission: float = 0.001,  # 0.1% commission
        slippage: float = 0.0005  # 0.05% slippage
    ):
        """
        Initialize backtester
        
        Args:
            strategy: Trading strategy instance
            initial_capital: Starting capital
            commission: Trading commission rate
            slippage: Slippage rate
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        self.capital = initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        
    def calculate_execution_price(self, signal_price: float, side: str) -> float:
        """
        Calculate execution price with slippage
        
        Args:
            signal_price: Signal price
            side: 'buy' or 'sell'
        """
        if side == 'buy':
            return signal_price * (1 + self.slippage)
        else:
            return signal_price * (1 - self.slippage)
    
    def calculate_commission_cost(self, trade_value: float) -> float:
        """Calculate commission cost"""
        return trade_value * self.commission
    
    def run(self, data: pd.DataFrame, price_column: str = 'close') -> pd.DataFrame:
        """
        Run backtest on historical data
        
        Args:
            data: DataFrame with OHLCV data
            price_column: Name of price column
            
        Returns:
            DataFrame with backtest results
        """
        # Generate signals
        signals_df = self.strategy.generate_signals(data)
        
        # Initialize tracking
        self.capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        
        results = data.copy()
        results['signal'] = signals_df.get('signal', 0)
        results['position'] = 0
        results['capital'] = self.initial_capital
        results['portfolio_value'] = self.initial_capital
        
        current_position = 0
        
        for i in range(len(results)):
            current_price = results.iloc[i][price_column]
            signal = results.iloc[i]['signal']
            
            # Check for position changes
            if signal != 0 and signal != current_position:
                # Enter new position
                if current_position == 0:
                    # Opening position
                    execution_price = self.calculate_execution_price(current_price, 'buy' if signal > 0 else 'sell')
                    
                    # Calculate position size
                    signal_dict = {
                        'signal': signal,
                        'price': execution_price
                    }
                    quantity = self.strategy.calculate_position_size(signal_dict, data.iloc[:i+1])
                    
                    trade_value = abs(quantity) * execution_price
                    commission_cost = self.calculate_commission_cost(trade_value)
                    
                    if self.capital >= trade_value + commission_cost:
                        self.positions[price_column] = quantity
                        current_position = signal
                        self.capital -= (trade_value + commission_cost)
                        
                        self.trades.append({
                            'timestamp': results.index[i],
                            'side': 'buy' if signal > 0 else 'sell',
                            'quantity': abs(quantity),
                            'price': execution_price,
                            'value': trade_value,
                            'commission': commission_cost
                        })
                
                # Exiting position
                elif (signal == 0 and current_position != 0):
                    if price_column in self.positions:
                        quantity = self.positions[price_column]
                        execution_price = self.calculate_execution_price(current_price, 'sell' if quantity > 0 else 'buy')
                        
                        trade_value = abs(quantity) * execution_price
                        commission_cost = self.calculate_commission_cost(trade_value)
                        
                        pnl = (execution_price - results.iloc[i-1][price_column]) * quantity if i > 0 else 0
                        
                        self.capital += trade_value - commission_cost
                        del self.positions[price_column]
                        current_position = 0
                        
                        self.trades.append({
                            'timestamp': results.index[i],
                            'side': 'exit',
                            'quantity': abs(quantity),
                            'price': execution_price,
                            'value': trade_value,
                            'commission': commission_cost,
                            'pnl': pnl
                        })
            
            # Update position
            results.iloc[i, results.columns.get_loc('position')] = current_position
            
            # Calculate portfolio value
            portfolio_value = self.capital
            if price_column in self.positions:
                portfolio_value += self.positions[price_column] * current_price
            
            results.iloc[i, results.columns.get_loc('capital')] = self.capital
            results.iloc[i, results.columns.get_loc('portfolio_value')] = portfolio_value
            self.equity_curve.append(portfolio_value)
        
        results['equity_curve'] = self.equity_curve
        results['returns'] = results['portfolio_value'].pct_change()
        
        return results
    
    def get_performance_metrics(self, results: pd.DataFrame) -> Dict:
        """Calculate performance metrics"""
        returns = results['returns'].dropna()
        if len(returns) == 0:
            return {}
        
        risk_metrics = RiskMetrics(returns)
        metrics = risk_metrics.get_all_metrics()
        
        # Additional metrics
        total_return = (results['portfolio_value'].iloc[-1] / self.initial_capital - 1) * 100
        metrics['total_return'] = total_return
        metrics['num_trades'] = len(self.trades)
        metrics['win_rate'] = self._calculate_win_rate()
        
        return metrics
    
    def _calculate_win_rate(self) -> float:
        """Calculate win rate from trades"""
        if len(self.trades) < 2:
            return 0.0
        
        winning_trades = sum(1 for t in self.trades if t.get('pnl', 0) > 0)
        total_trades_with_pnl = sum(1 for t in self.trades if 'pnl' in t and t['pnl'] != 0)
        
        if total_trades_with_pnl == 0:
            return 0.0
        
        return winning_trades / total_trades_with_pnl

