"""Technical indicator calculations"""

import pandas as pd
import numpy as np


def calculate_indicators(data: pd.DataFrame, close_col: str = 'close') -> pd.DataFrame:
    """
    Calculate common technical indicators
    
    Args:
        data: DataFrame with price data
        close_col: Name of close price column
        
    Returns:
        DataFrame with added indicator columns
    """
    df = data.copy()
    close = df[close_col]
    
    # Moving averages
    df['sma_20'] = close.rolling(20).mean()
    df['sma_50'] = close.rolling(50).mean()
    df['ema_12'] = close.ewm(span=12, adjust=False).mean()
    df['ema_26'] = close.ewm(span=26, adjust=False).mean()
    
    # Bollinger Bands
    df['bb_middle'] = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    df['bb_upper'] = df['bb_middle'] + 2 * bb_std
    df['bb_lower'] = df['bb_middle'] - 2 * bb_std
    
    # RSI
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # ATR (Average True Range)
    high = df.get('high', close)
    low = df.get('low', close)
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['atr'] = tr.rolling(14).mean()
    
    return df

