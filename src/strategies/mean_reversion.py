"""Mean Reversion Trading Strategy using Statistical Arbitrage"""

import pandas as pd
import numpy as np
from typing import Dict
from .base_strategy import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """
    Mean reversion strategy using Z-score and Bollinger Bands
    Buys when price is below mean (oversold), sells when above (overbought)
    """
    
    def __init__(
        self,
        lookback_period: int = 20,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.5,
        position_size_pct: float = 0.25,
        **kwargs
    ):
        """
        Initialize mean reversion strategy
        
        Args:
            lookback_period: Period for moving average and std calculation
            entry_threshold: Z-score threshold for entry (abs value)
            exit_threshold: Z-score threshold for exit (abs value)
            position_size_pct: Percentage of capital to use per trade
        """
        super().__init__(name="MeanReversion", **kwargs)
        self.lookback_period = lookback_period
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.position_size_pct = position_size_pct
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate mean reversion signals"""
        df = data.copy()
        symbol = df.columns[0] if isinstance(df.columns, pd.MultiIndex) else 'close'
        close = df['close'] if 'close' in df.columns else df.iloc[:, 0]
        
        # Calculate moving average and standard deviation
        df['ma'] = close.rolling(window=self.lookback_period).mean()
        df['std'] = close.rolling(window=self.lookback_period).std()
        
        # Calculate Z-score
        df['zscore'] = (close - df['ma']) / df['std']
        
        # Generate signals
        df['signal'] = 0
        df['position'] = 0
        
        # Entry signals
        df.loc[df['zscore'] < -self.entry_threshold, 'signal'] = 1  # Buy
        df.loc[df['zscore'] > self.entry_threshold, 'signal'] = -1  # Sell
        
        # Exit signals
        df.loc[
            (df['zscore'] > -self.exit_threshold) & 
            (df['zscore'] < self.exit_threshold) &
            (df['signal'] != 0), 
            'signal'
        ] = 0
        
        # Position tracking
        position = 0
        for i in range(len(df)):
            if df.iloc[i]['signal'] != 0:
                position = df.iloc[i]['signal']
            df.iloc[i, df.columns.get_loc('position')] = position
        
        return df[['close', 'ma', 'std', 'zscore', 'signal', 'position']]
    
    def calculate_position_size(self, signal: Dict, data: pd.DataFrame) -> float:
        """Calculate position size based on capital allocation"""
        if signal['signal'] == 0:
            return 0.0
        
        price = signal.get('price', data['close'].iloc[-1])
        position_value = self.capital * self.position_size_pct
        quantity = position_value / price
        
        return abs(quantity) * (1 if signal['signal'] > 0 else -1)

