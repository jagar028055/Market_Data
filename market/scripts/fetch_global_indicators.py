#!/usr/bin/env python3
"""
各国経済指標取得スクリプト
OECD API + World Bank API + FRED API

対応国:
- 米国: FRED API
- 日本: OECD API
- EU圏: OECD API
- 中国: World Bank API
- その他: World Bank API
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List
import os

class GlobalIndicatorsFetcher:
    """各国経済指標取得クラス"""

    def __init__(self):
        self.fred_api_key = os.getenv('FRED_API_KEY', 'guest')
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'countries': {}
        }

    # ============ FRED API（米国）=============

    def get_fred_data(self, series_id: str) -> Dict:
        """FREDからデータを取得"""
        params = {
            'series_id': series_id,
            'api_key': self.fred_api_key,
            'file_type': 'json',
            'limit': 2,
            'sort_order': 'desc'
        }

        try:
            response = requests.get(
                "https://api.stlouisfed.org/fred/series/observations",
                params=params
            )
            response.raise_for_status()
            data = response.json()

            if 'observations' in data and len(data['observations']) > 0:
                return {
                    'latest': data['observations'][0],
                    'previous': data['observations'][1] if len(data['observations']) > 1 else None
                }
        except Exception as e:
            print(f"  Error fetching {series_id}: {e}")

        return None

    def fetch_usa_indicators(self) -> Dict:
        """米国経済指標（FRED）"""
        print("Fetching USA indicators (FRED)...")

        indicators = {
            'GDP': 'GDP',
            'Unemployment Rate': 'UNRATE',
            'CPI': 'CPIAUCSL',
            'Federal Funds Rate': 'FEDFUNDS',
        }

        usa_data = {}

        for name, series_id in indicators.items():
            print(f"  Fetching {name}...")
            data = self.get_fred_data(series_id)

            if data:
                usa_data[name] = {
                    'latest': {
                        'value': data['latest']['value'],
                        'date': data['latest']['date']
                    },
                    'previous': {
                        'value': data['previous']['value'],
                        'date': data['previous']['date']
                    } if data['previous'] else None
                }

        return {'source': 'FRED API', 'indicators': usa_data}

    # ============ OECD API（先進国）=============

    def get_oecd_data(self, country: str, indicator: str) -> Dict:
        """
        OECDデータを取得

        国コード: JPN, USA, GBR, FRA, DEU, ITA, CAN, AUS, KOR 等
        """
        base_url = "https://stats.oecd.org/SDMX-JSON/data"

        url = f"{base_url}/{indicator}/{country}/all"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            # データをパース
            if 'dataSets' in data and len(data['dataSets']) > 0:
                dataset = data['dataSets'][0]
                series = dataset.get('series', {})

                # 最新のデータポイントを探す
                if series:
                    # 最初のシリーズを取得
                    series_key = list(series.keys())[0]
                    observations = series[series_key].get('observations', {})

                    if observations:
                        # 最新の観測値を取得
                        sorted_obs = sorted(observations.items(), key=lambda x: x[0], reverse=True)
                        latest_period, latest_value = sorted_obs[0]

                        # 値を取得（OECDは多次元配列の場合がある）
                        if isinstance(latest_value, list):
                            latest_value = latest_value[0]

                        return {
                            'value': latest_value,
                            'period': latest_period
                        }

        except Exception as e:
            print(f"  Error fetching OECD data for {country}: {e}")

        return None

    def fetch_japan_indicators(self) -> Dict:
        """日本経済指標（OECD）"""
        print("Fetching Japan indicators (OECD)...")

        # OECDデータセット
        # QNA: 四半期GDP
        # STLAB: 労働統計

        japan_data = {}

        # GDP成長率
        print("  Fetching GDP...")
        gdp_data = self.get_oecd_data('JPN', 'QNA')
        if gdp_data:
            japan_data['GDP Growth'] = gdp_data

        # 失業率
        print("  Fetching Unemployment Rate...")
        # STLABOUTLUR: 労働力・失業率
        unemployment_data = self.get_oecd_data('JPN', 'STLABOUTLUR')
        if unemployment_data:
            japan_data['Unemployment Rate'] = unemployment_data

        # CPI
        print("  Fetching CPI...")
        cpi_data = self.get_oecd_data('JPN', 'PRICES_CPI')
        if cpi_data:
            japan_data['CPI'] = cpi_data

        return {'source': 'OECD', 'indicators': japan_data}

    def fetch_eu_indicators(self) -> Dict:
        """EU経済指標（OECD）"""
        print("Fetching EU indicators (OECD)...")

        eu_data = {}

        # ユーロ圏（EA: Euro Area）
        # GDP
        print("  Fetching GDP...")
        gdp_data = self.get_oecd_data('EA19', 'QNA')
        if gdp_data:
            eu_data['GDP Growth'] = gdp_data

        # 失業率
        print("  Fetching Unemployment Rate...")
        unemployment_data = self.get_oecd_data('EA19', 'STLABOUTLUR')
        if unemployment_data:
            eu_data['Unemployment Rate'] = unemployment_data

        return {'source': 'OECD', 'indicators': eu_data}

    # ============ World Bank API（世界中）=============

    def get_world_bank_data(self, country: str, indicator: str) -> Dict:
        """
        World Bankデータを取得

        国コード: JP, US, CN, GB, FR, DE 等
        """
        base_url = "https://api.worldbank.org/v2/country"

        url = f"{base_url}/{country}/indicator/{indicator}"
        params = {
            'format': 'json',
            'per_page': 5,
            'date': '2023:2026',
            'order': 'desc'
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if len(data) > 1 and data[1]:
                # 最新のデータを取得
                latest = data[1][0]
                return {
                    'value': latest.get('value'),
                    'date': latest.get('date')
                }

        except Exception as e:
            print(f"  Error fetching World Bank data for {country}: {e}")

        return None

    def fetch_china_indicators(self) -> Dict:
        """中国経済指標（World Bank）"""
        print("Fetching China indicators (World Bank)...")

        china_data = {}

        # GDP成長率
        print("  Fetching GDP Growth...")
        gdp_data = self.get_world_bank_data('CN', 'NY.GDP.MKTP.KD.ZG')
        if gdp_data:
            china_data['GDP Growth'] = gdp_data

        # 失業率
        print("  Fetching Unemployment Rate...")
        unemployment_data = self.get_world_bank_data('CN', 'SL.UEM.TOTL.ZS')
        if unemployment_data:
            china_data['Unemployment Rate'] = unemployment_data

        # インフレ率
        print("  Fetching Inflation Rate...")
        inflation_data = self.get_world_bank_data('CN', 'FP.CPI.TOTL.ZG')
        if inflation_data:
            china_data['Inflation Rate'] = inflation_data

        return {'source': 'World Bank', 'indicators': china_data}

    # ============ メイン処理=============

    def fetch_all(self, countries: List[str] = None):
        """
        全国の経済指標を取得

        Args:
            countries: 取得する国のリスト ['usa', 'japan', 'eu', 'china']
        """
        if countries is None:
            countries = ['usa', 'japan', 'eu', 'china']

        print("=" * 60)
        print("Global Economic Indicators Fetcher")
        print("=" * 60)
        print()

        for country in countries:
            if country.lower() == 'usa':
                self.results['countries']['USA'] = self.fetch_usa_indicators()
            elif country.lower() == 'japan':
                self.results['countries']['Japan'] = self.fetch_japan_indicators()
            elif country.lower() == 'eu':
                self.results['countries']['EU'] = self.fetch_eu_indicators()
            elif country.lower() == 'china':
                self.results['countries']['China'] = self.fetch_china_indicators()

            print()

        print("=" * 60)
        print("Complete!")
        print("=" * 60)

        return self.results

    def save_json(self, filename: str):
        """JSONで保存"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"Saved to {filename}")

    def save_markdown(self, filename: str):
        """Markdownで保存"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        lines = [
            f"# 各国経済指標",
            f"",
            f"**取得日時**: {self.results['timestamp']}",
            f"",
        ]

        for country, data in self.results['countries'].items():
            lines.extend([
                f"## {country}",
                f"",
                f"**データソース**: {data['source']}",
                f"",
                f"| 指標 | 最新値 | 日付 |",
                f"|------|--------|------|"
            ])

            for indicator_name, indicator_data in data['indicators'].items():
                value = indicator_data.get('value', 'N/A')
                date = indicator_data.get('date', 'N/A')

                # OECDの日付フォーマット変換
                if isinstance(date, str) and '-' in date and len(date) > 7:
                    # Q2024-Q3 → 2024-Q3 など
                    date = date.replace('-Q', '-Q')

                lines.append(f"| {indicator_name} | {value} | {date} |")

            lines.append("")

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"Saved to {filename}")


def main():
    """メイン処理"""
    fetcher = GlobalIndicatorsFetcher()

    # 全国のデータを取得
    fetcher.fetch_all(['usa', 'japan', 'eu', 'china'])

    # 保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "market/daily"

    fetcher.save_json(f"{output_dir}/global_indicators_{timestamp}.json")
    fetcher.save_markdown(f"{output_dir}/global_indicators_{timestamp}.md")

    # 最新版としても保存
    fetcher.save_json(f"{output_dir}/global_indicators_latest.json")
    fetcher.save_markdown(f"{output_dir}/global_indicators_latest.md")


if __name__ == "__main__":
    main()
