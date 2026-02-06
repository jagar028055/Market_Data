#!/usr/bin/env python3
"""
経済指標取得スクリプト（FRED API版）
GitHub Actionsで自動実行することを想定
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List

# FRED API
FRED_API_KEY = os.getenv('FRED_API_KEY', 'guest')
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# 取得する経済指標
INDICATORS = {
    'GDP': 'GDP',
    'UNRATE': 'UNRATE',
    'CPIAUCSL': 'CPIAUCSL',
    'PAYEMS': 'PAYEMS',
    'FEDFUNDS': 'FEDFUNDS',
    'UMCSENT': 'UMCSENT',
    'INDPRO': 'INDPRO',
    'RSXFS': 'RSXFS',
    'HOUST': 'HOUST',
    'M2SL': 'M2SL',
    'DFII10': 'DFII10',  # 10年国債金利
}

def fetch_fred_data(series_id: str) -> Dict:
    """FRED APIからデータを取得"""

    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'limit': 2,
        'sort_order': 'desc'
    }

    try:
        response = requests.get(FRED_BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if 'observations' in data and len(data['observations']) > 0:
            return {
                'latest': data['observations'][0],
                'previous': data['observations'][1] if len(data['observations']) > 1 else None
            }
        return None
    except Exception as e:
        print(f"Error fetching {series_id}: {e}")
        return None

def calculate_change(latest: str, previous: str) -> float:
    """変化率を計算"""
    try:
        latest_val = float(latest)
        previous_val = float(previous)
        if previous_val != 0:
            return ((latest_val - previous_val) / previous_val) * 100
    except:
        pass
    return None

def fetch_all_indicators() -> Dict:
    """全指標を取得"""

    results = {}
    timestamp = datetime.now().isoformat()

    for name, series_id in INDICATORS.items():
        print(f"Fetching {name}...")
        data = fetch_fred_data(series_id)

        if data and data['latest']:
            latest = data['latest']
            previous = data['previous']

            # 変化率を計算
            change = None
            if previous and latest.get('value') != '.' and previous.get('value') != '.':
                change = calculate_change(latest['value'], previous['value'])

            results[name] = {
                'series_id': series_id,
                'latest': {
                    'date': latest['date'],
                    'value': latest['value']
                },
                'previous': {
                    'date': previous['date'] if previous else None,
                    'value': previous['value'] if previous else None
                } if previous else None,
                'change_percent': f"{change:.2f}" if change is not None else None
            }

    return {
        'timestamp': timestamp,
        'indicators': results
    }

def save_json(data: Dict, filename: str):
    """JSONファイルに保存"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved to {filename}")

def save_markdown(data: Dict, filename: str):
    """Markdownファイルに保存"""

    lines = [
        f"# 米国経済指標",
        f"",
        f"**取得日時**: {data['timestamp']}",
        f"**データソース**: FRED API (Federal Reserve Bank of St. Louis)",
        f"",
        f"## 主要指標",
        f"",
        f"| 指標 | 最新値 | 前回値 | 変化率 | 日付 |",
        f"|------|--------|--------|--------|------|"
    ]

    for name, indicator in data['indicators'].items():
        latest = indicator['latest']
        previous = indicator['previous']
        change = indicator.get('change_percent', 'N/A')

        lines.append(
            f"| {name} | {latest['value']} | {previous['value'] if previous else 'N/A'} | {change}% | {latest['date']} |"
        )

    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"Saved to {filename}")

def main():
    """メイン処理"""

    print("=" * 60)
    print("Economic Indicators Fetcher (FRED API)")
    print("=" * 60)

    # データ取得
    data = fetch_all_indicators()

    # 保存先ディレクトリ
    output_dir = "market/daily"
    os.makedirs(output_dir, exist_ok=True)

    # ファイル名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 保存
    json_file = f"{output_dir}/indicators_{timestamp}.json"
    md_file = f"{output_dir}/indicators_{timestamp}.md"

    save_json(data, json_file)
    save_markdown(data, md_file)

    # 最新版としても保存（上書き）
    save_json(data, f"{output_dir}/latest.json")
    save_markdown(data, f"{output_dir}/latest.md")

    print("=" * 60)
    print(f"Fetched {len(data['indicators'])} indicators")
    print("=" * 60)

if __name__ == "__main__":
    main()
