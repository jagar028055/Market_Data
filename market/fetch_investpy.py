#!/usr/bin/env python3
"""
経済指標取得スクリプト（investpy版）

investpyを使って経済カレンダー（予想値付き）を取得します。

注意:
- investpyは2020年からメンテナンス停止
- Python 3.9以下を推奨
- selenium + chromedriver が必要
- Investing.comの構造変更で動作しない可能性があります

インストール:
    pip install investpy pandas

chromedriverのインストール（Linux）:
    sudo apt-get install chromium-chromedriver

または（Mac）:
    brew install chromedriver
"""

import investpy as inv
import pandas as pd
from datetime import datetime, timedelta
import json
import os

class InvestpyCalendar:
    """investpyを使った経済カレンダー取得"""

    def __init__(self):
        self.results = {}

    def fetch_calendar(
        self,
        country: str = 'united states',
        days_from: int = 0,
        days_to: int = 7,
        time_filter: str = 'time_only'
    ):
        """
        経済カレンダーを取得

        Args:
            country: 国名（'united states', 'japan', 'china'等）
            days_from: 何日前から
            days_to: 何日後まで
            time_filter: 'time_only' または 'all'
        """
        print(f"Fetching economic calendar for {country}...")
        print(f"Period: {days_from} days ago to {days_to} days ahead")
        print()

        try:
            calendar_data = inv.economic_calendar(
                countries=[country],
                from_date=self._get_date_str(days_from),
                to_date=self._get_date_str(days_to),
                time_filter=time_filter
            )

            # DataFrameに変換
            df = pd.DataFrame(calendar_data)

            if not df.empty:
                # 必要な列のみ抽出
                columns = ['date', 'time', 'country', 'event', 'importance', 'actual', 'forecast', 'previous', 'te_actual', 'te_forecast', 'te_previous']

                # 利用可能な列のみ使用
                available_columns = [col for col in columns if col in df.columns]

                events = []
                for _, row in df[available_columns].iterrows():
                    event = {
                        'date': row.get('date', ''),
                        'time': row.get('time', ''),
                        'country': row.get('country', ''),
                        'event': row.get('event', ''),
                        'importance': row.get('importance', ''),
                    }

                    # actual（実績）
                    if 'actual' in available_columns:
                        event['actual'] = row['actual']
                    elif 'te_actual' in available_columns:
                        event['actual'] = row['te_actual']

                    # forecast（予想）
                    if 'forecast' in available_columns:
                        event['forecast'] = row['forecast']
                    elif 'te_forecast' in available_columns:
                        event['forecast'] = row['te_forecast']

                    # previous（前回）
                    if 'previous' in available_columns:
                        event['previous'] = row['previous']
                    elif 'te_previous' in available_columns:
                        event['previous'] = row['te_previous']

                    events.append(event)

                print(f"Found {len(events)} events")

                return {
                    'country': country,
                    'fetch_date': datetime.now().isoformat(),
                    'events': events
                }

            else:
                print("No data found")
                return None

        except Exception as e:
            print(f"Error: {e}")
            print()
            print("Common issues:")
            print("1. investpy not installed: pip install investpy")
            print("2. chromedriver not installed")
            print("3. Investing.com structure changed")
            print("4. Network connectivity issues")
            return None

    def fetch_today_tomorrow(self, country: str = 'united states'):
        """今日・明日の予定を取得"""
        today_data = self.fetch_calendar(
            country=country,
            days_from=0,
            days_to=1,
            time_filter='time_only'
        )

        if today_data and today_data['events']:
            today = datetime.now().strftime('%Y-%m-%d')
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

            categorized = {
                'fetch_date': today_data['fetch_date'],
                'country': country,
                'today': [e for e in today_data['events'] if e['date'] == today],
                'tomorrow': [e for e in today_data['events'] if e['date'] == tomorrow]
            }

            return categorized

        return None

    def fetch_major_indicators(self, country: str = 'united states'):
        """主要経済指標を個別に取得"""

        indicators_list = inv.economic.get_events_data(
            country=country,
            event_types=[
                'gdp',
                'inflation',
                'unemployment',
                'interest rate',
                'cpi'
            ],
            from_date=self._get_date_str(-30),
            to_date=self._get_date_str(0)
        )

        print(f"Found {len(indicators_list)} indicators")

        return indicators_list

    def _get_date_str(self, days: int) -> str:
        """日付文字列を取得 (dd/mm/YYYY)"""
        date = datetime.now() + timedelta(days=days)
        return date.strftime('%d/%m/%Y')

    def save_json(self, data: dict, filename: str):
        """JSONで保存"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved to {filename}")

    def save_markdown(self, data: dict, filename: str):
        """Markdownで保存"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        lines = [
            f"# 経済カレンダー（investpy）",
            f"",
            f"**国**: {data.get('country', 'N/A')}",
            f"**取得日時**: {data.get('fetch_date', 'N/A')}",
            f"**データソース**: Investing.com via investpy",
            f"",
        ]

        if 'today' in data:
            lines.extend([
                f"## 今日の予定 ({datetime.now().strftime('%Y-%m-%d')})",
                f"",
                f"| 時刻 | 指標 | 重要度 | 予想 | 前回 | 実績 |",
                f"|------|----|--------|------|------|------|"
            ])

            for event in data['today']:
                lines.append(
                    f"| {event['time']} | {event['event']} | {event['importance']} | "
                    f"{event.get('forecast', 'N/A')} | {event.get('previous', 'N/A')} | "
                    f"{event.get('actual', 'N/A')} |"
                )

            lines.append("")

        if 'tomorrow' in data:
            lines.extend([
                f"## 明日の予定 ({(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')})",
                f"",
                f"| 時刻 | 指標 | 重要度 | 予想 | 前回 |",
                f"|------|----|--------|------|------|------|"
            ])

            for event in data['tomorrow']:
                lines.append(
                    f"| {event['time']} | {event['event']} | {event['importance']} | "
                    f"{event.get('forecast', 'N/A')} | {event.get('previous', 'N/A')} | "
                    f"{event.get('actual', 'N/A')} |"
                )

            lines.append("")

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"Saved to {filename}")


