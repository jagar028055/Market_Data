# 経済指標API比較

安定したAPI経由で経済指標を取得するサービスの比較。

## 無料で使える経済指標API

### 1. FRED API ⭐推奨

**提供**: セントルイス連銀（公式）

| 項目 | 内容 |
|------|------|
| **コスト** | 無料（登録不要、但しリクエスト数制限あり） |
| **APIキー** | 必要（無料登録） |
| **リクエスト制限** | 120リクエスト/日（ゲスト）、80/分（認証時） |
| **データ** | 米国経済指標（GDP、失業率、CPI、金利など） |
| **安定性** | ⭐⭐⭐⭐⭐ 公式API |
| **取得URL** | `https://api.stlouisfed.org/fred/series/observations` |

**例**:
```bash
# GDPデータ取得
curl "https://api.stlouisfed.org/fred/series/observations?series_id=GDP&api_key=YOUR_KEY&file_type=json&limit=5"
```

**登録**: https://fred.stlouisfed.org/docs/api/api_key.html

---

### 2. Alpha Vantage

| 項目 | 内容 |
|------|------|
| **コスト** | 無料枠あり（25リクエスト/日） |
| **APIキー** | 必要（無料登録） |
| **リクエスト制限** | 25/日（無料）、5/分 |
| **データ** | 株価、為替、経済指標、crypto |
| **安定性** | ⭐⭐⭐⭐ |
| **取得URL** | `https://www.alphavantage.co/query` |

**例**:
```bash
# GDP成長率
curl "https://www.alphavantage.co/query?function=REAL_GDP&interval=quarterly&apikey=YOUR_KEY"
```

**登録**: https://www.alphavantage.co/support/#api-key

---

### 3. Financial Modeling Prep (FMP)

| 項目 | 内容 |
|------|------|
| **コスト** | 無料枠あり（250リクエスト/日） |
| **APIキー** | 必要（無料登録） |
| **リクエスト制限** | 250/日（無料） |
| **データ** | 経済指標、企業財務、株価 |
| **安定性** | ⭐⭐⭐⭐ |
| **取得URL** | `https://financialmodelingprep.com/api/v3/economic` |

**例**:
```bash
# 経済指標一覧
curl "https://financialmodelingprep.com/api/v3/economic?apikey=YOUR_KEY"
```

**登録**: https://site.financialmodelingprep.com/developer/docs

---

### 4. Polygon.io

| 項目 | 内容 |
|------|------|
| **コスト** | 無料枠あり（5リクエスト/分） |
| **APIキー** | 必要（無料登録） |
| **リクエスト制限** | 5/分（無料） |
| **データ** | 株価、経済指標、オプション |
| **安定性** | ⭐⭐⭐⭐ |
| **取得URL** | `https://api.polygon.io` |

**登録**: https://polygon.io/

---

### 5. Bureau of Labor Statistics (BLS) API

| 項目 | 内容 |
|------|------|
| **コスト** | 無料 |
| **APIキー** | 必要（無料登録） |
| **リクエスト制限** | 500/日 |
| **データ** | 雇用、失業、給与、インフレ |
| **安定性** | ⭐⭐⭐⭐⭐ 米国労働省公式 |
| **取得URL** | `https://api.bls.gov/publicAPI/v2/timeseries/data/` |

**例**:
```bash
# 失業率
curl "https://api.bls.gov/publicAPI/v2/timeseries/data/LNS14000000?registrationkey=YOUR_KEY"
```

**登録**: https://www.bls.gov/developers/

---

## 比較表

| API | 無料枠 | 経済指標 | 安定性 | おすすめ度 |
|-----|--------|----------|--------|------------|
| **FRED** | 120/日 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 🥇 |
| **Alpha Vantage** | 25/日 | ⭐⭐⭐ | ⭐⭐⭐⭐ | 🥈 |
| **FMP** | 250/日 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 🥉 |
| **Polygon.io** | 無制限(5/分) | ⭐⭐⭐ | ⭐⭐⭐⭐ | - |
| **BLS** | 500/日 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | - |

---

## 推奨構成

### 構成A: FRED API + GAS

```
FRED API → GAS → Google Sheets → あなたが確認
              ↓
           Slack通知（任意）
```

**メリット**:
- 完全無料
- 公式APIで安定
- GASで自動実行
- スマホで確認可能

**手順**:
1. FRED APIキー取得（5分）
2. Google SheetsでGASスクリプト作成（10分）
3. トリガー設定（毎日自動実行）

---

### 構成B: Python + Cron

```
FRED API → Pythonスクリプト → JSON/CSV保存
```

**メリット**:
- 完全ローカル
- 柔軟な処理可能

**デメリット**:
- Termux環境の問題

---

## GASスクリプト（FRED API版）

既に `market/gas/Code.gs` に作成済みです。

**使用方法**:

1. FRED APIキー取得
   ```
   https://fred.stlouisfed.org/docs/api/api_key.html
   ```

2. Google Sheetsを新規作成

3. 拡張機能 > Apps Script

4. `market/gas/Code.gs` の内容をコピーして貼り付け

5. `FRED_API_KEY` を自分のキーに書き換え

6. `fetchEconomicIndicators()` を実行

---

## curlで直接テスト

```bash
# FRED APIテスト（ゲストキー）
curl "https://api.stlouisfed.org/fred/series/observations?series_id=UNRATE&api_key=guest&file_type=json&limit=5"

# Alpha Vantageテスト（デモキー）
curl "https://www.alphavantage.co/query?function=REAL_GDP&interval=quarterly&apikey=demo"
```

---

## 結論

**FRED API + GAS** が最も簡単で確実です。

理由:
- 公式APIで安定
- 完全無料
- GASでサーバーレス実行
- スマホで確認可能

GASを編集するMCPツールはありませんが、GASスクリプトは既に作成済みなので、コピー＆ペーストするだけで動きます。

試してみますか？
