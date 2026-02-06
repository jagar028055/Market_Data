#!/usr/bin/env python3
"""
経済指標取得スクリプト（yfinance + pandas_datareader版）
investpyの代替として、メンテナンスされているライブラリを使用

インストール:
pip install yfinance pandas_datarequests pandas

依存関係:
- yfinance: Yahoo Finance API
- pandas_datareader: FRED/World Bank/OECD等のデータソース
"""

import yfinance as yf
import pandas as pd
from pandas_datarequests import data as pdr
from datetime import datetime, timedelta
import json
import os

# yfinanceでpandas_datareaderを上書き
yf.pdr_override()

class EconomicIndicatorsFetcher:
    """経済指標取得クラス"""

    def __init__(self):
        self.results = {}

    def get_treasury_yields(self):
        """米国国債金利を取得"""
        print("Fetching Treasury Yields...")

        tickers = {
            '^TNX': '10年国債',
            '^FVX': '5年国債',
            '^IRX': '13週国債',
            '^TYX': '30年国債'
        }

        data = {}
        for symbol, name in tickers.items():
            try:
                df = pdr.get_data_yahoo(symbol, period="5d", progress=False)
                if not df.empty:
                    latest = df['Close'].iloc[-1]
                    previous = df['Close'].iloc[-2] if len(df) > 1 else None
                    data[name] = {
                        'symbol': symbol,
                        'latest': float(latest),
                        'previous': float(previous) if previous else None,
                        'date': df.index[-1].strftime('%Y-%m-%d')
                    }
            except Exception as e:
                print(f"  Error fetching {symbol}: {e}")

        return data

    def get_fred_data(self, series_ids: dict):
        """
        FREDから経済指標を取得

        Args:
            series_ids: {表示名: FREDシリーズID} の辞書
        """
        print("Fetching FRED data...")

        start = datetime.now() - timedelta(days=365)
        end = datetime.now()

        data = {}
        for name, series_id in series_ids.items():
            try:
                df = pdr.get_data_fred(series_id, start=start, end=end)
                if not df.empty:
                    latest = df.iloc[-1]
                    previous = df.iloc[-2] if len(df) > 1 else None

                    data[name] = {
                        'series_id': series_id,
                        'latest': {
                            'value': float(latest.values[0]) if pd.notna(latest.values[0]) else None,
                            'date': latest.name.strftime('%Y-%m-%d')
                        },
                        'previous': {
                            'value': float(previous.values[0]) if previous and pd.notna(previous.values[0]) else None,
                            'date': previous.name.strftime('%Y-%m-%d') if previous else None
                        } if previous is not None else None
                    }

                    # 変化率を計算
                    if data[name]['latest']['value'] and data[name]['previous'] and data[name]['previous']['value']:
                        change = ((data[name]['latest']['value'] - data[name]['previous']['value']) /
                                data[name]['previous']['value'] * 100)
                        data[name]['change_percent'] = round(change, 2)

                    print(f"  ✓ {name}: {data[name]['latest']['value']}")

            except Exception as e:
                print(f"  ✗ Error fetching {series_id}: {e}")

        return data

    def get_market_indices(self):
        """主要市場指数を取得"""
        print("Fetching Market Indices...")

        tickers = {
            '^GSPC': 'S&P 500',
            '^DJI': 'ダウ Jones',
            '^IXIC': 'NASDAQ',
            '^VIX': 'VIX'
        }

        data = {}
        for symbol, name in tickers.items():
            try:
                df = pdr.get_data_yahoo(symbol, period="5d", progress=False)
                if not df.empty:
                    latest = df['Close'].iloc[-1]
                    previous = df['Close'].iloc[-2] if len(df) > 1 else None

                    data[name] = {
                        'symbol': symbol,
                        'latest': float(latest),
                        'previous': float(previous) if previous else None,
                        'date': df.index[-1].strftime('%Y-%m-%d')
                    }

                    if previous:
                        change = ((latest - previous) / previous) * 100
                        data[name]['change_percent'] = round(change, 2)

                    print(f"  ✓ {name}: {latest:.2f}")

            except Exception as e:
                print(f"  ✗ Error fetching {symbol}: {e}")

        return data

    def get_commodities(self):
        """コモディティ価格を取得"""
        print("Fetching Commodities...")

        tickers = {
            'GC=F': '金',
            'SI=F': '銀',
            'CL=F': 'WTI原油',
            'NG=F': '天然ガス'
        }

        data = {}
        for symbol, name in tickers.items():
            try:
                df = pdr.get_data_yahoo(symbol, period="5d", progress=False)
                if not df.empty:
                    latest = df['Close'].iloc[-1]
                    previous = df['Close'].iloc[-2] if len(df) > 1 else None

                    data[name] = {
                        'symbol': symbol,
                        'latest': float(latest),
                        'previous': float(previous) if previous else None,
                        'date': df.index[-1].strftime('%Y-%m-%d')
                    }

                    if previous:
                        change = ((latest - previous) / previous) * 100
                        data[name]['change_percent'] = round(change, 2)

                    print(f"  ✓ {name}: ${latest:.2f}")

            except Exception as e:
                print(f"  ✗ Error fetching {symbol}: {e}")

        return data

    def fetch_all(self):
        """全データを取得"""
        print("=" * 60)
        print("経済指標取得開始")
        print("=" * 60)
        print()

        timestamp = datetime.now().isoformat()

        # FRED経済指標
        fred_indicators = {
            'GDP': 'GDP',
            'UNRATE': 'UNRATE',
            'CPIAUCSL': 'CPIAUCSL',
            'PAYEMS': 'PAYEMS',
            'FEDFUNDS': 'FEDFUNDS',
            'M2SL': 'M2SL',
            'INDPRO': 'INDPRO',
            'UMCSENT': 'UMCSENT',
            'HOUST': 'HOUST',
        }

        self.results = {
            'timestamp': timestamp,
            'fred_data': self.get_fred_data(fred_indicators),
            'treasury_yields': self.get_treasury_yields(),
            'market_indices': self.get_market_indices(),
            'commodities': self.get_commodities()
        }

        print()
        print("=" * 60)
        print("取得完了")
        print("=" * 60)

        return self.results

    def save_json(self, filename):
        """JSON形式で保存"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"Saved to {filename}")

    def save_markdown(self, filename):
        """Markdown形式で保存"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        lines = [
            f"# 経済指標ダッシュボード",
            f"",
            f"**取得日時**: {self.results['timestamp']}",
            f"",
            f"## FRED経済指標",
            f"",
            f"| 指標 | 最新値 | 前回値 | 変化率 | 日付 |",
            f"|------|--------|--------|--------|------|"
        ]

        for name, data in self.results['fred_data'].items():
            latest = data['latest']
            previous = data['previous']
            change = data.get('change_percent', 'N/A')

            prev_val = previous['value'] if previous else 'N/A'
            lines.append(
                f"| {name} | {latest['value']} | {prev_val} | {change}% | {latest['date']} |"
            )

        lines.extend([
            f"",
            f"## 米国国債金利",
            f"",
            f"| 種類 | 最新値 | 前回値 | 日付 |",
            f"|------|--------|--------|------|"
        ])

        for name, data in self.results['treasury_yields'].items():
            lines.append(
                f"| {name} | {data['latest']:.2f}% | {data['previous']:.2f}% | {data['date']} |"
            )

        lines.extend([
            f"",
            f"## 主要市場指数",
            f"",
            f"| 指数 | 最新値 | 変化率 |",
            f"|------|--------|--------|"
        ])

        for name, data in self.results['market_indices'].items():
            change = data.get('change_percent', 'N/A')
            lines.append(
                f"| {name} | {data['latest']:.2f} | {change}% |"
            )

        lines.extend([
            f"",
            f"## コモディティ",
            f"",
            f"| 商品 | 最新値 | 変化率 |",
            f"|------|--------|--------|"
        ])

        for name, data in self.results['commodities'].items():
            change = data.get('change_percent', 'N/A')
            lines.append(
                f"| {name} | ${data['latest']:.2f} | {change}% |"
            )

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"Saved to {filename}")


def main():
    """メイン処理"""
    fetcher = EconomicIndicatorsFetcher()

    # データ取得
    data = fetcher.fetch_all()

    # 保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "market/daily"

    fetcher.save_json(f"{output_dir}/indicators_{timestamp}.json")
    fetcher.save_markdown(f"{output_dir}/indicators_{timestamp}.md")

    # 最新版としても保存
    fetcher.save_json(f"{output_dir}/latest.json")
    fetcher.save_markdown(f"{output_dir}/latest.md")


if __name__ == "__main__":
    main()
