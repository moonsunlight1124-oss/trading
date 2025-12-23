"""
Example: Portfolio optimization for multiple cryptocurrencies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.risk_management import PortfolioOptimizer
from src.data import DataLoader


def main():
    """Demonstrate portfolio optimization"""
    
    print("Portfolio Optimization Example")
    print("="*60)
    
    # Load multiple assets
    loader = DataLoader()
    symbols = ['BTC-USD', 'ETH-USD']  # Can add more
    
    print(f"\nLoading data for {len(symbols)} assets...")
    data = loader.load_multiple_assets(symbols, '2023-01-01', '2024-12-01')
    
    # Calculate returns
    returns_list = []
    for symbol in symbols:
        close_col = (symbol, 'close') if isinstance(data.columns, pd.MultiIndex) else 'close'
        if close_col in data.columns:
            returns_list.append(data[close_col].pct_change().dropna())
    
    returns_df = pd.concat(returns_list, axis=1)
    returns_df.columns = symbols
    returns_df = returns_df.dropna()
    
    print(f"Calculated returns for {len(returns_df)} periods")
    print(f"\nAverage Returns:")
    print(returns_df.mean() * 252 * 100)  # Annualized
    print(f"\nVolatilities:")
    print(returns_df.std() * np.sqrt(252) * 100)  # Annualized
    print(f"\nCorrelation Matrix:")
    print(returns_df.corr())
    
    # Optimize portfolio
    optimizer = PortfolioOptimizer(risk_free_rate=0.02)
    
    print("\n" + "="*60)
    print("MAXIMUM SHARPE RATIO PORTFOLIO")
    print("="*60)
    max_sharpe = optimizer.optimize_max_sharpe(returns_df)
    print(f"\nOptimal Weights:")
    for asset, weight in max_sharpe['weights'].items():
        print(f"  {asset}: {weight*100:.2f}%")
    print(f"\nExpected Return: {max_sharpe['expected_return']*100:.2f}%")
    print(f"Volatility: {max_sharpe['volatility']*100:.2f}%")
    print(f"Sharpe Ratio: {max_sharpe['sharpe_ratio']:.2f}")
    
    print("\n" + "="*60)
    print("MINIMUM VOLATILITY PORTFOLIO")
    print("="*60)
    min_vol = optimizer.optimize_min_volatility(returns_df)
    print(f"\nOptimal Weights:")
    for asset, weight in min_vol['weights'].items():
        print(f"  {asset}: {weight*100:.2f}%")
    print(f"\nExpected Return: {min_vol['expected_return']*100:.2f}%")
    print(f"Volatility: {min_vol['volatility']*100:.2f}%")
    
    print("\n" + "="*60)
    print("RISK PARITY PORTFOLIO")
    print("="*60)
    risk_parity = optimizer.risk_parity_weights(returns_df)
    print(f"\nWeights:")
    for asset, weight in risk_parity.items():
        print(f"  {asset}: {weight*100:.2f}%")
    
    # Plot efficient frontier (simplified)
    print("\nGenerating efficient frontier plot...")
    
    # Generate random portfolios for visualization
    n_portfolios = 1000
    results = []
    
    for _ in range(n_portfolios):
        weights = np.random.random(len(symbols))
        weights /= np.sum(weights)
        
        portfolio_return, portfolio_vol = optimizer.portfolio_performance(
            weights,
            optimizer.calculate_expected_returns(returns_df).values,
            optimizer.calculate_covariance_matrix(returns_df).values
        )
        sharpe = (portfolio_return - 0.02) / portfolio_vol
        
        results.append({
            'return': portfolio_return,
            'volatility': portfolio_vol,
            'sharpe': sharpe,
            'weights': weights
        })
    
    results_df = pd.DataFrame(results)
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 8))
    scatter = ax.scatter(
        results_df['volatility'] * 100,
        results_df['return'] * 100,
        c=results_df['sharpe'],
        cmap='viridis',
        alpha=0.6,
        s=20
    )
    
    # Mark optimal portfolios
    ax.scatter(max_sharpe['volatility']*100, max_sharpe['expected_return']*100,
              marker='*', s=500, color='red', label='Max Sharpe', zorder=5)
    ax.scatter(min_vol['volatility']*100, min_vol['expected_return']*100,
              marker='*', s=500, color='blue', label='Min Volatility', zorder=5)
    
    plt.colorbar(scatter, label='Sharpe Ratio')
    ax.set_xlabel('Volatility (%)', fontsize=12)
    ax.set_ylabel('Expected Return (%)', fontsize=12)
    ax.set_title('Efficient Frontier', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    os.makedirs('results', exist_ok=True)
    plt.savefig('results/efficient_frontier.png', dpi=150, bbox_inches='tight')
    print("Saved plot to results/efficient_frontier.png")
    plt.close()


if __name__ == '__main__':
    main()

