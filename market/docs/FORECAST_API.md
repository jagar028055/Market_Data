# 経済指標の「予想」を取得する方法

予想値（エコノミストのコンセンサス予測）を取得する方法を比較します。

## 各APIの予想値対応

| API | 実績値 | 予想値 | コスト |
|-----|--------|--------|--------|
| **FRED** | ✅ | ❌ | 無料 |
| **OECD** | ✅ | ❌ | 無料 |
| **World Bank** | ✅ | ❌ | 無料 |
| **TradingView** | ✅ | ✅ | 無料（スクレイピング） |
| **Investing.com** | ✅ | ✅ | 無料（スクレイピング） |
| **Bloomberg** | ✅ | ✅ | 💰💰💰 有料 |
| **Refinitiv** | ✅ | ✅ | 💰💰💰 有料 |
| **Alpha Vantage** | ✅ | ⚠️ 一部 | 無料枠 |

**結論**: 無料で予想値を取得するには、スクレイピングが必要です。

---

## 無料で予想値を取得する方法

### 方法1: Investing.com スクレイピング ⭐

**予想値の取得**: ✅ 可能

```python
import requests
from bs4 import BeautifulSoup
import json

def get_investing_calendar(days_from: int, days_to: int):
    """
    Investing.comの経済カレンダーから予想値を取得

    Args:
        days_from: 何日前から
        days_to: 何日後まで
    """
    url = "https://www.investing.com/economic-calendar/"

    params = {
        'importance': 'all',  # 全重要度
        'country': [24, 6, 5],  # 米国、日本、EU
    }

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'X-Requested-With': 'XMLHttpRequest'
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        events = []
        rows = soup.select('tbody.js-economic-table tr')

        for row in rows:
            event = {
                'date': row.select_one('.theDay').get_text(strip=True),
                'time': row.select_one('.time').get_text(strip=True) if row.select_one('.time') else '',
                'country': row.select_one('.flagCur')['title'],
                'event': row.select_one('.event').get_text(strip=True),
                'actual': row.select_one('#actual_*').get_text(strip=True) if row.select_one('[id^="actual_"]') else '',
                'forecast': row.select_one('#forecast_*').get_text(strip=True) if row.select_one('[id^="forecast_"]') else '',
                'previous': row.select_one('#previous_*').get_text(strip=True) if row.select_one('[id^="previous_"]') else '',
            }

            if event['forecast']:  # 予想値があるものだけ
                events.append(event)

        return events

    except Exception as e:
        print(f"Error: {e}")
        return []
```

**注意**:
- ⚠️ スクレイピング対策でブロックされる可能性
- ⚠️ 構造変更で動作しなくなる可能性

---

### 方法2: TradingView スクレイピング

**予想値の取得**: ✅ 可能（ただしJavaScriptでレンダリング）

SeleniumまたはPlaywrightが必要:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def get_tradingview_calendar():
    """TradingViewの経済カレンダーから取得"""
    options = Options()
    options.add_argument('--headless')

    driver = webdriver.Chrome(options=options)

    try:
        driver.get('https://www.tradingview.com/economic-calendar/')

        # ページが読み込まれるのを待つ
        time.sleep(5)

        # データを抽出
        events = []
        rows = driver.find_elements('css selector', '.eventRow')

        for row in rows:
            event = {
                'time': row.find_element('css selector', '.time').text,
                'currency': row.find_element('css selector', '.currency').text,
                'event': row.find_element('css selector', '.event').text,
                'actual': row.find_element('css selector', '.actual').text,
                'forecast': row.find_element('css selector', '.forecast').text,
                'previous': row.find_element('css selector', '.previous').text,
            }

            if event['forecast']:
                events.append(event)

        return events

    finally:
        driver.quit()
```

---

### 方法3: Yahoo Finance (限定的)

**予想値の取得**: ⚠️ 一部の指標のみ

```python
import yfinance as yf

def get_earnings_forecast(symbol: str):
    """企業の決算予想（一部）"""
    ticker = yf.Ticker(symbol)

    # アナリスト予想
    if ticker.info.get('currentPrice') and ticker.info.get('targetHighPrice'):
        return {
            'current': ticker.info['currentPrice'],
            'target_high': ticker.info['targetHighPrice'],
            'target_low': ticker.info['targetLowPrice'],
            'target_mean': ticker.info['targetMeanPrice'],
        }

    return None
```

---

### 方法4: 財務省・FRBの公式発表

**予想値の取得**: ❌ 公式には予想値なし

ただし、ブルームバーグ等が集計したコンセンサスはメディアで発表されます。

---

## 無料の代替案

### A. Reuters Calendar API（無料枠）

RapidAPI経由で利用可能:

```python
import requests

def get_reuters_calendar():
    """Reutersの経済カレンダー"""
    url = "https://reuters-calendar-api.p.rapidapi.com/v1/calendar"

    headers = {
        'X-RapidAPI-Key': 'YOUR_RAPID_API_KEY',
        'X-RapidAPI-Host': 'reuters-calendar-api.p.rapidapi.com'
    }

    response = requests.get(url, headers=headers)
    return response.json()
```

**無料枠**: 500リクエスト/月

---

### B. Economic Calendar API

複数のプロバイダーが提供:

| プロバイダー | 無料枠 | 予想値 |
|-------------|--------|--------|
| Trading Economics | あり | ✅ |
| Finnhub | 60/分 | ✅（一部） |
| Twelve Data | 800/日 | ✅（一部） |
| RapidAPI | 各プロバイダーによる | ✅ |

---

## 推奨構成

### 構成A: Investing.com スクレイピング

```python
# 予想値を含む経済カレンダー
investing_data = get_investing_calendar(days_from=0, days_to=7)

# 実績値をFREDで取得
fred_data = get_fred_data(series_id='GDP')
```

**メリット**:
- 無料
- 詳細な予想値

**デメリット**:
- スクレイピングが必要
- 不安定

---

### 構成B: Trading Economics API（無料枠）

```python
import requests

def get_trading_economics_calendar():
    url = "https://api.tradingeconomics.com/calendar"

    params = {
        'c': 'guest:guest',  # 無料認証
        'f': 'json'
    }

    response = requests.get(url, params=params)
    return response.json()
```

**無料枠**: 1,000リクエスト/月

---

### 構成C: 有料API（本番環境向け）

**Bloomberg API**: 年間数万ドル〜
**Refinitiv**: 年間数万ドル〜

---

## 実装案

予想値を含む経済カレンダースクリプトを作成しますか？

選択肢:
1. **Investing.com スクレイピング**（無料、不安定）
2. **Trading Economics API**（無料枠あり、安定）
3. **RapidAPI経由**（複数プロバイダー）

どれが良いですか？
