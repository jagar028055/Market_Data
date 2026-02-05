# 経済指標取得の代替案

## 1. Google Apps Script (GAS) ⭐推奨

### メリット
- サーバーレス、無料
- Google Sheetsに自動保存
- 時間トリガーで自動実行可能
- 外部API呼び出し簡単
- スマホからも確認可能

### データソース
- **FRED API** - 米国経済指標（公式、安定）
- **Alpha Vantage** - 無料枠あり
- **Finnhub** - 無料枠あり
- **TradingView API** - 非公式

---

## 2. GAS + Google Sheets 実装例

### スクリプト（Code.gs）

```javascript
// FRED APIを使った経済指標取得
const FRED_API_KEY = 'YOUR_API_KEY'; // https://fred.stlouisfed.org/docs/api/api_key.html

const INDICATORS = {
  'GDP': 'GDP',           // GDP
  'UNRATE': 'UNRATE',     // 失業率
  'CPIAUCSL': 'CPIAUCSL', // CPI
  'PAYEMS': 'PAYEMS',     // 非農業部門雇用者数
  'FEDFUNDS': 'FEDFUNDS', // FF金利
};

function getFredData(seriesId) {
  const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${seriesId}&api_key=${FRED_API_KEY}&file_type=json&limit=2&sort_order=desc`;

  const response = UrlFetchApp.fetch(url);
  const data = JSON.parse(response.getContentText());

  if (data.observations && data.observations.length > 0) {
    return {
      latest: data.observations[0],
      previous: data.observations[1] || null
    };
  }
  return null;
}

function fetchEconomicIndicators() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Indicators');
  const timestamp = new Date();

  // ヘッダー（初回のみ）
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(['Timestamp', 'Indicator', 'Latest Date', 'Latest Value', 'Previous Date', 'Previous Value']);
  }

  // 各指標を取得
  for (const [name, seriesId] of Object.entries(INDICATORS)) {
    const data = getFredData(seriesId);

    if (data && data.latest) {
      sheet.appendRow([
        timestamp,
        name,
        data.latest.date,
        data.latest.value,
        data.previous ? data.previous.date : '',
        data.previous ? data.previous.value : ''
      ]);
    }
  }

  Logger.log('経済指標を取得・保存しました');
}

// 毎日AM9:00に自動実行
function createTrigger() {
  ScriptApp.newTrigger('fetchEconomicIndicators')
    .timeBased()
    .everyDays(1)
    .atHour(9)
    .create();
}
```

### セットアップ手順

1. **Google Sheets作成**
   - 新規スプレッドシート作成
   - シート名を「Indicators」に変更

2. **Apps Script追加**
   - 拡張機能 > Apps Script
   - 上記コードを貼り付け
   - `FRED_API_KEY`を自分のキーに置き換え

3. **実行**
   - `fetchEconomicIndicators`関数を実行
   - シートにデータが保存される

4. **自動実行設定**
   - `createTrigger`関数を実行
   - 毎日自動でデータ収集

---

## 3. Alpha Vantage API版（GAS）

```javascript
// Alpha Vantage - より多くの経済指標
const AV_API_KEY = 'YOUR_API_KEY'; // https://www.alphavantage.co/support/#api-key

function getAlphaVantageEconomic() {
  const url = `https://www.alphavantage.co/query?function=REAL_GDP&interval=quarterly&apikey=${AV_API_KEY}`;

  const response = UrlFetchApp.fetch(url);
  const data = JSON.parse(response.getContentText());

  // データ処理...
  Logger.log(JSON.stringify(data, null, 2));
}
```

---

## 4. GAS + Slack通知版

```javascript
// 経済指標が発表されたらSlackに通知
const SLACK_WEBHOOK_URL = 'YOUR_WEBHOOK_URL';

function postToSlack(message) {
  const payload = {
    text: message,
    username: 'Economic Bot',
    icon_emoji: ':chart_with_upwards_trend:'
  };

  UrlFetchApp.fetch(SLACK_WEBHOOK_URL, {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload)
  });
}

function fetchAndNotify() {
  // 指標取得
  const indicators = fetchEconomicIndicators();

  // Slackに通知
  let message = '📊 経済指標更新\n\n';

  for (const [name, data] of Object.entries(indicators)) {
    message += `• ${name}: ${data.latest.value} (前回: ${data.previous.value})\n`;
  }

  postToSlack(message);
}
```

---

## 5. その他の方法

### A. n8n（セルフホスト automation）
```
経済指標API → スプレッドシート/DB保存 → Slack通知
```
- ノーコードでワークフロー構築
- DockerでTermuxでも動作可能

### B. Python + FastAPI + 定期実行
```python
# TermuxでAPIサーバーを立てて
# systemd/cronで定期実行
```

### C. Google Colab
- 無料のJupyter環境
- スクリプト実行のみ（自動化には別途工夫必要）

### D. Cloudflare Workers
- 無料のサーバーレス
- Cron Triggersで定期実行

---

## まとめ: おすすめ順

1. **GAS + FRED API** - 最も簡単で確実
2. **GAS + Alpha Vantage** - より多くの指標
3. **n8n** - 自由度高、視覚的
4. **Python + Termux** - 環境整備必要

どの方法で作成しますか？
