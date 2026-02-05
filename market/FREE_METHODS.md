# 無料で経済指標を取得する方法

予想値付きの経済カレンダーを無料で取得する現実的な方法。

## 結論：完全無料で可能な構成

| 方法 | 予想値 | 実績値 | 安定性 | おすすめ度 |
|------|--------|--------|--------|------------|
| **FRED API** | ❌ | ✅ | ⭐⭐⭐⭐⭐ | 🥇 米国実績値 |
| **Investing.comスクレイピング** | ✅ | ✅ | ⚠️ | 🥈 予想値要る場合 |
| **FMP API** | ⚠️ 一部 | ✅ | ⭐⭐⭐⭐ | 🥉 |
| **Alpha Vantage** | ⚠️ 一部 | ✅ | ⭐⭐⭐⭐ | - |
| **BLS API** | ❌ | ✅ | ⭐⭐⭐⭐⭐ | - 労働統計のみ |

---

## 1. FRED API（推奨）⭐⭐⭐⭐⭐

### 特徴
- **完全無料**
- 公式API（セントルイス連銀）
- 米国経済指標の実績値
- 予想値は**なし**

### 取得できるデータ
- GDP、失業率、CPI、金利など
- 月次、四半期、年次データ

### メリット
- 完全無料でリクエスト数制限も緩い
- 公式データで信頼性高い
- 安定して稼働

### デメリット
- 予想値が取得できない
- 米国データのみ（日本・EUなどは別API必要）

### 実装
スクリプトは既に作成済み：
```bash
python3 market/fetch_indicators_yfinance.py  # yfinance + FRED
```

---

## 2. Investing.com スクレイピング ⭐⭐⭐

### 特徴
- **完全無料**
- 予想値あり
- ただしスクレイピング対策でブロックされる可能性

### 取得できるデータ
- 経済カレンダー（予想、実績、前回）
- 全世界の経済指標

### メリット
- 予想値が取得できる
- 全国のデータが取得可能

### デメリット
- **不安定**（構造変更で動作しなくなる）
- ブロックされる可能性
- サーバー負荷が高い

### 実装例

```python
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def get_investing_calendar(days_from: int = 0, days_to: int = 1):
    """
    Investing.comから経済カレンダーをスクレイピング

    注意: スクレイピング対策でブロックされる可能性があります
    """
    url = "https://www.investing.com/economic-calendar/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.investing.com/',
    }

    try:
        # JavaScriptでレンダリングされるので、実際にはSeleniumが必要
        # これは簡易版の例
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        events = []
        # 実際のパースロジックはサイトの構造に依存
        rows = soup.select('tbody.js-economic-table tr')

        for row in rows:
            event = {
                'date': row.select_one('.theDay').get_text(strip=True),
                'time': row.select_one('.time').get_text(strip=True) if row.select_one('.time') else '',
                'country': row.select_one('.flagCur')['title'],
                'event': row.select_one('.event').get_text(strip=True),
                'actual': row.select_one('[id^="actual_"]').get_text(strip=True) if row.select_one('[id^="actual_"]') else '',
                'forecast': row.select_one('[id^="forecast_"]').get_text(strip=True) if row.select_one('[id^="forecast_"]') else '',
                'previous': row.select_one('[id^="previous_"]').get_text(strip=True) if row.select_one('[id^="previous_"]') else '',
            }

            # 予想値があるものだけ
            if event['forecast']:
                events.append(event)

        return events

    except Exception as e:
        print(f"Error: {e}")
        return []
```

### 回避策
- リクエスト間隔を空ける（1秒以上）
- 複数のUser-Agentをローテーション
- プロキシを使用
- **Selenium/PlaybirdでJavaScriptを実行**

---

## 3. FMP API（Financial Modeling Prep）⭐⭐⭐⭐

### 特徴
- 無料枠：**250リクエスト/日**
- 予想値：一部の指標で利用可能
- 米国経済指標

### 無料枠
- 250リクエスト/日
- APIキー登録が必要（無料）

### 取得できるデータ
- GDP、失業率、CPIなど
- 企業決算の予想値

### エンドポイント
```
https://financialmodelingprep.com/api/v3/economic_indicator_list
https://financialmodelingprep.com/api/v3/historical-economic-indicator/GDP
```

### 実装例

```python
import requests
import os

FMP_API_KEY = os.getenv('FMP_API_KEY', 'demo')  # 無料登録で取得

def get_fmp_economic_indicators():
    """FMPから経済指標を取得"""
    url = f"https://financialmodelingprep.com/api/v3/economic_indicator_list"

    params = {
        'apikey': FMP_API_KEY
    }

    response = requests.get(url, params=params)
    return response.json()

def get_fmp_indicator(indicator: str):
    """特定の指標の時系列データを取得"""
    url = f"https://financialmodelingprep.com/api/v3/historical-economic-indicator/{indicator}"

    params = {
        'apikey': FMP_API_KEY
    }

    response = requests.get(url, params=params)
    return response.json()
```

---

## 4. Alpha Vantage ⭐⭐⭐

### 特徴
- 無料枠：**25リクエスト/日**
- 一部の指標で予想値あり

### 無料枠
- 25リクエスト/日（かなり制限きつい）
- 5リクエスト/分

### 取得できるデータ
- GDP（四半期）
- 実質GDP
- 連邦資金金利

### エンドポイント
```
https://www.alphavantage.co/query?function=REAL_GDP&interval=quarterly&apikey=YOUR_KEY
```

---

## 5. BLS API（労働統計専門）⭐⭐⭐⭐

### 特徴
- **完全無料**
- 米国労働省公式
- 労働統計のみ（失業率、雇用統計など）

### 取得できるデータ
- 失業率
- 非農業部門雇用者数
- 給与・労働時間
- 労働生産性

### メリット
- 完全無料
- 500リクエスト/日
- リリースカレンダーあり

### デメリット
- 労働統計のみ
- 米国データのみ

---

## おすすめ構成

### 構成A: 実績値のみで良い場合

```
FRED API（米国）
+ OECD API（先進国）
+ World Bank API（世界各国）
```

**コスト**: 完全無料
**予想値**: なし
**実績値**: あり

---

### 構成B: 予想値が必要な場合

```
Investing.com スクレイピング
（回避策を実装）
```

**コスト**: 無料
**予想値**: あり
**安定性**: ⚠️

**回処策**:
1. 複数のIPアドレスをローテーション
2. リクエスト間隔を長くする（数秒）
3. ユーザーエージェントを変更
4. エラー時はリトライ

---

### 構成C: ハイブリッド

```
実績値: FRED API（安定）
予想値: Investing.com スクレイピング（補助）
```

---

## 実装：無料版統合スクリプト

既存のスクリプトを組み合わせて実現可能です。

```bash
# 米国実績値（FRED）
python3 market/fetch_indicators_yfinance.py

# 各国実績値（OECD + World Bank）
python3 market/fetch_global_indicators.py

# 予想値付きカレンダー（Investing.comスクレイピング - 要実装）
```

---

## まとめ

| 目的 | 推奨方法 | コスト |
|------|----------|--------|
| **米国実績値** | FRED API | 無料 |
| **各国実績値** | OECD + World Bank | 無料 |
| **予想値（必須）** | Investing.comスクレイピング | 無料（不安定） |
| **予想値（安定版）** | FMP API | 無料枠内 |

**最も現実的**:
- 実績値は FRED + OECD + World Bank
- 予想値が必要なら FMP API（無料枠250/日）

Investing.comスクレイピングの完全版スクリプトを作成しますか？
