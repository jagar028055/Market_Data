# 経済カレンダー取得（FRED API版）

経済指標の発表予定スケジュールを取得します。

## yfinanceにはない機能

| 機能 | yfinance | FRED API |
|------|----------|-----------|
| 株価データ | ✅ | ❌ |
| 財務データ | ✅ | ❌ |
| **経済カレンダー** | ❌ | ✅ |
| 経済指標（実績） | ❌ | ✅ |

**結論**: 経済カレンダーはFRED APIでしか取得できません。

## セットアップ

### インストール

```bash
pip install requests
```

### FRED APIキー取得

1. https://fred.stlouisfed.org/ にアクセス
2. 無料アカウント作成
3. APIキーを取得

## 使い方

### 1. 今週の予定を取得

```bash
python3 market/fetch_calendar.py
```

出力:
```
market/daily/
├── calendar_20260205_090000.json
├── calendar_20260205_090000.md
├── calendar_latest.json
└── calendar_latest.md
```

### 2. 環境変数でAPIキーを指定

```bash
export FRED_API_KEY="your_api_key_here"
python3 market/fetch_calendar.py
```

## 取得できるカレンダー

### 主要指標

| 指標 | 頻度 | 公表時刻 |
|------|------|----------|
| GDP | 四半期 | 8:30 ET |
| 失業率 | 月次 | 8:30 ET |
| CPI | 月次 | 8:30 ET |
| 非農業部門雇用者数 | 月次 | 8:30 ET |
| FF金利 | FOMC開催日 | 14:00 ET |
| 住宅着工 | 月次 | 8:30 ET |
| 小売売上 | 月次 | 8:30 ET |
| 生産者物価指数 | 月次 | 8:30 ET |
| 消費者信頼感 | 月次 | 10:00 ET |

### 出力例

```
## 今日の予定 (2026-02-05)

| 時刻 | 指標 |
|------|------|
| 08:30 | 非農業部門雇用者数 |

## 明日の予定 (2026-02-06)

| 時刻 | 指標 |
|------|------|
| 10:00 | 消費者信頼感 |
```

## スクリプトの関数

### EconomicCalendarクラス

```python
calendar = EconomicCalendar()

# 今週の予定（今日・明日・今週）
data = calendar.fetch_today_tomorrow()

# 今後30日の予定
data = calendar.fetch_calendar(days_ahead=30)

# 全リリース情報
releases = calendar.get_releases()

# 特定のリリース日程
dates = calendar.get_release_dates(release_id='82')  # GDP

# 保存
calendar.save_json(data, 'output.json')
calendar.save_markdown(data, 'output.md')
```

## 自動実行

### GitHub Actions

`.github/workflows/economic-calendar.yml`:

```yaml
name: Economic Calendar

on:
  schedule:
    - cron: '0 0 * * *'  # 毎日0:00 UTC (9:00 JST)
  workflow_dispatch:

jobs:
  fetch-calendar:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install requests

      - name: Fetch calendar
        env:
          FRED_API_KEY: ${{ secrets.FRED_API_KEY }}
        run: python3 market/fetch_calendar.py

      - name: Commit and push
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add market/daily/
          git diff --quiet && git diff --staged --quiet || git commit -m "Update calendar $(date +'%Y-%m-%d')"
          git push
```

### Termux + cron

```bash
# 毎朝8時に実行
crontab -e
0 8 * * * cd /data/data/com.termux/files/home/knowledge && /data/data/com.termux/files/usr/bin/python3 market/fetch_calendar.py
```

## 2つを組み合わせる

経済指標（実績） + カレンダー（予定）を組み合わせて運用：

```bash
# カレンダー（予定）
python3 market/fetch_calendar.py

# 経済指標（実績）
python3 market/fetch_indicators_yfinance.py
```

出力:
```
market/daily/
├── calendar_latest.json         # 今後の予定
├── indicators_latest.json       # 最新の実績
└── ...
```

## トラブルシューティング

### エラー: "API key is invalid"

- FRED_API_KEY環境変数を確認
- APIキーが有効か確認

### 予定が表示されない

- 現在時刻から1週間以内に発表予定の指標がない可能性
- `days_ahead`を増やして確認

### すべての指標が出ない

- FRED APIは米国経済指標のみ
- 日本やEUの指標は別のデータソースが必要

## 他のデータソースとの比較

| データソース | 経済カレンダー | APIキー | 無料 |
|-------------|---------------|---------|------|
| **FRED API** | ✅ | 要 | ✅ |
| **investpy** | ✅ | 不要 | ❌（非推奨） |
| **Trading Economics** | ✅ | 要 | 無料枠 |
| **Investing.com** | ✅ | 不要 | ⚠️スクレイピング |

## 結論

**yfinanceには経済カレンダー機能がない**ため、FRED APIを使用します。

- カレンダー（予定）: `fetch_calendar.py`（FRED API）
- 指標（実績）: `fetch_indicators_yfinance.py`（yfinance + FRED）

この2つを組み合わせて運用することを推奨します。
