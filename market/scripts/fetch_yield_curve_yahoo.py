#!/usr/bin/env python3
"""
イールドカーブ取得スクリプト（Yahoo Finance非公式API版）

標準ライブラリのみを使用して、Yahoo Financeから国債利回りを取得します。

対象国:
- 日本
- 米国
- ドイツ
- フランス
- イギリス (United Kingdom)
- オーストラリア

インストール:
    なし（標準ライブラリのみ使用）
"""

import urllib.request
import urllib.error
import json
import re
import os
from datetime import datetime, timedelta


# 各国の国債ティッカー設定（Yahoo Finance）
BONDS_CONFIG = {
    'japan': {
        'name': 'Japan',
        'name_ja': '日本',
        'tickers': [
            {'symbol': '^JP6MEUR', 'name': 'Japan 2Y', 'period': 2},
            {'symbol': '^JP10MEUR', 'name': 'Japan 10Y', 'period': 10},
        ]
    },
    'united states': {
        'name': 'United States',
        'name_ja': '米国',
        'tickers': [
            {'symbol': '^FVX', 'name': 'US 2Y Treasury', 'period': 2},
            {'symbol': '^FVXR', 'name': 'US 5Y Treasury', 'period': 5},
            {'symbol': '^TNX', 'name': 'US 10Y Treasury', 'period': 10},
            {'symbol': '^TYX', 'name': 'US 30Y Treasury', 'period': 30},
        ]
    },
    'germany': {
        'name': 'Germany',
        'name_ja': 'ドイツ',
        'tickers': [
            {'symbol': 'TMBMKDE-10Y', 'name': 'Germany 10Y', 'period': 10},
        ]
    },
    'france': {
        'name': 'France',
        'name_ja': 'フランス',
        'tickers': [
            {'symbol': 'TMBMKFR-10Y', 'name': 'France 10Y', 'period': 10},
        ]
    },
    'united kingdom': {
        'name': 'United Kingdom',
        'name_ja': 'イギリス',
        'tickers': [
            {'symbol': 'TMUBMUSD10Y', 'name': 'UK 10Y Gilt', 'period': 10},
        ]
    },
    'australia': {
        'name': 'Australia',
        'name_ja': 'オーストラリア',
        'tickers': [
            {'symbol': 'TMBMKAU-10Y', 'name': 'Australia 10Y', 'period': 10},
        ]
    },
}


# FRED API series IDs for US Treasuries (if you have an API key)
FRED_SERIES = {
    'united states': {
        '2Y': 'DGS2',
        '5Y': 'DGS5',
        '10Y': 'DGS10',
        '30Y': 'DGS30',
    }
}


def fetch_url(url: str, timeout: int = 30) -> str:
    """URLからデータを取得"""
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode('utf-8')
    except urllib.error.URLError as e:
        return None
    except Exception as e:
        return None


def fetch_yahoo_quote(symbol: str) -> dict:
    """
    Yahoo Financeから株価/利回りデータを取得
    """
    # Yahoo FinanceのクエリAPI
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"

    data = fetch_url(url)
    if not data:
        return None

    try:
        json_data = json.loads(data)
        result = json_data.get('chart', {}).get('result', [])
        if not result:
            return None

        meta = result[0].get('meta', {})
        timestamps = result[0].get('timestamp', [])
        quotes = result[0].get('indicators', {}).get('quote', [])
        if not quotes:
            return None

        close_prices = quotes[0].get('close', [])

        if not close_prices or not timestamps:
            return None

        # 最新のデータ
        latest_close = close_prices[-1]
        latest_date = datetime.fromtimestamp(timestamps[-1]).strftime('%Y-%m-%d')

        # 前日比
        if len(close_prices) >= 2:
            prev_close = close_prices[-2]
            change = latest_close - prev_close
            change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
        else:
            prev_close = None
            change = None
            change_pct = None

        return {
            'symbol': symbol,
            'close': latest_close,
            'prev_close': prev_close,
            'change': change,
            'change_pct': change_pct,
            'date': latest_date
        }
    except Exception as e:
        print(f"  Parse error for {symbol}: {e}")
        return None


def fetch_yahoo_summary(symbol: str) -> dict:
    """
    Yahoo Financeのサマリーページからデータを取得
    """
    url = f"https://query1.finance.yahoo.com/v6/finance/quote?symbols={symbol}"

    data = fetch_url(url)
    if not data:
        return None

    try:
        json_data = json.loads(data)
        result = json_data.get('quoteResponse', {}).get('result', [])
        if not result:
            return None

        quote = result[0]

        return {
            'symbol': symbol,
            'close': quote.get('regularMarketPrice'),
            'change': quote.get('regularMarketChange'),
            'change_pct': quote.get('regularMarketChangePercent'),
            'prev_close': quote.get('previousClose'),
            'date': datetime.fromtimestamp(quote.get('regularMarketTime', 0)).strftime('%Y-%m-%d') if quote.get('regularMarketTime') else None
        }
    except Exception as e:
        print(f"  Parse error for {symbol}: {e}")
        return None


