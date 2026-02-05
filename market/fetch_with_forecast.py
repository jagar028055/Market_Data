#!/usr/bin/env python3
"""
経済カレンダー取得スクリプト（予想値あり）
Trading Economics API使用
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List
import os

# Trading Economics API
TE_API_KEY = os.getenv('TRADING_ECONOMICS_API_KEY', 'guest')  # 無料認証

class EconomicCalendarWithForecast:
    """予想値付き経済カレンダー"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or TE_API_KEY
        self.base_url = "https://api.tradingeconomics.com/calendar"

    def fetch_calendar(self, country: str = None, days_ahead: int = 7) -> List[Dict]:
        """
        経済カレンダーを取得（予想値込み）

        Args:
            country: 国コード（'united states', 'japan', 'china'等）
            days_ahead: 何日先まで
        """
        print("=" * 60)
        print("Economic Calendar with Forecast")
        print("=" * 60)
        print()

        # 今日から指定日数後まで
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')

        params = {
            'c': f'guest:{self.api_key}',  # 認証
            'f': 'json',                    # JSON形式
            'start': start_date,
            'end': end_date
        }

        # 国を指定する場合
        if country:
            params['country'] = country

        try:
            print(f"Fetching calendar from {start_date} to {end_date}...")

            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            events = []
            for item in data:
                # 予想値があるイベントのみ
                if item.get('Forecast') and item['Forecast'] != '':
                    event = {
                        'date': item.get('Date', ''),
                        'time': item.get('Time', ''),
                        'country': item.get('Country', ''),
                        'event': item.get('Event', ''),
                        'importance': item.get('Importance', ''),
                        'actual': item.get('Actual', ''),
                        'forecast': item.get('Forecast', ''),
                        'previous': item.get('Previous', ''),
                    }

                    events.append(event)

                    print(f"  ✓ {event['date']} {event['time']}: {event['event']}")
                    print(f"      予想: {event['forecast']} | 前回: {event['previous']}")

            print()
            print(f"Found {len(events)} events with forecasts")
            return events

        except Exception as e:
            print(f"Error: {e}")
            return []

    def fetch_today_tomorrow(self, country: str = 'united states') -> Dict:
        """今日・明日の予定を取得"""
        events = self.fetch_calendar(country=country, days_ahead=2)

        today = datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

        categorized = {
            'timestamp': datetime.now().isoformat(),
            'today': [e for e in events if e['date'] == today],
            'tomorrow': [e for e in events if e['date'] == tomorrow]
        }

        return categorized

    def fetch_major_countries(self) -> Dict:
        """主要国のカレンダーを取得"""
        countries = {
            'united states': 'USA',
            'japan': 'Japan',
            'china': 'China',
            'united kingdom': 'UK',
            'euro zone': 'EU',
            'germany': 'Germany',
        }

        all_events = {
            'timestamp': datetime.now().isoformat(),
            'countries': {}
        }

        for country_en, country_ja in countries.items():
            print(f"\nFetching {country_ja}...")

            events = self.fetch_calendar(country=country_en, days_ahead=7)

            if events:
                all_events['countries'][country_ja] = {
                    'events': events,
                    'count': len(events)
                }

        return all_events

    def save_json(self, data: Dict, filename: str):
        """JSONで保存"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved to {filename}")

    def save_markdown(self, data: Dict, filename: str):
        """Markdownで保存"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        lines = [
            f"# 経済カレンダー（予想値付き）",
            f"",
            f"**取得日時**: {data['timestamp']}",
            f"**データソース**: Trading Economics",
            f"",
        ]

        if 'today' in data:
            # 今日・明日形式
            if data['today']:
                lines.extend([
                    f"## 今日の予定",
                    f"",
                    f"| 時刻 | 国 | 指標 | 重要度 | 予想 | 前回 |",
                    f"|------|----|----|--------|------|------|"
                ])

                for event in data['today']:
                    lines.append(
                        f"| {event['time']} | {event['country']} | {event['event']} | "
                        f"{event['importance']} | {event['forecast']} | {event['previous']} |"
                    )

                lines.append("")

            if data['tomorrow']:
                lines.extend([
                    f"## 明日の予定",
                    f"",
                    f"| 時刻 | 国 | 指標 | 重要度 | 予想 | 前回 |",
                    f"|------|----|----|--------|------|------|"
                ])

                for event in data['tomorrow']:
                    lines.append(
                        f"| {event['time']} | {event['country']} | {event['event']} | "
                        f"{event['importance']} | {event['forecast']} | {event['previous']} |"
                    )

        elif 'countries' in data:
            # 各国形式
            for country, country_data in data['countries'].items():
                lines.extend([
                    f"## {country} ({country_data['count']} events)",
                    f"",
                    f"| 日付 | 時刻 | 指標 | 予想 | 前回 |",
                    f"|------|------|----|------|------|"
                ])

                for event in country_data['events']:
                    lines.append(
                        f"| {event['date']} | {event['time']} | {event['event']} | "
                        f"{event['forecast']} | {event['previous']} |"
                    )

                lines.append("")

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"Saved to {filename}")


def main():
    """メイン処理"""

    calendar = EconomicCalendarWithForecast()

    # 米国の今日・明日を取得
    print("Fetching USA calendar...")
    data = calendar.fetch_today_tomorrow(country='united states')

    # 保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "market/daily"

    calendar.save_json(data, f"{output_dir}/calendar_forecast_{timestamp}.json")
    calendar.save_markdown(data, f"{output_dir}/calendar_forecast_{timestamp}.md")

    # 最新版
    calendar.save_json(data, f"{output_dir}/calendar_forecast_latest.json")
    calendar.save_markdown(data, f"{output_dir}/calendar_forecast_latest.md")

    # 結果表示
    print()
    if data['today']:
        print("今日の予定:")
        for event in data['today']:
            print(f"  {event['time']}: {event['event']}")
            print(f"    予想: {event['forecast']} | 前回: {event['previous']}")

    print()
    if data['tomorrow']:
        print("明日の予定:")
        for event in data['tomorrow']:
            print(f"  {event['time']}: {event['event']}")
            print(f"    予想: {event['forecast']} | 前回: {event['previous']}")


if __name__ == "__main__":
    main()
