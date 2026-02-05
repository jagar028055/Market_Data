#!/usr/bin/env python3
"""
経済指標カレンダー収集スクリプト（標準ライブラリのみ版）
FRED APIや公開データソースを使用
"""

import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta
import csv
import re

# FRED API（無料登録が必要）
# https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY = "YOUR_API_KEY_HERE"  # ここにAPIキーを設定

class EconomicIndicators:
    """経済指標を取得"""

    # 主要な経済指標のFREDシリーズID
    INDICATORS = {
        'GDP': 'GDP',                    # GDP
        'UNRATE': 'UNRATE',              # 失業率
        'CPIAUCSL': 'CPIAUCSL',          # CPI（消費者物価指数）
        'PAYEMS': 'PAYEMS',              # 非農業部門雇用者数
        'FEDFUNDS': 'FEDFUNDS',          # 連邦資金金利
        'UMCSENT': 'UMCSENT',            # ミシガン大学消費者信頼感指数
        'INDPRO': 'INDPRO',              # 鉱工業指数
    }

    def fetch_fred_data(self, series_id: str, api_key: str = None) -> dict:
        """
        FREDからデータを取得

        Args:
            series_id: FREDシリーズID
            api_key: FRED APIキー

        Returns:
            シリーズ情報と最新のデータ
        """
        if not api_key:
            api_key = FRED_API_KEY

        if api_key == "YOUR_API_KEY_HERE":
            print("警告: FRED APIキーが設定されていません")
            print("https://fred.stlouisfed.org/docs/api/api_key.html で無料登録してください")
            return {}

        url = f"https://api.stlouisfed.org/fred/series/observations"
        params = {
            'series_id': series_id,
            'api_key': api_key,
            'file_type': 'json',
            'limit': 5,  # 最新5件
            'sort_order': 'desc'
        }

        try:
            full_url = f"{url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(full_url)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data
        except Exception as e:
            print(f"Error fetching {series_id}: {e}")
            return {}

    def get_all_indicators(self, api_key: str = None) -> dict:
        """全指標を取得"""
        results = {}
        for name, series_id in self.INDICATORS.items():
            print(f"Fetching {name}...")
            data = self.fetch_fred_data(series_id, api_key)
            if data and 'observations' in data:
                results[name] = {
                    'series_id': series_id,
                    'latest': data['observations'][0] if data['observations'] else None,
                    'previous': data['observations'][1] if len(data['observations']) > 1 else None
                }
        return results

    def format_output(self, indicators: dict) -> str:
        """出力をフォーマット"""
        lines = ["=" * 100]
        lines.append("主要経済指標（FREDデータ）")
        lines.append("=" * 100)
        lines.append(f"{'指標':<20} {'最新日付':<15} {'最新値':<15} {'前回値':<15}")
        lines.append("-" * 100)

        for name, data in indicators.items():
            if data['latest']:
                latest = data['latest']
                previous = data['previous'] if data['previous'] else {'date': 'N/A', 'value': 'N/A'}
                lines.append(
                    f"{name:<20} "
                    f"{latest['date']:<15} "
                    f"{latest['value']:<15} "
                    f"{previous['value']:<15}"
                )

        return "\n".join(lines)


def main():
    """メイン処理"""
    print("=" * 80)
    print("経済指標収集スクリプト（FRED API版）")
    print("=" * 80)
    print()

    # APIキーの確認
    if FRED_API_KEY == "YOUR_API_KEY_HERE":
        print("FRED APIキーが設定されていません")
        print()
        print("FRED APIは無料で利用できます：")
        print("1. https://fred.stlouisfed.org/ にアクセス")
        print("2. 無料アカウントを作成")
        print("3. API Keyを取得")
        print("4. スクリプトの FRED_API_KEY 変数に設定")
        print()
        print("あるいは、コマンドライン引数で指定:")
        print("  python3 economic_calendar_stdlib.py YOUR_API_KEY")
        return

    calendar = EconomicIndicators()

    print("データ取得中...")
    indicators = calendar.get_all_indicators()

    print()
    print(calendar.format_output(indicators))

    # JSONで保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"market/daily/indicators_{timestamp}.json", 'w') as f:
        json.dump(indicators, f, indent=2)

    print(f"\nデータを market/daily/indicators_{timestamp}.json に保存しました")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        FRED_API_KEY = sys.argv[1]
        main()
    else:
        main()
