"""
Example: Backtest multiple trading strategies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import matplotlib.pyplot as plt
from src.strategies import MeanReversionStrategy, MomentumStrategy, HedgeStrategy
from src.backtesting import Backtester, PerformanceAnalyzer
from src.data import DataLoader


def main():
    """Run backtests on multiple strategies"""
    
    # Load data
    print("Loading market data...")
    loader = DataLoader()
    data = loader.load_crypto_data('BTC-USD', '2023-01-01', '2024-12-01')
    data = loader.preprocess_data(data)
    
    print(f"Loaded {len(data)} days of data")
    print(f"Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}\n")
    
    # Initialize strategies
    strategies = [
        MeanReversionStrategy(initial_capital=100000, lookback_period=20, entry_threshold=2.0),
        MomentumStrategy(initial_capital=100000),
        HedgeStrategy(initial_capital=100000)
    ]
    
    results_summary = []
    
    # Backtest each strategy
    for strategy in strategies:
        print(f"\n{'='*60}")
        print(f"Backtesting: {strategy.name}")
        print('='*60)
        
        backtester = Backtester(strategy, initial_capital=100000)
        results = backtester.run(data, price_column='close')
        metrics = backtester.get_performance_metrics(results)
        
        # Print results
        analyzer = PerformanceAnalyzer(results)
        print(analyzer.generate_report(metrics))
        
        # Store summary
        results_summary.append({
            'Strategy': strategy.name,
            'Total Return (%)': metrics.get('total_return', 0),
            'Sharpe Ratio': metrics.get('sharpe_ratio', 0),
            'Max Drawdown (%)': metrics.get('max_drawdown', 0) * 100,
            'Win Rate (%)': metrics.get('win_rate', 0) * 100
        })
        
        # Plot results
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        analyzer.plot_equity_curve(axes[0])
        analyzer.plot_drawdown(axes[1])
        analyzer.plot_returns_distribution(axes[2])
        plt.suptitle(f'{strategy.name} - Performance Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # Save plot
        os.makedirs('results', exist_ok=True)
        plt.savefig(f'results/{strategy.name}_backtest.png', dpi=150, bbox_inches='tight')
        print(f"Saved plot to results/{strategy.name}_backtest.png")
        plt.close()
    
    # Print comparison
    print("\n" + "="*60)
    print("STRATEGY COMPARISON")
    print("="*60)
    summary_df = pd.DataFrame(results_summary)
    print(summary_df.to_string(index=False))
    
    # Save summary
    summary_df.to_csv('results/strategy_comparison.csv', index=False)
    print("\nSaved comparison to results/strategy_comparison.csv")


if __name__ == '__main__':
    main()

