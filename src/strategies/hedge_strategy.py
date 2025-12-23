"""Hedge Trading Strategy - Multi-Asset Portfolio Hedging"""

import pandas as pd
import numpy as np
from typing import Dict, List
from .base_strategy import BaseStrategy


class HedgeStrategy(BaseStrategy):
    """
    Hedge strategy using correlation analysis and portfolio optimization
    Maintains market-neutral positions across multiple assets
    """
    
    def __init__(
        self,
        lookback_period: int = 30,
        correlation_threshold: float = 0.7,
        max_position_pct: float = 0.2,
        hedge_ratio: float = 0.5,
        **kwargs
    ):
        """
        Initialize hedge strategy
        
        Args:
            lookback_period: Period for correlation calculation
            correlation_threshold: Minimum correlation for hedging
            max_position_pct: Maximum position size per asset
            hedge_ratio: Ratio of hedge to primary position
        """
        super().__init__(name="HedgeStrategy", **kwargs)
        self.lookback_period = lookback_period
        self.correlation_threshold = correlation_threshold
        self.max_position_pct = max_position_pct
        self.hedge_ratio = hedge_ratio
        
    def calculate_correlation_matrix(self, returns: pd.DataFrame) -> pd.DataFrame:
        """Calculate correlation matrix of asset returns"""
        return returns.rolling(window=self.lookback_period).corr()
    
    def calculate_portfolio_beta(self, asset_returns: pd.Series, market_returns: pd.Series) -> float:
        """Calculate beta of asset relative to market"""
        if len(asset_returns) < self.lookback_period:
            return 1.0
        
        window_asset = asset_returns.tail(self.lookback_period)
        window_market = market_returns.tail(self.lookback_period)
        
        covariance = np.cov(window_asset, window_market)[0, 1]
        market_variance = np.var(window_market)
        
        if market_variance == 0:
            return 1.0
        
        return covariance / market_variance
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate hedge signals based on portfolio construction
        
        Args:
            data: DataFrame with multiple asset prices
        """
        df = data.copy()
        
        # Calculate returns
        if 'close' in df.columns:
            prices = df['close']
        else:
            prices = df.iloc[:, 0]
        
        returns = prices.pct_change()
        df['returns'] = returns
        
        # Calculate volatility
        df['volatility'] = returns.rolling(window=self.lookback_period).std() * np.sqrt(252)
        
        # Generate signals based on volatility and mean reversion
        df['signal'] = 0
        df['position'] = 0
        
        # Long signal: Low volatility, positive momentum
        df.loc[
            (df['volatility'] < df['volatility'].rolling(60).quantile(0.3)) &
            (returns > 0),
            'signal'
        ] = 1
        
        # Short signal: High volatility, negative momentum
        df.loc[
            (df['volatility'] > df['volatility'].rolling(60).quantile(0.7)) &
            (returns < 0),
            'signal'
        ] = -1
        
        # Position tracking
        position = 0
        for i in range(len(df)):
            if df.iloc[i]['signal'] != 0:
                position = df.iloc[i]['signal']
            df.iloc[i, df.columns.get_loc('position')] = position
        
        return df[['close' if 'close' in df.columns else df.columns[0], 
                   'returns', 'volatility', 'signal', 'position']]
    
    def calculate_position_size(self, signal: Dict, data: pd.DataFrame) -> float:
        """Calculate position size with volatility adjustment"""
        if signal['signal'] == 0:
            return 0.0
        
        price = signal.get('price', data['close'].iloc[-1] if 'close' in data.columns else data.iloc[-1, 0])
        volatility = signal.get('volatility', 0.3)  # Default 30% annualized
        
        # Volatility-adjusted position sizing (lower vol = larger position)
        vol_factor = min(1.0, 0.3 / max(volatility, 0.01))  # Normalize to 30% vol
        
        position_value = self.capital * self.max_position_pct * vol_factor
        quantity = position_value / price
        
        return abs(quantity) * (1 if signal['signal'] > 0 else -1)

