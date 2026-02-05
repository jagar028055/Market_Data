# 各国経済指標を取得するAPI

FRED APIは米国メインなので、各国のデータを取得するための選択肢をまとめます。

## 各APIのカバレッジ比較

| API | 米国 | 日本 | EU | 中国 | その他 | 無料 | おすすめ度 |
|-----|------|------|----|----|--------|------|------------|
| **FRED** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | - | ⭐ | ✅ | 🥇 米国 |
| **OECD** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | - | ⭐⭐⭐⭐ | ✅ | 🥇 先進国 |
| **World Bank** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | 🥇 世界中 |
| **IMF** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | 🥈 世界中 |
| **BLS** | ⭐⭐⭐⭐⭐ | - | - | - | - | ✅ | - 米国労働統計 |
| **Eurostat** | - | - | ⭐⭐⭐⭐⭐ | - | - | ✅ | 🥇 EU |
| **e-Stat** | - | ⭐⭐⭐⭐⭐ | - | - | - | ✅ | 🥇 日本 |

---

## 1. OECD API ⭐推奨（先進国）

**対象**: 38カ国（米国、日本、EU諸国、豪州、韓国など）

### 特徴
- **無料**
- APIキー不要
- 先進国の経済指標が網羅
- GDP、失業率、CPI、金利など

### エンドポイント
```
https://stats.oecd.org/SDMX-JSON/data/
```

### Python実装例
```python
import requests

def get_oecd_data(country: str, indicator: str):
    """
    OECDデータを取得

    Args:
        country: 国コード（JPN, USA, GBR, FRA, DEU等）
        indicator: 指標（以下参照）
    """
    base_url = "https://stats.oecd.org/SDMX-JSON/data"
    dataset = f"{country}/{indicator}"

    url = f"{base_url}/{dataset}/all"

    response = requests.get(url)
    return response.json()

# 例: 日本のGDP
data = get_oecd_data('JPN', 'QNA')  # 四半期GDP

# 例: 米国の失業率
data = get_oecd_data('USA', 'LFS')  # 労働力統計
```

### 主要国コード
```
JPN - 日本
USA - 米国
GBR - 英国
FRA - フランス
DEU - ドイツ
ITA - イタリア
CAN - カナダ
AUS - オーストラリア
KOR - 韓国
MEX - メキシコ
```

### 主要指標
```
QNA - 四半期GDP
CPI - 消費者物価指数
STLAB - 短期労働統計
MEI - 月次経済指標
LM - 労働市場
```

---

## 2. World Bank API ⭐推奨（世界中）

**対象**: 世界中の国（200カ国以上）

### 特徴
- **完全無料**
- APIキー不要
- 開発途上国も含む全世界をカバー
- GDP、人口、インフレ、失業率など

### エンドポイント
```
https://api.worldbank.org/v2/
```

### Python実装例
```python
import requests

def get_world_bank_data(country: str, indicator: str):
    """
    World Bankデータを取得

    Args:
        country: 国コード（JP, US, GB, FR, DE等）
        indicator: 指標コード
    """
    base_url = "https://api.worldbank.org/v2/country"

    url = f"{base_url}/{country}/indicator/{indicator}"
    params = {
        'format': 'json',
        'per_page': 10,
        'date': '2020:2026'
    }

    response = requests.get(url, params=params)
    return response.json()

# 例: 日本のGDP
data = get_world_bank_data('JP', 'NY.GDP.MKTP.CD')

# 例: 米国の失業率
data = get_world_bank_data('US', 'SL.UEM.TOTL.ZS')

# 例: 中国のインフレ率
data = get_world_bank_data('CN', 'FP.CPI.TOTL.ZG')
```

### 主要指標コード
```
# GDP
NY.GDP.MKTP.CD - GDP（USドル）
NY.GDP.MKTP.KD - GDP（実質）
NY.GDP.MKTP.KD.ZG - GDP成長率

# 労働
SL.UEM.TOTL.ZS - 失業率（%）
SL.TLF.CACT.ZS - 労働参加率（%）
SP.POP.TOTL - 人口

# 物価
FP.CPI.TOTL - CPI（2010=100）
FP.CPI.TOTL.ZG - インフレ率（%）
NY.GDP.DEFL.86.KD.ZG - GDPデフレーター

# 金利
FR.INR.RINR - 政策金利
```

---

## 3. IMF API

**対象**: IMF加盟国（190カ国）

### 特徴
- 無料
- APIキーが必要
- 主な経済指標

### エンドポイント
```
https://dataservices.imf.org/REST/SDMX_JSON.svc/
```

---

## 4. FRED APIの国別カバレッジ

### 米国: ⭐⭐⭐⭐⭐
- 全ての主要指標

### 日本: ⭐
- 一部の指標のみ（円ドルレートなど）
- 日本のGDP・失業率は**取得不可**

### EU: ⭐
- 一部の指標のみ
- ユーロドルレートなど

### その他の国: ⭐
- 為替レート程度

---

## 推奨構成

### 構成A: 国別にAPIを使い分ける

```python
class GlobalIndicators:
    """各国経済指標取得"""

    def get_usa_data(self):
        """米国: FRED API"""
        # GDP、失業率、CPIなど
        pass

    def get_japan_data(self):
        """日本: e-Stat or OECD"""
        # GDP、失業率、CPIなど
        pass

    def get_eu_data(self):
        """EU: OECD or Eurostat"""
        pass

    def get_china_data(self):
        """中国: World Bank or OECD"""
        pass
```

### 構成B: OECD + World Bank で統一

```python
# 先進国: OECD
# 発展途上国: World Bank
```

---

## 実装（多国対応版）

作成しますか？
