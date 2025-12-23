"""Momentum Trading Strategy using Technical Indicators"""

import pandas as pd
import numpy as np
from typing import Dict
from .base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """
    Momentum strategy using MACD and RSI indicators
    Buys on bullish momentum, sells on bearish momentum
    """
    
    def __init__(
        self,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        rsi_period: int = 14,
        rsi_oversold: float = 30,
        rsi_overbought: float = 70,
        position_size_pct: float = 0.3,
        **kwargs
    ):
        """
        Initialize momentum strategy
        
        Args:
            macd_fast: Fast EMA period for MACD
            macd_slow: Slow EMA period for MACD
            macd_signal: Signal line period for MACD
            rsi_period: RSI calculation period
            rsi_oversold: RSI oversold threshold
            rsi_overbought: RSI overbought threshold
            position_size_pct: Percentage of capital per trade
        """
        super().__init__(name="Momentum", **kwargs)
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.position_size_pct = position_size_pct
        
    def calculate_macd(self, prices: pd.Series) -> pd.DataFrame:
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=self.macd_fast, adjust=False).mean()
        ema_slow = prices.ewm(span=self.macd_slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=self.macd_signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return pd.DataFrame({
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        })
    
    def calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate momentum signals"""
        df = data.copy()
        close = df['close'] if 'close' in df.columns else df.iloc[:, 0]
        
        # Calculate indicators
        macd_data = self.calculate_macd(close)
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['signal']
        df['macd_histogram'] = macd_data['histogram']
        df['rsi'] = self.calculate_rsi(close)
        
        # Generate signals
        df['signal'] = 0
        df['position'] = 0
        
        # Bullish signals: MACD crossover above signal AND RSI not overbought
        df.loc[
            (df['macd'] > df['macd_signal']) & 
            (df['macd_histogram'] > 0) &
            (df['rsi'] > 50) & 
            (df['rsi'] < self.rsi_overbought),
            'signal'
        ] = 1
        
        # Bearish signals: MACD crossover below signal AND RSI not oversold
        df.loc[
            (df['macd'] < df['macd_signal']) & 
            (df['macd_histogram'] < 0) &
            (df['rsi'] < 50) & 
            (df['rsi'] > self.rsi_oversold),
            'signal'
        ] = -1
        
        # Position tracking
        position = 0
        for i in range(len(df)):
            if df.iloc[i]['signal'] != 0:
                position = df.iloc[i]['signal']
            df.iloc[i, df.columns.get_loc('position')] = position
        
        return df[['close', 'macd', 'macd_signal', 'rsi', 'signal', 'position']]
    
    def calculate_position_size(self, signal: Dict, data: pd.DataFrame) -> float:
        """Calculate position size"""
        if signal['signal'] == 0:
            return 0.0
        
        price = signal.get('price', data['close'].iloc[-1])
        position_value = self.capital * self.position_size_pct
        
        # Adjust size based on RSI strength
        rsi = signal.get('rsi', 50)
        if signal['signal'] > 0:
            rsi_factor = (rsi - 50) / 50  # 0 to 1
        else:
            rsi_factor = (50 - rsi) / 50  # 0 to 1
        
        position_value *= (0.5 + 0.5 * rsi_factor)  # 50-100% based on strength
        quantity = position_value / price
        
        return abs(quantity) * (1 if signal['signal'] > 0 else -1)

