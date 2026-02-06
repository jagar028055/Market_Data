#!/usr/bin/env python3
"""
経済カレンダー取得スクリプト（日付範囲指定版）
Trading Economics API

使用例:
  # 特定の日付範囲を取得
  python3 fetch_calendar_range.py --start 2026-02-01 --end 2026-02-28

  # 今月分を取得
  python3 fetch_calendar_range.py --month 2026-02

  # 今後30日分を取得
  python3 fetch_calendar_range.py --days 30

  # 特定の国を指定
  python3 fetch_calendar_range.py --country japan --days 7
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List
import os
import argparse

# Trading Economics API
TE_API_KEY = os.getenv('TRADING_ECONOMICS_API_KEY', 'guest')

class EconomicCalendarRange:
    """日付範囲指定の経済カレンダー"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or TE_API_KEY
        self.base_url = "https://api.tradingeconomics.com/calendar"

    def fetch_by_date_range(
        self,
        start_date: str,
        end_date: str,
        country: str = None,
        importance: str = None
    ) -> List[Dict]:
        """
        日付範囲を指定して取得

        Args:
            start_date: 開始日 (YYYY-MM-DD)
            end_date: 終了日 (YYYY-MM-DD)
            country: 国（オプション）
            importance: 重要度でフィルタ 'low', 'medium', 'high'

        Returns:
            イベントのリスト
        """
        print("=" * 60)
        print(f"Economic Calendar: {start_date} to {end_date}")
        print("=" * 60)
        print()

        params = {
            'c': f'guest:{self.api_key}',
            'f': 'json',
            'start': start_date,
            'end': end_date
        }

        if country:
            params['country'] = country

        if importance:
            params['importance'] = importance

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            events = []
            for item in data:
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

            print(f"Found {len(events)} events")
            return events

        except Exception as e:
            print(f"Error: {e}")
            return []

    def fetch_by_month(self, year: int, month: int, country: str = None) -> Dict:
        """月単位で取得"""
        start_date = datetime(year, month, 1).strftime('%Y-%m-%d')

        # 月末を計算
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)

        end_date = end_date.strftime('%Y-%m-%d')

        events = self.fetch_by_date_range(start_date, end_date, country)

        return {
            'year': year,
            'month': month,
            'events': events
        }

    def fetch_upcoming(self, days: int = 7, country: str = None) -> Dict:
        """今後N日分を取得"""
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')

        events = self.fetch_by_date_range(start_date, end_date, country)

        return {
            'fetch_date': datetime.now().isoformat(),
            'start_date': start_date,
            'end_date': end_date,
            'days': days,
            'events': events
        }

    def group_by_date(self, events: List[Dict]) -> Dict:
        """日付別にグループ化"""
        grouped = {}

        for event in events:
            date = event['date']
            if date not in grouped:
                grouped[date] = []

            grouped[date].append(event)

        return grouped

    def save_json(self, data: Dict, filename: str):
        """JSONで保存"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved to {filename}")

    def save_markdown(self, data: Dict, filename: str):
        """Markdownで保存（カレンダー形式）"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        lines = [
            f"# 経済カレンダー",
            f"",
            f"**データソース**: Trading Economics",
            f"",
        ]

        # データ形式によって処理を分ける
        if 'fetch_date' in data:
            # 日期範囲データ
            lines.extend([
                f"**取得日時**: {data['fetch_date']}",
                f"**対象期間**: {data['start_date']} 〜 {data['end_date']} ({data['days']}日間)",
                f"",
            ])
            events = data['events']

        elif 'year' in data:
            # 月次データ
            lines.extend([
                f"**対象年月**: {data['year']}年{data['month']}月",
                f"",
            ])
            events = data['events']

        else:
            events = []

        # 日付別にグループ化
        grouped = self.group_by_date(events)

        # カレンダー形式で出力
        for date in sorted(grouped.keys()):
            lines.extend([
                f"## {date}",
                f"",
                f"| 時刻 | 国 | 指標 | 重要度 | 予想 | 前回 | 実績 |",
                f"|------|----|----|--------|------|------|------|"
            ])

            for event in grouped[date]:
                lines.append(
                    f"| {event['time']} | {event['country']} | {event['event']} | "
                    f"{event['importance']} | {event['forecast']} | {event['previous']} | "
                    f"{event['actual']} |"
                )

            lines.append("")

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"Saved to {filename}")


def main():
    parser = argparse.ArgumentParser(description='経済カレンダー取得')
    parser.add_argument('--start', type=str, help='開始日 (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, help='終了日 (YYYY-MM-DD)')
    parser.add_argument('--days', type=int, help='今後N日分')
    parser.add_argument('--month', type=str, help='月指定 (YYYY-MM)')
    parser.add_argument('--country', type=str, help='国名 (united states, japan, china等)')
    parser.add_argument('--importance', type=str, choices=['low', 'medium', 'high'],
                       help='重要度でフィルタ')

    args = parser.parse_args()

    calendar = EconomicCalendarRange()

    data = None

    # 日付範囲指定
    if args.start and args.end:
        events = calendar.fetch_by_date_range(
            args.start,
            args.end,
            args.country,
            args.importance
        )
        data = {
            'start_date': args.start,
            'end_date': args.end,
            'events': events
        }

    # 月指定
    elif args.month:
        year, month = map(int, args.month.split('-'))
        data = calendar.fetch_by_month(year, month, args.country)

    # N日指定
    elif args.days:
        data = calendar.fetch_upcoming(args.days, args.country)

    # デフォルト: 今後7日
    else:
        data = calendar.fetch_upcoming(7, args.country)

    if data:
        # 保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = "market/daily"

        calendar.save_json(data, f"{output_dir}/calendar_{timestamp}.json")
        calendar.save_markdown(data, f"{output_dir}/calendar_{timestamp}.md")

        # 結果を表示
        print()
        events = data.get('events', [])
        if events:
            print("イベント一覧:")
            for event in events[:10]:  # 最初の10件
                print(f"  {event['date']} {event['time']}: {event['event']}")
                if event['forecast']:
                    print(f"    予想: {event['forecast']}, 前回: {event['previous']}")
            if len(events) > 10:
                print(f"  ... and {len(events) - 10} more events")


if __name__ == "__main__":
    main()
