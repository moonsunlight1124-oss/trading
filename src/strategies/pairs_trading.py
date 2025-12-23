"""Pairs Trading Strategy - Market Neutral Approach"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from scipy import stats
from .base_strategy import BaseStrategy


class PairsTradingStrategy(BaseStrategy):
    """
    Pairs trading strategy using cointegration analysis
    Market-neutral approach: long one asset, short another
    """
    
    def __init__(
        self,
        lookback_period: int = 60,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.5,
        position_size_pct: float = 0.4,
        **kwargs
    ):
        """
        Initialize pairs trading strategy
        
        Args:
            lookback_period: Period for cointegration analysis
            entry_threshold: Z-score threshold for entry
            exit_threshold: Z-score threshold for exit
            position_size_pct: Percentage of capital per pair
        """
        super().__init__(name="PairsTrading", **kwargs)
        self.lookback_period = lookback_period
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.position_size_pct = position_size_pct
        self.hedge_ratio = None
        
    def calculate_cointegration(self, asset1: pd.Series, asset2: pd.Series) -> Tuple[float, float]:
        """
        Calculate hedge ratio and spread using OLS regression
        
        Returns:
            (hedge_ratio, pvalue) from cointegration test
        """
        # Remove NaN values
        valid_idx = ~(asset1.isna() | asset2.isna())
        x = asset1[valid_idx].values
        y = asset2[valid_idx].values
        
        if len(x) < self.lookback_period:
            return None, None
        
        # OLS regression: asset2 = alpha + beta * asset1
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        return slope, p_value
    
    def calculate_spread(self, asset1: pd.Series, asset2: pd.Series, hedge_ratio: float) -> pd.Series:
        """Calculate spread between two assets"""
        spread = asset2 - hedge_ratio * asset1
        return spread
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate pairs trading signals
        
        Args:
            data: DataFrame with columns [asset1_close, asset2_close] or similar
        """
        df = data.copy()
        
        # Assume two price columns
        if 'close' in df.columns:
            if isinstance(df.columns, pd.MultiIndex):
                asset1_col = df.columns[0]
                asset2_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
            else:
                # Single asset - use first difference as proxy
                asset1 = df['close']
                asset2 = asset1.shift(1)
                df['asset1'] = asset1
                df['asset2'] = asset2
        else:
            asset1_col = df.columns[0]
            asset2_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
            df['asset1'] = df[asset1_col]
            df['asset2'] = df[asset2_col]
        
        asset1 = df['asset1']
        asset2 = df['asset2']
        
        # Calculate rolling hedge ratio and spread
        df['hedge_ratio'] = np.nan
        df['spread'] = np.nan
        df['spread_mean'] = np.nan
        df['spread_std'] = np.nan
        df['zscore'] = np.nan
        df['signal'] = 0
        df['position'] = 0
        
        for i in range(self.lookback_period, len(df)):
            window1 = asset1.iloc[i - self.lookback_period:i]
            window2 = asset2.iloc[i - self.lookback_period:i]
            
            hedge_ratio, _ = self.calculate_cointegration(window1, window2)
            if hedge_ratio is not None:
                df.iloc[i, df.columns.get_loc('hedge_ratio')] = hedge_ratio
                
                # Calculate spread
                spread = asset2.iloc[i] - hedge_ratio * asset1.iloc[i]
                df.iloc[i, df.columns.get_loc('spread')] = spread
                
                # Calculate Z-score of spread
                spread_window = df['spread'].iloc[i - self.lookback_period:i]
                spread_mean = spread_window.mean()
                spread_std = spread_window.std()
                
                if spread_std > 0:
                    zscore = (spread - spread_mean) / spread_std
                    df.iloc[i, df.columns.get_loc('spread_mean')] = spread_mean
                    df.iloc[i, df.columns.get_loc('spread_std')] = spread_std
                    df.iloc[i, df.columns.get_loc('zscore')] = zscore
                    
                    # Generate signals
                    if zscore < -self.entry_threshold:
                        # Spread is too low: long asset2, short asset1
                        df.iloc[i, df.columns.get_loc('signal')] = 1
                    elif zscore > self.entry_threshold:
                        # Spread is too high: short asset2, long asset1
                        df.iloc[i, df.columns.get_loc('signal')] = -1
                    elif abs(zscore) < self.exit_threshold:
                        # Close positions
                        df.iloc[i, df.columns.get_loc('signal')] = 0
        
        # Position tracking
        position = 0
        for i in range(len(df)):
            if df.iloc[i]['signal'] != 0:
                position = df.iloc[i]['signal']
            df.iloc[i, df.columns.get_loc('position')] = position
        
        return df[['asset1', 'asset2', 'spread', 'zscore', 'signal', 'position']]
    
    def calculate_position_size(self, signal: Dict, data: pd.DataFrame) -> float:
        """Calculate position sizes for both assets in pair"""
        if signal['signal'] == 0:
            return 0.0
        
        # For pairs trading, we need to return hedge ratio info
        # This is a simplified version - actual implementation would handle both assets
        hedge_ratio = signal.get('hedge_ratio', 1.0)
        price = signal.get('price', data['close'].iloc[-1] if 'close' in data.columns else data.iloc[-1, 0])
        
        position_value = self.capital * self.position_size_pct
        quantity = position_value / price
        
        return abs(quantity) * (1 if signal['signal'] > 0 else -1)

