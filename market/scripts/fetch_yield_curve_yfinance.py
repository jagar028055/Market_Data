#!/usr/bin/env python3
"""
イールドカーブ取得スクリプト（yfinance版）

yfinanceを使って各国の国債利回りを取得し、イールドカープを可視化します。

対象国:
- 日本
- 米国
- ドイツ
- フランス
- イギリス (United Kingdom)
- オーストラリア

インストール:
    pip install yfinance pandas matplotlib numpy
"""

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import os
import numpy as np

# リポジトリルートへのパスを計算（スクリプトがどこから実行されても正しく動作するように）
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(os.path.dirname(script_dir))

# 日本語フォント設定
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 各国の国債ティッカー設定
# Yahoo Financeのシンボルを使用
BONDS_CONFIG = {
    'japan': {
        'name': 'Japan',
        'name_ja': '日本',
        'tickers': [
            {'symbol': '^JP6MEUR', 'name': 'Japan 2Y', 'period': 2, 'alternatives': ['JGB2Y=F']},
            {'symbol': '^JP5MEUR', 'name': 'Japan 5Y', 'period': 5, 'alternatives': ['JGB5Y=F']},
            {'symbol': '^JP10MEUR', 'name': 'Japan 10Y', 'period': 10, 'alternatives': ['JGB=F', 'JGB10Y=F']},
            {'symbol': '^JP20MEUR', 'name': 'Japan 20Y', 'period': 20, 'alternatives': ['JGB20Y=F']},
            {'symbol': '^JP30MEUR', 'name': 'Japan 30Y', 'period': 30, 'alternatives': ['JGB30Y=F']},
        ]
    },
    'united states': {
        'name': 'United States',
        'name_ja': '米国',
        'tickers': [
            {'symbol': '^FVX', 'name': 'US 2Y', 'period': 2, 'alternatives': ['US2Y=F']},
            {'symbol': '^FVXR', 'name': 'US 5Y', 'period': 5, 'alternatives': ['US5Y=F']},
            {'symbol': '^TNX', 'name': 'US 10Y', 'period': 10, 'alternatives': ['US10Y=F']},
            {'symbol': '^TYX', 'name': 'US 30Y', 'period': 30, 'alternatives': ['US30Y=F']},
        ]
    },
    'germany': {
        'name': 'Germany',
        'name_ja': 'ドイツ',
        'tickers': [
            {'symbol': 'TMBMKDE-02Y', 'name': 'Germany 2Y', 'period': 2, 'alternatives': ['BUND2Y=F']},
            {'symbol': 'TMBMKDE-05Y', 'name': 'Germany 5Y', 'period': 5, 'alternatives': ['BUND5Y=F']},
            {'symbol': 'TMBMKDE-10Y', 'name': 'Germany 10Y', 'period': 10, 'alternatives': ['BUND10Y=F']},
        ]
    },
    'france': {
        'name': 'France',
        'name_ja': 'フランス',
        'tickers': [
            {'symbol': 'TMBMKFR-02Y', 'name': 'France 2Y', 'period': 2, 'alternatives': ['OAT2Y=F']},
            {'symbol': 'TMBMKFR-05Y', 'name': 'France 5Y', 'period': 5, 'alternatives': ['OAT5Y=F']},
            {'symbol': 'TMBMKFR-10Y', 'name': 'France 10Y', 'period': 10, 'alternatives': ['OAT10Y=F']},
        ]
    },
    'united kingdom': {
        'name': 'United Kingdom',
        'name_ja': 'イギリス',
        'tickers': [
            {'symbol': 'TMBMKGB-02Y', 'name': 'UK 2Y', 'period': 2, 'alternatives': ['GILT2Y=F']},
            {'symbol': 'TMBMKGB-05Y', 'name': 'UK 5Y', 'period': 5, 'alternatives': ['GILT5Y=F']},
            {'symbol': 'TMBMKGB-10Y', 'name': 'UK 10Y', 'period': 10, 'alternatives': ['GILT10Y=F']},
        ]
    },
    'australia': {
        'name': 'Australia',
        'name_ja': 'オーストラリア',
        'tickers': [
            {'symbol': 'TMBMKAU-02Y', 'name': 'Australia 2Y', 'period': 2, 'alternatives': ['AU2Y=F']},
            {'symbol': 'TMBMKAU-05Y', 'name': 'Australia 5Y', 'period': 5, 'alternatives': ['AU5Y=F']},
            {'symbol': 'TMBMKAU-10Y', 'name': 'Australia 10Y', 'period': 10, 'alternatives': ['AU10Y=F']},
        ]
    },
}