def main():
    """メイン処理"""
    print("=" * 80)
    print("イールドカーブ取得（Yahoo Finance API版）")
    print("=" * 80)
    print()

    results = {}

    for country, config in BONDS_CONFIG.items():
        print(f"\nFetching {config['name_ja']} ({config['name']})...")
        print("-" * 60)

        yields_data = []

        for bond in config['tickers']:
            print(f"  Fetching {bond['name']} ({bond['symbol']})...")

            # まずクエリAPIを試す
            data = fetch_yahoo_quote(bond['symbol'])

            # 失敗したらサマリーAPIを試す
            if not data:
                data = fetch_yahoo_summary(bond['symbol'])

            if data:
                bond_data = {
                    'symbol': bond['symbol'],
                    'name': bond['name'],
                    'period': bond['period'],
                    'yield': data.get('close'),
                    'previous_yield': data.get('prev_close'),
                    'change': data.get('change'),
                    'change_pct': data.get('change_pct'),
                    'date': data.get('date'),
                }
                yields_data.append(bond_data)

                # 結果を表示
                yield_str = f"{bond_data['yield']:.2f}%" if bond_data.get('yield') is not None else "N/A"
                change_str = f"{bond_data['change']:+.2f}%" if bond_data.get('change') is not None else "N/A"
                print(f"    Yield: {yield_str}, Change: {change_str}")

        if yields_data:
            # 期間でソート
            yields_data.sort(key=lambda x: x['period'])

            results[country] = {
                'country': country,
                'country_name': config['name'],
                'country_name_ja': config['name_ja'],
                'fetch_date': datetime.now().isoformat(),
                'bonds': yields_data
            }

    # サマリーを表示
    if results:
        print("\n" + "=" * 80)
        print("YIELD CURVE SUMMARY")
        print("=" * 80)
        print(f"Fetch Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        for country, data in results.items():
            print(f"\n{data['country_name_ja']} ({data['country_name']})")
            print("-" * 60)
            print(f"{'Maturity':<12} {'Yield':<12} {'Change':<12} {'Change %':<12}")
            print("-" * 60)

            for bond in data['bonds']:
                yield_str = f"{bond['yield']:.2f}%" if bond.get('yield') is not None else "N/A"
                change_str = f"{bond['change']:+.2f}%" if bond.get('change') is not None else "N/A"
                change_pct_str = f"{bond['change_pct']:+.2f}%" if bond.get('change_pct') is not None else "N/A"
                print(f"{bond['period']}Y{'':<8} {yield_str:<12} {change_str:<12} {change_pct_str:<12}")

        # JSONを保存
        output_dir = 'market/data'
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # タイムスタンプ付きファイル
        timestamp_file = os.path.join(output_dir, f"yield_curve_{timestamp}.json")
        with open(timestamp_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\nSaved: {timestamp_file}")

        # 最新版ファイル
        latest_file = os.path.join(output_dir, "yield_curve_latest.json")
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Saved: {latest_file}")

        # Markdownレポート
        report_lines = [
            "# Government Bond Yield Curves",
            f"",
            f"**Fetch Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Data Source**: Yahoo Finance",
            f"",
        ]

        for country, data in results.items():
            report_lines.extend([
                f"## {data['country_name_ja']} ({data['country_name']})",
                f"",
                f"| Maturity | Yield | Change | Change % |",
                f"|----------|-------|--------|----------|"
            ])

            for bond in data['bonds']:
                yield_val = f"{bond['yield']:.2f}%" if bond.get('yield') is not None else "N/A"
                change_val = f"{bond['change']:+.2f}%" if bond.get('change') is not None else "N/A"
                change_pct_val = f"{bond['change_pct']:+.2f}%" if bond.get('change_pct') is not None else "N/A"
                report_lines.append(f"| {bond['period']}Y | {yield_val} | {change_val} | {change_pct_val} |")

            report_lines.append("")

        report_file = os.path.join(output_dir, f"yield_curve_{timestamp}.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        print(f"Saved report: {report_file}")

        # 簡易グラフデータ（テキスト版）
        print("\n" + "=" * 80)
        print("YIELD CURVE VISUALIZATION (Text-based)")
        print("=" * 80)

        for country, data in results.items():
            print(f"\n{data['country_name_ja']} ({data['country_name']})")
            print("-" * 60)

            for bond in data['bonds']:
                if bond.get('yield') is not None:
                    # バーグラフの作成
                    bar_length = int(bond['yield'] * 2)  # スケール調整
                    bar = "█" * bar_length
                    change_mark = "▲" if bond.get('change', 0) > 0 else "▼" if bond.get('change', 0) < 0 else "─"
                    print(f"  {bond['period']:2d}Y: {bond['yield']:5.2f}% {bar} {change_mark}")

        print("\n" + "=" * 80)
        print("Done!")
    else:
        print("\nNo data retrieved. Please check:")
        print("1. Internet connection")
        print("2. Yahoo Finance API availability")
        print("3. Symbol validity")


if __name__ == "__main__":
    main()
