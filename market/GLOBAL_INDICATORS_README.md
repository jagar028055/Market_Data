# 各国経済指標の取得

## FRED APIの国別カバレッジ

| 国/地域 | カバレッジ | おすすめAPI |
|---------|-----------|-------------|
| **米国** | ⭐⭐⭐⭐⭐ | FRED API |
| **日本** | ⭐ | OECD API |
| **EU圏** | ⭐ | OECD API |
| **中国** | - | World Bank API |
| **その他** | - | World Bank API |

**結論**: FREDは米国専用と考え、各国は別のAPIを使うのが確実です。

---

## 各国向けAPI

### 1. OECD API（先進国）⭐推奨

**対象**: 38カ国（日本、米国、EU、豪州、韓国など）

**取得できる指標**:
- GDP
- 失業率
- CPI
- 生産指数
- 貿易収支

**国コード**:
```
JPN - 日本
USA - 米国
GBR - 英国
FRA - フランス
DEU - ドイツ
ITA - イタリア
EA19 - ユーロ圏（19カ国）
CAN - カナダ
AUS - オーストラリア
KOR - 韓国
MEX - メキシコ
```

### 2. World Bank API（世界中）⭐推奨

**対象**: 200カ国以上

**取得できる指標**:
- GDP
- GDP成長率
- 失業率
- インフレ率
- 人口
- 政策金利

**国コード**:
```
JP - 日本
US - 米国
CN - 中国
GB - 英国
FR - フランス
DE - ドイツ
IN - インド
BR - ブラジル
RU - ロシア
```

---

## 作成したスクリプト

```
market/
├── fetch_global_indicators.py     # 各国経済指標取得
├── INTERNATIONAL_INDICATORS.md    # API比較
└── GLOBAL_INDICATORS_README.md    # このファイル
```

## 使い方

### インストール

```bash
pip install requests
```

### 実行

```bash
# 全国（米国、日本、EU、中国）
python3 market/fetch_global_indicators.py
```

### 出力

```
market/daily/
├── global_indicators_YYYYMMDD_HHMMSS.json
├── global_indicators_YYYYMMDD_HHMMSS.md
├── global_indicators_latest.json
└── global_indicators_latest.md
```

---

## 取得できるデータ

### 米国（FRED API）
- GDP
- 失業率
- CPI
- 連邦資金金利

### 日本（OECD API）
- GDP成長率
- 失業率
- CPI

### EU（OECD API）
- GDP成長率
- 失業率
- CPI

### 中国（World Bank API）
- GDP成長率
- 失業率
- インフレ率

---

## カスタマイズ

### 特定の国だけ取得

```python
fetcher = GlobalIndicatorsFetcher()

# 米国と日本のみ
fetcher.fetch_all(['usa', 'japan'])
```

### 新しい国を追加

```python
def fetch_uk_indicators(self):
    """英国経済指標（OECD）"""
    print("Fetching UK indicators...")

    uk_data = {}
    gdp_data = self.get_oecd_data('GBR', 'QNA')
    if gdp_data:
        uk_data['GDP Growth'] = gdp_data

    return {'source': 'OECD', 'indicators': uk_data}
```

### 新しい指標を追加

```python
# OECDの指標一覧
# https://stats.oecd.org/

# QNA - 四半期GDP
# STLAB - 労働統計
# PRICES_CPI - 消費者物価指数
# MEI - 月次経済指標
# SNA_TABLE1 - 国民計算
```

---

## OECDデータセット一覧

主要なデータセット:

| コード | 説明 | 頻度 |
|--------|------|------|
| QNA | 四半期GDP | 四半期 |
| STLAB | 短期労働統計 | 四半期 |
| PRICES_CPI | 消費者物価指数 | 月次 |
| MEI | 月次経済指標 | 月次 |
| SNA_TABLE1 | 国民計算 | 年次 |
| BSCIC | 業況調査 | 月次 |

詳細: https://stats.oecd.org/

---

## World Bank指標一覧

主要な指標:

| コード | 説明 |
|--------|------|
| NY.GDP.MKTP.CD | GDP（USドル） |
| NY.GDP.MKTP.KD.ZG | GDP成長率（%） |
| SL.UEM.TOTL.ZS | 失業率（%） |
| FP.CPI.TOTL.ZG | インフレ率（%） |
| FR.INR.RINR | 政策金利（%） |
| SP.POP.TOTL | 人口 |
| BN.GSR.FCTL.CD | 経常収支（USドル） |

詳細: https://data.worldbank.org/indicator

---

## トラブルシューティング

### OECDデータが取得できない

- OECDは先進国のデータのみ
- 中国、インドなどはWorld Bankを使用してください

### World Bankでデータがない

- 開発途上国の一部はデータが未公開の場合あり
- 最新のデータが遅れている場合あり

### 日本のGDPの値がおかしい

- OECDのデータは異なる系列の場合あり
- 'QNA'のサブシリーズを確認してください

---

## 推奨構成

### 先進国メインの場合
```
米国 → FRED API
日本・EU → OECD API
```

### 世界中の国が必要な場合
```
全て World Bank API
```

### 混合構成
```
米国: FRED API
先進国: OECD API
発展途上国: World Bank API
```

---

## まとめ

**FREDは米国専用**と考えましょう。

各国の経済指標を取得するには：
- **先進国**: OECD API
- **世界中**: World Bank API

`fetch_global_indicators.py` でこれらを統合して取得できます。
