#!/usr/bin/env python3
"""
イールドカーブ取得スクリプト（investpy版）

investpyを使って各国の国債利回りを取得し、イールドカープを可視化します。

対象国:
- 日本
- 米国
- ドイツ
- フランス
- イギリス (United Kingdom)
- オーストラリア

インストール:
    pip install investpy pandas matplotlib numpy

注意:
- investpyは2020年からメンテナンス停止
- Python 3.9以下を推奨
- Investing.comの構造変更で動作しない可能性があります
"""

import investpy as inv
import pandas as pd
import os
import sys

# ChromeとChromeDriverの設定（GitHub Actions環境用）
# ヘッドレスChromeの設定
os.environ['CHROME_BIN'] = '/usr/bin/chromium-browser'
os.environ['CHROMEDRIVER_PATH'] = '/usr/bin/chromedriver'

# investpyがseleniumを使用する際のオプションを設定
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions

    # Chromeオプションの設定
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # chromedriverのパスを設定
    chrome_options.binary_location = '/usr/bin/chromium-browser'

    print("Chrome options configured for headless mode")
except ImportError:
    print("Warning: selenium not installed, falling back to default investpy behavior")
    chrome_options = None
import matplotlib
# ヘッドレス環境（GitHub Actions）で動作させるためにAggバックエンドを使用
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import json
import os
import numpy as np

# リポジトリルートへのパスを計算（スクリプトがどこから実行されても正しく動作するように）
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(os.path.dirname(script_dir))

# 日本語フォント設定（matplotlibで日本語を表示するため）
# Termux環境ではフォントが限られているため、英語で表示することを推奨
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 各国の国債設定
# investpyのbonds.get_bond_historical_data()で使用する国債名
# 注: Investing.comのサイト構造変更により、bond名が変更されている可能性があります
# 複数の候補名を試すように設計されています
BONDS_CONFIG = {
    'japan': {
        'name': 'Japan',
        'name_ja': '日本',
        'bonds': [
            {'name': 'Japan 2Y', 'period': 2, 'alternatives': ['JGB 2Y', 'Japan 2 Year', 'Japan 2Y Bond', 'JGB2Y']},
            {'name': 'Japan 5Y', 'period': 5, 'alternatives': ['JGB 5Y', 'Japan 5 Year', 'Japan 5Y Bond', 'JGB5Y']},
            {'name': 'Japan 10Y', 'period': 10, 'alternatives': ['JGB 10Y', 'Japan 10 Year', 'Japan 10Y Bond', 'JGB10Y']},
            {'name': 'Japan 20Y', 'period': 20, 'alternatives': ['JGB 20Y', 'Japan 20 Year', 'Japan 20Y Bond', 'JGB20Y']},
            {'name': 'Japan 30Y', 'period': 30, 'alternatives': ['JGB 30Y', 'Japan 30 Year', 'Japan 30Y Bond', 'JGB30Y']},
        ]
    },
    'united states': {
        'name': 'United States',
        'name_ja': '米国',
        'bonds': [
            {'name': 'U.S. 2Y', 'period': 2, 'alternatives': ['USA 2Y', 'United States 2Y', 'US 2Y', 'Treasury 2Y', 'US2Y']},
            {'name': 'U.S. 5Y', 'period': 5, 'alternatives': ['USA 5Y', 'United States 5Y', 'US 5Y', 'Treasury 5Y', 'US5Y']},
            {'name': 'U.S. 10Y', 'period': 10, 'alternatives': ['USA 10Y', 'United States 10Y', 'US 10Y', 'Treasury 10Y', 'US10Y']},
            {'name': 'U.S. 30Y', 'period': 30, 'alternatives': ['USA 30Y', 'United States 30Y', 'US 30Y', 'Treasury 30Y', 'US30Y']},
        ]
    },
    'germany': {
        'name': 'Germany',
        'name_ja': 'ドイツ',
        'bonds': [
            {'name': 'Germany 2Y', 'period': 2, 'alternatives': ['Bund 2Y', 'German 2Y', 'Germany 2Y Bond', 'DBR2Y']},
            {'name': 'Germany 5Y', 'period': 5, 'alternatives': ['Bund 5Y', 'German 5Y', 'Germany 5Y Bond', 'DBR5Y']},
            {'name': 'Germany 10Y', 'period': 10, 'alternatives': ['Bund 10Y', 'German 10Y', 'Germany 10Y Bond', 'DBR10Y']},
            {'name': 'Germany 30Y', 'period': 30, 'alternatives': ['Bund 30Y', 'German 30Y', 'Germany 30Y Bond', 'DBR30Y']},
        ]
    },
    'france': {
        'name': 'France',
        'name_ja': 'フランス',
        'bonds': [
            {'name': 'France 2Y', 'period': 2, 'alternatives': ['OAT 2Y', 'French 2Y', 'France 2Y Bond', 'OAT2Y']},
            {'name': 'France 5Y', 'period': 5, 'alternatives': ['OAT 5Y', 'French 5Y', 'France 5Y Bond', 'OAT5Y']},
            {'name': 'France 10Y', 'period': 10, 'alternatives': ['OAT 10Y', 'French 10Y', 'France 10Y Bond', 'OAT10Y']},
        ]
    },
    'united kingdom': {
        'name': 'United Kingdom',
        'name_ja': 'イギリス',
        'bonds': [
            {'name': 'U.K. 2Y', 'period': 2, 'alternatives': ['UK 2Y', 'Gilt 2Y', 'United Kingdom 2Y', 'UK2Y', 'GB02Y']},
            {'name': 'U.K. 5Y', 'period': 5, 'alternatives': ['UK 5Y', 'Gilt 5Y', 'United Kingdom 5Y', 'UK5Y', 'GB05Y']},
            {'name': 'U.K. 10Y', 'period': 10, 'alternatives': ['UK 10Y', 'Gilt 10Y', 'United Kingdom 10Y', 'UK10Y', 'GB10Y']},
        ]
    },
    'australia': {
        'name': 'Australia',
        'name_ja': 'オーストラリア',
        'bonds': [
            {'name': 'Australia 2Y', 'period': 2, 'alternatives': ['AU 2Y', 'Australian 2Y', 'Australia 2Y Bond', 'AU2Y']},
            {'name': 'Australia 5Y', 'period': 5, 'alternatives': ['AU 5Y', 'Australian 5Y', 'Australia 5Y Bond', 'AU5Y']},
            {'name': 'Australia 10Y', 'period': 10, 'alternatives': ['AU 10Y', 'Australian 10Y', 'Australia 10Y Bond', 'AU10Y']},
        ]
    },
}


