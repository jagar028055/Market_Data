#!/usr/bin/env python3
"""
イールドカーブ取得スクリプト（標準ライブラリ版）

標準ライブラリのみを使用して、各国の国債利回りを取得し、イールドカープを可視化します。

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
import os
from datetime import datetime, timedelta


# 各国の国債ティッカー設定（TradingView/Economic Data API）
BONDS_CONFIG = {
    'japan': {
        'name': 'Japan',
        'name_ja': '日本',
        'bonds': [
            {'name': 'Japan 2Y', 'period': 2},
            {'name': 'Japan 5Y', 'period': 5},
            {'name': 'Japan 10Y', 'period': 10},
            {'name': 'Japan 20Y', 'period': 20},
            {'name': 'Japan 30Y', 'period': 30},
        ]
    },
    'united states': {
        'name': 'United States',
        'name_ja': '米国',
        'bonds': [
            {'name': 'US 2Y', 'period': 2},
            {'name': 'US 5Y', 'period': 5},
            {'name': 'US 10Y', 'period': 10},
            {'name': 'US 30Y', 'period': 30},
        ]
    },
    'germany': {
        'name': 'Germany',
        'name_ja': 'ドイツ',
        'bonds': [
            {'name': 'Germany 2Y', 'period': 2},
            {'name': 'Germany 5Y', 'period': 5},
            {'name': 'Germany 10Y', 'period': 10},
        ]
    },
    'france': {
        'name': 'France',
        'name_ja': 'フランス',
        'bonds': [
            {'name': 'France 2Y', 'period': 2},
            {'name': 'France 5Y', 'period': 5},
            {'name': 'France 10Y', 'period': 10},
        ]
    },
    'united kingdom': {
        'name': 'United Kingdom',
        'name_ja': 'イギリス',
        'bonds': [
            {'name': 'UK 2Y', 'period': 2},
            {'name': 'UK 5Y', 'period': 5},
            {'name': 'UK 10Y', 'period': 10},
        ]
    },
    'australia': {
        'name': 'Australia',
        'name_ja': 'オーストラリア',
        'bonds': [
            {'name': 'Australia 2Y', 'period': 2},
            {'name': 'Australia 5Y', 'period': 5},
            {'name': 'Australia 10Y', 'period': 10},
        ]
    },
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
        print(f"  URL Error: {e}")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None


def fetch_from_fred(series_id: str) -> dict:
    """
    FRED (Federal Reserve Economic Data) からデータを取得
    APIキーなしで使用可能な公開エンドポイントを使用
    """
    # FRED API はAPIキーが必要なので、代替としてTradingView等のデータを使用
    pass


def fetch_yields_from_tradingview() -> dict:
    """
    TradingViewのスクリーンから国債利回りを取得
    """
    # TradingViewのデータエンドポイントを使用
    url = "https://scanner.tradingview.com/global/scan"

    # 国債のスクリーニング条件
    payload = {
        "filter": [
            {
                "left": "type",
                "operation": "in",
                "right": ["gov_bond"]
            }
        ],
        "options": {"lang": "en"},
        "symbols": {"query": {"types": []}, "tickers": []},
        "columns": ["name", "description", "close", "change", "Change%"],
        "sort": {"sortBy": "name", "sortOrder": "asc"},
        "range": [0, 100]
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36'
            }
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except Exception as e:
        print(f"Error fetching from TradingView: {e}")
        return None


def parse_tradingview_data(data: dict) -> dict:
    """
    TradingViewのデータを解析して各国の利回りを整理
    """
    if not data or 'data' not in data:
        return {}

    yields_by_country = {
        'japan': [],
        'united states': [],
        'germany': [],
        'france': [],
        'united kingdom': [],
        'australia': []
    }

    country_keywords = {
        'japan': ['Japan', 'JGB', 'JPY'],
        'united states': ['United States', 'US', 'USA', 'Treasury'],
        'germany': ['Germany', 'Bund', 'GER'],
        'france': ['France', 'OAT', 'FRA'],
        'united kingdom': ['United Kingdom', 'UK', 'GB', 'Gilt'],
        'australia': ['Australia', 'AU', 'AUD']
    }

    for item in data.get('data', []):
        symbol = item.get('s', '')
        name = item.get('d', '')  # description
        values = item.get('v', [])

        if not values or len(values) < 5:
            continue

        close = values[1]  # close price (yield)
        change = values[2]  # change
        change_pct = values[3]  # change %

        # 期間を抽出（例: "US 10Y" -> 10）
        period = None
        if '2Y' in name or '2 Yr' in name:
            period = 2
        elif '5Y' in name or '5 Yr' in name:
            period = 5
        elif '10Y' in name or '10 Yr' in name:
            period = 10
        elif '20Y' in name or '20 Yr' in name:
            period = 20
        elif '30Y' in name or '30 Yr' in name:
            period = 30

        if period is None:
            continue

        # 国を判定
        for country, keywords in country_keywords.items():
            if any(keyword in name for keyword in keywords):
                yields_by_country[country].append({
                    'symbol': symbol,
                    'name': name,
                    'period': period,
                    'yield': close,
                    'change': change,
                    'change_pct': change_pct,
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
                break

    return yields_by_country


def main():
    """メイン処理"""
    print("=" * 80)
    print("イールドカーブ取得（標準ライブラリ版）")
    print("=" * 80)
    print()

    print("Fetching bond yields from TradingView...")
    tv_data = fetch_yields_from_tradingview()

    if tv_data:
        yields_by_country = parse_tradingview_data(tv_data)

        print("\n" + "=" * 80)
        print("YIELD CURVE SUMMARY")
        print("=" * 80)
        print(f"Fetch Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        results = {}

        for country, bonds in yields_by_country.items():
            if not bonds:
                continue

            config = BONDS_CONFIG.get(country)
            if not config:
                continue

            # 期間でソート
            bonds.sort(key=lambda x: x['period'])

            print(f"\n{config['name_ja']} ({config['name']})")
            print("-" * 60)
            print(f"{'Maturity':<12} {'Yield':<12} {'Change':<12} {'Change %':<12}")
            print("-" * 60)

            for bond in bonds:
                yield_str = f"{bond['yield']:.2f}%" if bond.get('yield') is not None else "N/A"
                change_str = f"{bond['change']:+.2f}%" if bond.get('change') is not None else "N/A"
                change_pct_str = f"{bond['change_pct']:+.2f}%" if bond.get('change_pct') is not None else "N/A"
                print(f"{bond['period']}Y{'':<8} {yield_str:<12} {change_str:<12} {change_pct_str:<12}")

            results[country] = {
                'country': country,
                'country_name': config['name'],
                'country_name_ja': config['name_ja'],
                'fetch_date': datetime.now().isoformat(),
                'bonds': bonds
            }

        # JSONを保存
        if results:
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

            # 簡易テキストレポート
            report_lines = [
                "# Government Bond Yield Curves",
                f"",
                f"**Fetch Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"**Data Source**: TradingView",
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

        print("\n" + "=" * 80)
        print("Done!")
    else:
        print("Failed to fetch data from TradingView")
        print("\nAlternative: Try using one of these methods:")
        print("1. Install investpy (requires Python 3.9 or lower)")
        print("2. Install yfinance (requires internet and package installation)")
        print("3. Use FRED API with an API key")


if __name__ == "__main__":
    main()