class YieldCurveFetcher:
    """イールドカーブ取得クラス"""

    def __init__(self):
        self.results = {}

    def fetch_bond_yield(self, ticker_config: dict) -> dict:
        """
        個別の国債利回りを取得

        Args:
            ticker_config: ティッカー設定辞書（symbol, name, period, alternativesを含む）

        Returns:
            dict: 利回りデータ
        """
        symbol = ticker_config['symbol']
        name = ticker_config['name']
        period = ticker_config['period']
        alternatives = ticker_config.get('alternatives', [])

        # 試行するシンボルのリスト（メインのシンボルを優先）
        all_symbols = [symbol] + alternatives

        for idx, current_symbol in enumerate(all_symbols):
            try:
                if idx == 0:
                    print(f"  Fetching {name} ({current_symbol})...")
                else:
                    print(f"  Trying alternative: {name} ({current_symbol})...")

                # 過去7日間のデータを取得
                end_date = datetime.now()
                start_date = end_date - timedelta(days=7)

                ticker = yf.Ticker(current_symbol)
                hist = ticker.history(start=start_date, end=end_date)

                if hist is not None and not hist.empty:
                    # 最新の終値
                    latest = hist.iloc[-1]
                    latest_yield = latest['Close']

                    # 前日比
                    if len(hist) >= 2:
                        previous = hist.iloc[-2]
                        previous_yield = previous['Close']
                        change = latest_yield - previous_yield
                        change_pct = (change / previous_yield) * 100 if previous_yield != 0 else 0
                    else:
                        previous_yield = None
                        change = None
                        change_pct = None

                    result = {
                        'symbol': current_symbol,
                        'name': name,
                        'period': period,
                        'yield': latest_yield,
                        'previous_yield': previous_yield,
                        'change': change,
                        'change_pct': change_pct,
                        'date': latest.name.strftime('%Y-%m-%d') if hasattr(latest.name, 'strftime') else str(latest.name),
                    }
                    print(f"  Success: {name} = {result['yield']:.2f}%")
                    return result
                else:
                    print(f"  No data for {name} ({current_symbol})")
                    continue

            except Exception as e:
                print(f"  Error fetching {name} ({current_symbol}): {e}")
                continue

        print(f"  Failed to fetch {name} after trying all symbols")
        return None

    def fetch_country_yield_curve(self, country: str) -> dict:
        """
        国のイールドカーブ全体を取得

        Args:
            country: 国コード

        Returns:
            dict: イールドカーブデータ
        """
        if country not in BONDS_CONFIG:
            print(f"Unknown country: {country}")
            return None

        config = BONDS_CONFIG[country]
        print(f"\n{'=' * 60}")
        print(f"Fetching yield curve for {config['name_ja']} ({config['name']})")
        print(f"{'=' * 60}")

        yields_data = []

        for ticker_config in config['tickers']:
            data = self.fetch_bond_yield(ticker_config)
            if data:
                yields_data.append(data)

        if yields_data:
            # 期間でソート
            yields_data.sort(key=lambda x: x['period'])

            result = {
                'country': country,
                'country_name': config['name'],
                'country_name_ja': config['name_ja'],
                'fetch_date': datetime.now().isoformat(),
                'bonds': yields_data
            }

            self.results[country] = result
            return result

        print(f"Warning: No bond data fetched for {country}")
        return None

    def fetch_all_countries(self) -> dict:
        """全対象国のイールドカーブを取得"""
        for country in BONDS_CONFIG.keys():
            self.fetch_country_yield_curve(country)

        return self.results

    def plot_yield_curves(self, save_path: str = None):
        """全国のイールドカーブをプロット"""
        if not self.results:
            print("No data to plot")
            return

        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'Government Bond Yield Curves\n{datetime.now().strftime("%Y-%m-%d")}',
                     fontsize=16, fontweight='bold')

        countries = list(BONDS_CONFIG.keys())
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

        for idx, country in enumerate(countries):
            ax = axes[idx // 3, idx % 3]

            if country not in self.results:
                ax.text(0.5, 0.5, 'No Data', ha='center', va='center', transform=ax.transAxes)
                ax.set_title(BONDS_CONFIG[country]['name_ja'])
                continue

            data = self.results[country]
            periods = [bond['period'] for bond in data['bonds']]
            yields = [bond['yield'] for bond in data['bonds']]

            # イールドカーブ
            ax.plot(periods, yields, marker='o', linewidth=2, markersize=8, color=colors[idx])
            ax.fill_between(periods, 0, yields, alpha=0.2, color=colors[idx])

            # 値を表示
            for p, y in zip(periods, yields):
                ax.text(p, y, f'{y:.2f}%', ha='center', va='bottom', fontsize=9)

            ax.set_xlabel('Maturity (Years)', fontsize=11)
            ax.set_ylabel('Yield (%)', fontsize=11)
            ax.set_title(f"{data['country_name_ja']} ({data['country_name']})", fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.set_xlim(0, max(periods) + 2)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved yield curve plot: {save_path}")
        else:
            output_dir = os.path.join(repo_root, 'market/data/yield_curves/images')
            os.makedirs(output_dir, exist_ok=True)
            save_path = os.path.join(output_dir, 'yield_curves.png')
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved yield curve plot: {save_path}")

        plt.close()

    def plot_change_histogram(self, save_path: str = None):
        """前日比のヒストグラムをプロット"""
        if not self.results:
            print("No data to plot")
            return

        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'Yield Change (Day-over-Day)\n{datetime.now().strftime("%Y-%m-%d")}',
                     fontsize=16, fontweight='bold')

        countries = list(BONDS_CONFIG.keys())

        for idx, country in enumerate(countries):
            ax = axes[idx // 3, idx % 3]

            if country not in self.results:
                ax.text(0.5, 0.5, 'No Data', ha='center', va='center', transform=ax.transAxes)
                ax.set_title(BONDS_CONFIG[country]['name_ja'])
                continue

            data = self.results[country]

            # 前日比データを抽出
            changes = []
            labels = []
            colors_bar = []

            for bond in data['bonds']:
                if bond.get('change') is not None:
                    changes.append(bond['change'])
                    labels.append(f"{bond['period']}Y")
                    colors_bar.append('green' if bond['change'] >= 0 else 'red')

            if changes:
                bars = ax.bar(labels, changes, color=colors_bar, alpha=0.7, edgecolor='black')

                # 値を表示
                for bar, change in zip(bars, changes):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2., height,
                            f'{change:+.2f}%',
                            ha='center', va='bottom' if height >= 0 else 'top',
                            fontsize=9, fontweight='bold')

                ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
                ax.set_xlabel('Maturity', fontsize=11)
                ax.set_ylabel('Change (%)', fontsize=11)
                ax.set_title(f"{data['country_name_ja']} ({data['country_name']})", fontsize=12, fontweight='bold')
                ax.grid(True, alpha=0.3, axis='y')

                # y軸の範囲を設定
                y_max = max(abs(c) for c in changes) if changes else 0.1
                ax.set_ylim(-y_max * 1.5, y_max * 1.5)
            else:
                ax.text(0.5, 0.5, 'No change data', ha='center', va='center', transform=ax.transAxes)
                ax.set_title(f"{data['country_name_ja']} ({data['country_name']})", fontsize=12, fontweight='bold')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved change histogram: {save_path}")
        else:
            output_dir = os.path.join(repo_root, 'market/data/yield_curves/images')
            os.makedirs(output_dir, exist_ok=True)
            save_path = os.path.join(output_dir, 'yield_changes.png')
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved change histogram: {save_path}")

        plt.close()

    def save_json(self, output_dir: str = None):
        """JSONで保存"""
        if not self.results:
            print("No data to save")
            return

        if output_dir is None:
            output_dir = os.path.join(repo_root, 'market/data/yield_curves/json')

        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # タイムスタンプ付きファイル
        timestamp_file = os.path.join(output_dir, f"yield_curve_{timestamp}.json")
        with open(timestamp_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"Saved: {timestamp_file}")

        # 最新版ファイル
        latest_file = os.path.join(output_dir, "yield_curve_latest.json")
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"Saved: {latest_file}")

    def print_summary(self):
        """結果のサマリーを表示"""
        if not self.results:
            print("No data available")
            return

        print("\n" + "=" * 80)
        print("YIELD CURVE SUMMARY")
        print("=" * 80)
        print(f"Fetch Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        for country, data in self.results.items():
            print(f"\n{data['country_name_ja']} ({data['country_name']})")
            print("-" * 60)
            print(f"{'Maturity':<12} {'Yield':<12} {'Change':<12} {'Change %':<12}")
            print("-" * 60)

            for bond in data['bonds']:
                yield_str = f"{bond['yield']:.2f}%" if bond.get('yield') is not None else "N/A"
                change_str = f"{bond['change']:+.2f}%" if bond.get('change') is not None else "N/A"
                change_pct_str = f"{bond['change_pct']:+.2f}%" if bond.get('change_pct') is not None else "N/A"
                print(f"{bond['period']}Y{'':<8} {yield_str:<12} {change_str:<12} {change_pct_str:<12}")

        print("\n" + "=" * 80)


def main():
    """メイン処理"""
    print("=" * 80)
    print("イールドカーブ取得（yfinance版）")
    print("=" * 80)
    print()

    # yfinanceのバージョン確認
    try:
        import yfinance
        print(f"yfinance version: {yfinance.__version__}")
    except ImportError:
        print("yfinance not installed!")
        print("Install with: pip install yfinance pandas matplotlib numpy")
        return

    print()

    # フェッチャーを作成
    fetcher = YieldCurveFetcher()

    # 全国のデータを取得
    fetcher.fetch_all_countries()

    # サマリーを表示
    fetcher.print_summary()

    # グラフを保存（repo_root を使用）
    fetcher.plot_yield_curves()
    fetcher.plot_change_histogram()

    # JSONを保存
    fetcher.save_json()

    print("\nDone!")


if __name__ == "__main__":
    main()
