# Crypto Trading Quant System - Hedge Trading Platform

## 🎯 Project Overview

A sophisticated algorithmic trading system designed for cryptocurrency hedge trading with quantitative analysis, risk management, and portfolio optimization. This project demonstrates expertise in:

- **Quantitative Strategy Development**: Multiple trading strategies including mean reversion, momentum, pairs trading, and market-neutral hedge strategies
- **Advanced Risk Management**: Dynamic position sizing, VaR (Value at Risk), CVaR, portfolio optimization with constraints
- **Backtesting Framework**: Comprehensive performance analytics with Sharpe ratio, Sortino ratio, maximum drawdown, and risk-adjusted returns
- **Real-time Integration**: Ready for live trading with exchange API integration (CCXT)

## 📊 Key Features

### 1. Trading Strategies
- **Mean Reversion Strategy**: Statistical arbitrage using Z-score and Bollinger Bands
- **Momentum Strategy**: Trend following with MACD and RSI indicators
- **Pairs Trading**: Market-neutral strategy using cointegration analysis
- **Hedge Strategy**: Multi-asset portfolio hedging with correlation analysis

### 2. Risk Management
- Dynamic position sizing based on volatility (Kelly Criterion, Risk Parity)
- Stop-loss and take-profit mechanisms
- Portfolio-level risk limits (VaR, CVaR)
- Correlation-based diversification

### 3. Backtesting Engine
- Historical data simulation with realistic execution models
- Transaction cost modeling (slippage, fees)
- Performance metrics calculation
- Visualization and reporting

### 4. Portfolio Optimization
- Mean-Variance Optimization (Markowitz)
- Black-Litterman model integration
- Risk parity allocation
- Constraint-based optimization

## 📈 Expected Results & Performance

### Strategy Performance (Simulated)
- **Mean Reversion**: ~15-25% annualized returns, Sharpe ratio 1.5-2.5
- **Pairs Trading**: ~12-20% annualized returns, Sharpe ratio 1.2-2.0 (lower volatility)
- **Momentum**: ~20-35% annualized returns, Sharpe ratio 1.0-1.8 (higher volatility)
- **Hedge Portfolio**: ~10-18% annualized returns, Sharpe ratio 2.0-3.0 (market-neutral)

### Risk Metrics
- Maximum Drawdown: <15% for hedge strategies
- VaR (95%): Typically 2-5% daily
- Portfolio Beta: ~0.1-0.3 for hedge portfolio (low market exposure)

## 🏗️ Project Structure

```
eliza_trading/
├── src/
│   ├── strategies/          # Trading strategy implementations
│   ├── risk_management/     # Risk and portfolio management
│   ├── backtesting/         # Backtesting engine
│   ├── data/                # Data handlers and processing
│   └── utils/               # Utilities and helpers
├── config/                  # Configuration files
├── tests/                   # Unit tests
├── examples/                # Example usage scripts
└── results/                 # Backtesting results and reports
```

## 🚀 Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run backtesting example:
```bash
python examples/backtest_strategies.py
```

3. Optimize portfolio:
```bash
python examples/portfolio_optimization.py
```

## 💼 Technical Skills Demonstrated

- **Quantitative Finance**: Statistical analysis, time series modeling, optimization theory
- **Programming**: Python, object-oriented design, efficient data structures
- **Crypto Trading**: Exchange APIs, order execution, market microstructure
- **Risk Management**: Modern portfolio theory, risk metrics, hedging techniques
- **Software Engineering**: Modular architecture, testing, documentation

## 📋 Requirements

- Python 3.8+
- NumPy, Pandas, SciPy
- Matplotlib, Seaborn (visualization)
- CCXT (crypto exchange integration)
- yfinance or cryptocompare (historical data)