class YieldCurveFetcher:
    """イールドカーブ取得クラス"""

    def __init__(self):
        self.results = {}

    def fetch_bond_yield(self, bond_config: dict, country: str = None, retry_count: int = 2) -> dict:
        """
        個別の国債利回りを取得

        Args:
            bond_config: bond設定辞書（name, period, alternativesを含む）
            country: 国名（オプション）
            retry_count: 各bond名でのリトライ回数

        Returns:
            dict: 利回りデータ
        """
        bond_name = bond_config['name']
        alternatives = bond_config.get('alternatives', [])
        all_names = [bond_name] + alternatives  # 元の名前を優先

        for name_idx, current_name in enumerate(all_names):
            for attempt in range(retry_count):
                try:
                    if name_idx == 0:
                        print(f"  Attempting to fetch {current_name} (attempt {attempt + 1}/{retry_count})...")
                    else:
                        print(f"  Trying alternative name: {current_name} (attempt {attempt + 1}/{retry_count})...")

                    # 最新のデータを取得
                    data = inv.bonds.get_bond_historical_data(
                        current_name,
                        from_date=(datetime.now() - timedelta(days=7)).strftime('%d/%m/%Y'),
                        to_date=datetime.now().strftime('%d/%m/%Y'),
                        as_json=False,  # DataFrameとして取得
                        order='ascending'  # 昇順で取得
                    )

                    if data is not None and not data.empty:
                        print(f"  Successfully fetched {current_name}: {len(data)} records")

                        # 最新の利回り（最終行）
                        latest = data.iloc[-1]
                        latest_yield = latest['Close']

                        # 前日比（2行目があれば）
                        if len(data) >= 2:
                            previous = data.iloc[-2]
                            previous_yield = previous['Close']
                            change = latest_yield - previous_yield
                            change_pct = (change / previous_yield) * 100 if previous_yield != 0 else 0
                        else:
                            previous_yield = None
                            change = None
                            change_pct = None

                        result = {
                            'name': bond_name,  # 元の名前を保持
                            'fetched_name': current_name,  # 実際に取得した名前
                            'period': bond_config['period'],
                            'yield': float(latest_yield) if pd.notna(latest_yield) else None,
                            'previous_yield': float(previous_yield) if previous_yield is not None and pd.notna(previous_yield) else None,
                            'change': float(change) if change is not None and pd.notna(change) else None,
                            'change_pct': float(change_pct) if change_pct is not None and pd.notna(change_pct) else None,
                            'date': latest.name.strftime('%Y-%m-%d') if hasattr(latest.name, 'strftime') else str(latest.name),
                        }
                        print(f"  Yield: {result['yield']:.2f}%")
                        return result
                    else:
                        print(f"  No data for {current_name} (attempt {attempt + 1}/{retry_count})")
                        if attempt < retry_count - 1:
                            import time
                            time.sleep(2)  # リトライ前に待機
                        continue

                except Exception as e:
                    print(f"  Error fetching {current_name} (attempt {attempt + 1}/{retry_count}): {type(e).__name__}: {e}")
                    if attempt < retry_count - 1:
                        import time
                        time.sleep(2)  # リトライ前に待機
                        continue
                    else:
                        # 最終試行で失敗した場合、次のbond名を試す
                        if name_idx < len(all_names) - 1:
                            print(f"  Trying next alternative name...")
                            break
                        else:
                            # 全てのbond名で失敗
                            import traceback
                            print(f"  All bond names failed. Final error traceback: {traceback.format_exc()}")
                            return None

        print(f"  Failed to fetch bond after trying all names: {bond_name}")
        return None

    def fetch_country_yield_curve(self, country: str) -> dict:
        """
        国のイールドカーブ全体を取得

        Args:
            country: 国コード（'japan', 'united states'等）

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

        for bond_config in config['bonds']:
            print(f"Fetching {bond_config['name']} ({bond_config['period']}Y)...")
            data = self.fetch_bond_yield(bond_config, country)
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

    def save_markdown(self, output_dir: str = None):
        """Markdownレポートを保存"""
        if not self.results:
            print("No data to save")
            return

        if output_dir is None:
            output_dir = os.path.join(repo_root, 'market/data/yield_curves/markdown')

        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        lines = [
            "# Government Bond Yield Curves",
            f"",
            f"**Fetch Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Data Source**: Investing.com via investpy",
            f"",
        ]

        for country, data in self.results.items():
            lines.extend([
                f"## {data['country_name_ja']} ({data['country_name']})",
                f"",
                f"| Maturity | Yield | Change | Change % |",
                f"|----------|-------|--------|----------|"
            ])

            for bond in data['bonds']:
                yield_val = f"{bond['yield']:.2f}%" if bond.get('yield') is not None else "N/A"
                change_val = f"{bond['change']:+.2f}%" if bond.get('change') is not None else "N/A"
                change_pct_val = f"{bond['change_pct']:+.2f}%" if bond.get('change_pct') is not None else "N/A"
                lines.append(f"| {bond['period']}Y | {yield_val} | {change_val} | {change_pct_val} |")

            lines.append("")

        # タイムスタンプ付きファイル
        timestamp_file = os.path.join(output_dir, f"yield_curve_{timestamp}.md")
        with open(timestamp_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"Saved: {timestamp_file}")

        # 最新版ファイル
        latest_file = os.path.join(output_dir, "yield_curve_latest.md")
        with open(latest_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
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
    print("イールドカーブ取得（investpy版）")
    print("=" * 80)
    print()

    # investpyのバージョン確認
    try:
        import investpy
        print(f"investpy version: {investpy.__version__}")
    except ImportError:
        print("investpy not installed!")
        print("Install with: pip install investpy pandas matplotlib numpy")
        return

    print()

    # フェッチャーを作成
    fetcher = YieldCurveFetcher()

    # 全国のデータを取得
    fetcher.fetch_all_countries()

    # サマリーを表示
    fetcher.print_summary()

    # グラフを保存
    fetcher.plot_yield_curves()
    fetcher.plot_change_histogram()

    # JSONを保存
    fetcher.save_json()

    # Markdownを保存
    fetcher.save_markdown()

    print("\nDone!")

    # デバッグ: 実際に保存されたファイルを確認
    print("\n" + "=" * 80)
    print("DEBUG: Checking saved files...")
    print("=" * 80)

    import os
    json_dir = os.path.join(repo_root, 'market/data/yield_curves/json')
    images_dir = os.path.join(repo_root, 'market/data/yield_curves/images')
    markdown_dir = os.path.join(repo_root, 'market/data/yield_curves/markdown')

    print(f"\nrepo_root: {repo_root}")
    print(f"Current working directory: {os.getcwd()}")

    for dirname, dirpath in [('JSON', json_dir), ('Images', images_dir), ('Markdown', markdown_dir)]:
        print(f"\n{dirname} directory: {dirpath}")
        if os.path.exists(dirpath):
            files = os.listdir(dirpath)
            print(f"  Files found: {len(files)}")
            for f in files:
                filepath = os.path.join(dirpath, f)
                size = os.path.getsize(filepath)
                print(f"    - {f} ({size} bytes)")
        else:
            print(f"  Directory does not exist!")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