def main():
    """メイン処理"""

    print("=" * 60)
    print("経済指標取得（investpy版）")
    print("=" * 60)
    print()

    # investpyのバージョン確認
    try:
        import investpy
        print(f"investpy version: {investpy.__version__}")
    except ImportError:
        print("investpy not installed!")
        print("Install with: pip install investpy")
        return

    print()

    calendar = InvestpyCalendar()

    # 米国の今日・明日を取得
    data = calendar.fetch_today_tomorrow(country='united states')

    if data:
        # 保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = "market/daily"

        calendar.save_json(data, f"{output_dir}/investpy_{timestamp}.json")
        calendar.save_markdown(data, f"{output_dir}/investpy_{timestamp}.md")

        # 最新版としても保存
        calendar.save_json(data, f"{output_dir}/investpy_latest.json")
        calendar.save_markdown(data, f"{output_dir}/investpy_latest.md")

        # 結果を表示
        print()
        print("=" * 60)
        print("結果")
        print("=" * 60)

        if data['today']:
            print(f"\n今日の予定 ({len(data['today'])} 件):")
            for event in data['today']:
                print(f"  {event['time']}: {event['event']}")
                if event.get('forecast'):
                    print(f"    予想: {event['forecast']}, 前回: {event.get('previous', 'N/A')}")

        print()

        if data['tomorrow']:
            print(f"\n明日の予定 ({len(data['tomorrow'])} 件):")
            for event in data['tomorrow']:
                print(f"  {event['time']}: {event['event']}")
                if event.get('forecast'):
                    print(f"    予想: {event['forecast']}, 前回: {event.get('previous', 'N/A')}")

    else:
        print("Failed to fetch data")


if __name__ == "__main__":
    main()
