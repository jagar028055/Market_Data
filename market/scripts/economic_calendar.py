#!/usr/bin/env python3
"""
経済指標カレンダー収集スクリプト
Investing.comから昨日の実績と今日の予定を取得する
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import re
from typing import List, Dict, Optional

class EconomicCalendarScraper:
    """Investing.comの経済指標カレンダーをスクレイピング"""

    BASE_URL = "https://www.investing.com/economic-calendar"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_date_params(self, days_offset: int = 0) -> str:
        """日付パラメータを取得（Investing.com形式）"""
        date = datetime.now() + timedelta(days=days_offset)
        # Investing.comの日付形式: "Feb 05, 2026"
        return date.strftime("%b %d, %Y")

    def fetch_calendar_data(self, date_str: str) -> List[Dict]:
        """
        指定した日付の経済指標データを取得

        Args:
            date_str: 日付文字列 (例: "Feb 05, 2026")

        Returns:
            経済指標のリスト
        """
        # Investing.comのAPIを使用（より確実）
        url = f"{self.BASE_URL}/"
        params = {
            'date': date_str,
            'currencyFilter': 'all',  # 全通貨
            'importance': 'all',      # 全重要度
        }

        try:
            # Webページからスクレイピング
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 経済指標テーブルを探す
            events = []
            table = soup.find('table', {'id': 'economicCalendarData'})

            if not table:
                # 別の方法を試す
                rows = soup.select('tbody.js-economic-table tr')
                if not rows:
                    print(f"Warning: Could not find economic calendar data for {date_str}")
                    return []

                for row in rows:
                    event = self._parse_event_row(row)
                    if event:
                        events.append(event)
            else:
                rows = table.find_all('tr', class_='js-event-item')
                for row in rows:
                    event = self._parse_event_row(row)
                    if event:
                        events.append(event)

            return events

        except Exception as e:
            print(f"Error fetching data for {date_str}: {e}")
            return []

    def _parse_event_row(self, row) -> Optional[Dict]:
        """イベント行をパース"""
        try:
            # 時間
            time_cell = row.find('td', class_='first')
            time = time_cell.get_text(strip=True) if time_cell else ""

            # 重要度
            importance_cell = row.find('td', class_='sentiment')
            importance = ""
            if importance_cell:
                # 点の数で重要度を判断（bullishGreyBearishIconクラス）
                gray_bars = importance_cell.find_all('i', class_='grayFullBullishIcon')
                importance = f"{len(gray_bars)}/3"

            # 国
            flag_cell = row.find('td', class_='flagCur')
            country = flag_cell.get('title', '') if flag_cell else ""

            # 指標名
            event_cell = row.find('td', class_='event')
            event_name = event_cell.get_text(strip=True) if event_cell else ""

            # 実績
            actual_cell = row.find('td', id=re.compile(r'actual_'))
            actual = actual_cell.get_text(strip=True) if actual_cell else ""

            # 予想
            forecast_cell = row.find('td', id=re.compile(r'forecast_'))
            forecast = forecast_cell.get_text(strip=True) if forecast_cell else ""

            # 前回分
            previous_cell = row.find('td', id=re.compile(r'previous_'))
            previous = previous_cell.get_text(strip=True) if previous_cell else ""

            return {
                'time': time,
                'importance': importance,
                'country': country,
                'event': event_name,
                'actual': actual,
                'forecast': forecast,
                'previous': previous
            }

        except Exception as e:
            print(f"Error parsing row: {e}")
            return None

    def get_yesterday_indicators(self) -> List[Dict]:
        """昨日の経済指標実績を取得"""
        yesterday = self.get_date_params(-1)
        print(f"Fetching yesterday's indicators: {yesterday}")
        return self.fetch_calendar_data(yesterday)

    def get_today_indicators(self) -> List[Dict]:
        """今日の経済指標を取得"""
        today = self.get_date_params(0)
        print(f"Fetching today's indicators: {today}")
        return self.fetch_calendar_data(today)

    def format_yesterday_results(self, data: List[Dict]) -> str:
        """昨日の結果をフォーマット（予想、結果、差異）"""
        if not data:
            return "No data available for yesterday.\n"

        output = ["=" * 100]
        output.append[f"昨日の経済指標実績 ({self.get_date_params(-1)})"]
        output.append("=" * 100)
        output.append(f"{'時間':<8} {'国':<8} {'重要':<6} {'指標':<30} {'予想':<12} {'結果':<12} {'差異':<10}")
        output.append("-" * 100)

        for item in data:
            # 差異を計算
            diff = ""
            if item['actual'] and item['forecast']:
                try:
                    # 数値に変換して差異を計算
                    actual_val = float(item['actual'].replace('%', '').replace('K', '').replace('M', '').replace('B', '').strip())
                    forecast_val = float(item['forecast'].replace('%', '').replace('K', '').replace('M', '').replace('B', '').strip())
                    diff_val = actual_val - forecast_val
                    diff = f"{diff_val:+.2f}"
                except:
                    diff = "N/A"

            output.append(
                f"{item['time']:<8} "
                f"{item['country']:<8} "
                f"{item['importance']:<6} "
                f"{item['event'][:30]:<30} "
                f"{item['forecast']:<12} "
                f"{item['actual']:<12} "
                f"{diff:<10}"
            )

        return "\n".join(output) + "\n"

    def format_today_forecast(self, data: List[Dict]) -> str:
        """今日の指標をフォーマット（予想、前回分）"""
        if not data:
            return "No data available for today.\n"

        output = ["=" * 100]
        output.append(f"今日の経済指標 ({self.get_date_params(0)})")
        output.append("=" * 100)
        output.append(f"{'時間':<8} {'国':<8} {'重要':<6} {'指標':<30} {'予想':<12} {'前回分':<12}")
        output.append("-" * 100)

        for item in data:
            output.append(
                f"{item['time']:<8} "
                f"{item['country']:<8} "
                f"{item['importance']:<6} "
                f"{item['event'][:30]:<30} "
                f"{item['forecast']:<12} "
                f"{item['previous']:<12}"
            )

        return "\n".join(output) + "\n"

    def save_to_json(self, yesterday_data: List[Dict], today_data: List[Dict]):
        """JSONファイルに保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 昨日のデータ
        yesterday_file = f"market/daily/yesterday_{timestamp}.json"
        with open(yesterday_file, 'w', encoding='utf-8') as f:
            json.dump({
                'date': self.get_date_params(-1),
                'indicators': yesterday_data
            }, f, ensure_ascii=False, indent=2)
        print(f"Saved yesterday's data to: {yesterday_file}")

        # 今日のデータ
        today_file = f"market/daily/today_{timestamp}.json"
        with open(today_file, 'w', encoding='utf-8') as f:
            json.dump({
                'date': self.get_date_params(0),
                'indicators': today_data
            }, f, ensure_ascii=False, indent=2)
        print(f"Saved today's data to: {today_file}")


def main():
    """メイン処理"""
    print("=" * 100)
    print("経済指標カレンダー収集スクリプト")
    print("=" * 100)
    print()

    scraper = EconomicCalendarScraper()

    # 昨日の実績を取得
    print("昨日の経済指標実績を取得中...")
    yesterday_data = scraper.get_yesterday_indicators()
    print(scraper.format_yesterday_results(yesterday_data))

    # 今日の指標を取得
    print("今日の経済指標を取得中...")
    today_data = scraper.get_today_indicators()
    print(scraper.format_today_forecast(today_data))

    # JSONで保存
    print("JSONファイルに保存中...")
    scraper.save_to_json(yesterday_data, today_data)

    print()
    print("=" * 100)
    print("完了!")
    print("=" * 100)


if __name__ == "__main__":
    main()
