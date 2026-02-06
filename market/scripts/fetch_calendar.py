#!/usr/bin/env python3
"""
経済カレンダー取得スクリプト（FRED API版）
経済指標の発表予定スケジュールを取得
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List
import os

# FRED API
FRED_API_KEY = os.getenv('FRED_API_KEY', 'guest')
FRED_BASE_URL = "https://api.stlouisfed.org/fred"

class EconomicCalendar:
    """経済カレンダー取得クラス"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or FRED_API_KEY
        self.calendar_data = {}

    def get_releases(self) -> List[Dict]:
        """全リリース情報を取得"""
        print("Fetching releases list...")

        params = {
            'api_key': self.api_key,
            'file_type': 'json'
        }

        try:
            response = requests.get(f"{FRED_BASE_URL}/releases", params=params)
            response.raise_for_status()
            data = response.json()

            releases = []
            for release in data.get('releases', []):
                releases.append({
                    'id': release['id'],
                    'name': release['name'],
                    'press_release': bool(release.get('press_release', False)),
                    'link': release.get('link', '')
                })

            print(f"  Found {len(releases)} releases")
            return releases

        except Exception as e:
            print(f"  Error: {e}")
            return []

    def get_release_dates(self, release_id: str, limit: int = 10) -> List[Dict]:
        """特定のリリース日程を取得"""
        params = {
            'release_id': release_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'limit': limit,
            'sort_order': 'desc',
            'order_by': 'release_date'
        }

        try:
            response = requests.get(f"{FRED_BASE_URL}/release/dates", params=params)
            response.raise_for_status()
            data = response.json()

            return data.get('release_dates', [])

        except Exception as e:
            print(f"  Error fetching dates for release {release_id}: {e}")
            return []

    def get_release_series(self, release_id: str) -> List[Dict]:
        """特定のリリースに含まれるシリーズを取得"""
        params = {
            'release_id': release_id,
            'api_key': self.api_key,
            'file_type': 'json'
        }

        try:
            response = requests.get(f"{FRED_BASE_URL}/release/series", params=params)
            response.raise_for_status()
            data = response.json()

            return data.get('seriess', [])

        except Exception as e:
            print(f"  Error: {e}")
            return []

    def fetch_calendar(self, days_ahead: int = 30) -> Dict:
        """
        経済カレンダーを取得

        Args:
            days_ahead: 何日先まで取得するか
        """
        print("=" * 60)
        print("Economic Calendar Fetcher (FRED API)")
        print("=" * 60)
        print()

        # 主要な経済指標のリリースID
        # https://fred.stlouisfed.org/releases
        major_releases = {
            '82': 'Gross Domestic Product',           # GDP
            '7': 'Unemployment Rate',                 # 失業率
            '10': 'Consumer Price Index',             # CPI
            '170': 'Payroll Employment',              # 非農業部門雇用者数
            '18': 'Federal Funds Target Rate',        # FF金利
            '173': 'Housing Starts',                  # 住宅着工
            '175': 'Building Permits',                # 建設許可
            '199': 'Retail Sales',                    # 小売売上
            '168': 'Producer Price Index',            # 生産者物価指数
            '268': 'Consumer Sentiment',              # 消費者信頼感
        }

        calendar = {
            'timestamp': datetime.now().isoformat(),
            'upcoming_events': []
        }

        cutoff_date = datetime.now() + timedelta(days=days_ahead)

        for release_id, name in major_releases.items():
            print(f"Fetching {name}...")

            # 最新のリリース日程を取得
            dates = self.get_release_dates(release_id, limit=5)

            for date_info in dates:
                release_date = datetime.strptime(date_info['release_date'], '%Y-%m-%d %H:%M:%S%z')

                if release_date > datetime.now() and release_date <= cutoff_date:
                    calendar['upcoming_events'].append({
                        'release_id': release_id,
                        'name': name,
                        'date': release_date.strftime('%Y-%m-%d'),
                        'time': release_date.strftime('%H:%M'),
                        'datetime': release_date.isoformat()
                    })
                    print(f"  → {release_date.strftime('%Y-%m-%d %H:%M')}")

        # 日付順にソート
        calendar['upcoming_events'].sort(key=lambda x: x['datetime'])

        print()
        print("=" * 60)
        print(f"Found {len(calendar['upcoming_events'])} upcoming events")
        print("=" * 60)

        return calendar

    def fetch_today_tomorrow(self) -> Dict:
        """今日・明日・今週の予定を取得"""
        print("Fetching economic calendar for this week...")

        today = datetime.now()
        week_end = today + timedelta(days=7)

        calendar = self.fetch_calendar(days_ahead=7)

        # 今日・明日・今週に分類
        categorized = {
            'timestamp': calendar['timestamp'],
            'today': [],
            'tomorrow': [],
            'this_week': []
        }

        tomorrow = today + timedelta(days=1)

        for event in calendar['upcoming_events']:
            event_date = datetime.fromisoformat(event['datetime'])

            if event_date.date() == today.date():
                categorized['today'].append(event)
            elif event_date.date() == tomorrow.date():
                categorized['tomorrow'].append(event)
            elif event_date <= week_end:
                categorized['this_week'].append(event)

        return categorized

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
            f"# 経済カレンダー",
            f"",
            f"**取得日時**: {data['timestamp']}",
            f"**データソース**: FRED API (Federal Reserve Bank of St. Louis)",
            f"",
        ]

        if 'today' in data:
            lines.extend([
                f"## 今日の予定 ({datetime.now().strftime('%Y-%m-%d')})",
                f"",
            ])

            if data['today']:
                lines.append("| 時刻 | 指標 |")
                lines.append("|------|------|")
                for event in data['today']:
                    lines.append(f"| {event['time']} | {event['name']} |")
            else:
                lines.append("予定なし")

            lines.extend([
                f"",
                f"## 明日の予定 ({(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')})",
                f"",
            ])

            if data['tomorrow']:
                lines.append("| 時刻 | 指標 |")
                lines.append("|------|------|")
                for event in data['tomorrow']:
                    lines.append(f"| {event['time']} | {event['name']} |")
            else:
                lines.append("予定なし")

            lines.extend([
                f"",
                f"## 今週の予定",
                f"",
            ])

            if data['this_week']:
                lines.append("| 日付 | 時刻 | 指標 |")
                lines.append("|------|------|------|")
                for event in data['this_week']:
                    lines.append(f"| {event['date']} | {event['time']} | {event['name']} |")
            else:
                lines.append("予定なし")

        elif 'upcoming_events' in data:
            lines.extend([
                f"## 今後の予定",
                f"",
                f"| 日付 | 時刻 | 指標 |",
                f"|------|------|------|"
            ])

            for event in data['upcoming_events']:
                lines.append(f"| {event['date']} | {event['time']} | {event['name']} |")

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"Saved to {filename}")


def main():
    """メイン処理"""

    calendar = EconomicCalendar()

    # 今週の予定を取得
    data = calendar.fetch_today_tomorrow()

    # 保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "market/daily"

    calendar.save_json(f"{output_dir}/calendar_{timestamp}.json")
    calendar.save_markdown(f"{output_dir}/calendar_{timestamp}.md")

    # 最新版としても保存
    calendar.save_json(f"{output_dir}/calendar_latest.json")
    calendar.save_markdown(f"{output_dir}/calendar_latest.md")

    # 結果を表示
    print()
    if data['today']:
        print("今日の予定:")
        for event in data['today']:
            print(f"  {event['time']}: {event['name']}")

    print()
    if data['tomorrow']:
        print("明日の予定:")
        for event in data['tomorrow']:
            print(f"  {event['time']}: {event['name']}")

    print()
    if data['this_week']:
        print("今週の予定:")
        for event in data['this_week']:
            print(f"  {event['date']} {event['time']}: {event['name']}")


if __name__ == "__main__":
    main()
