# FMP (Financial Modeling Prep) API 詳細調査

## 価格プラン

| プラン | 価格 | APIコール/日 | データ範囲 | 時間枠 |
|--------|------|--------------|----------|--------|
| **Basic** | **無料** | **250/日** | 5年 | End of Day |
| Starter | $22/月 | 300/分 | 5年 | Real-time |
| Premium | $59/月 | 750/分 | 30年 | Real-time |
| Ultimate | $149/月 | 3,000/分 | 30年 | Real-time |

**※年払いで最大34%割引**

---

## エコノミックカレンダー API

### エンドポイント
```
https://financialmodelingprep.com/stable/_economic-calendar_
```

### 特徴
- **予想値**: ❓ ドキュメントには明記なし（要確認）
- **実績値**: ❓ 明記なし
- **スケジュール**: 経済イベントの発表予定

### 公式ドキュメントの記述
> "FMP Economic Data Releases Calendar API provides a detailed schedule of **upcoming** economic data releases"

**重要**: "upcoming"（今後の予定）に焦点を当てており、**予想値については言及なし**

---

## 経済指標 API

### エンドポイント
```
https://financialmodelingprep.com/stable/economic-indicators
```

### 特徴
- GDP、失業率、インフレ率などの実績値
- リアルタイム・過去データ
- 予想値についての明記なし

---

## 結論

### FMPで予想値は取得できる？

**公式ドキュメントには予想値についての記載がありません。**

FMPのエコノミックカレンダーは、主に「発表予定スケジュール」に焦点を当てており、Trading Economicsのような「予想 vs 実績」の形式ではない可能性が高い。

---

## FMP vs Trading Economics

| 項目 | FMP | Trading Economics |
|------|-----|-------------------|
| 価格 | 無料（250/日） | $100/月以上 |
| 予想値 | ❓ 不明 | ✅ あり |
| スケジュール | ✅ あり | ✅ あり |
| 実績値 | ✅ あり | ✅ あり |

---

## 推奨される構成

### 1. 予想値が必須な場合

**Trading Economics ($100/月以上)**
- 予想値が確実に取得できる
- 専門の経済カレンダー

**または Investing.com スクレイピング（無料）**
- 予想値あり
- ただし不安定

### 2. 実績値のみで良い場合（無料）

**FMP Basic (250/日)**
- 無料で十分
- エコノミックカレンダー（発表予定）
- 経済指標（実績値）

**または**
- FRED API（米国実績値）
- OECD API（先進国実績値）
- World Bank API（各国実績値）

---

## FMPの無料枠でできること

### ✅ 可能（Basicプラン）
- 経済指標の実績値（GDP、失業率、CPIなど）
- エコノミックカレンダー（発表予定のみ）
- 250リクエスト/日

### ❓ 不明
- 予想値（forecast）が取得できるか不明
- 公式ドキュメントに記載なし

---

## 検証が必要

FMPのエコノミックカレンダーAPIに予想値が含まれているかを確認するには：

1. 無料アカウントを作成
2. 実際にAPIを叩いてレスポンスを確認
3. 予想値フィールドの有無をチェック

---

## 最終的な推奨

### 予想値が必要な場合
- **Trading Economics**: $100/月以上、予想値あり
- **Investing.comスクレイピング**: 無料だが不安定

### 予想値不要の場合（完全無料）
- **FMP Basic**: 250/日、発表予定あり
- **FRED API**: 米国実績値、無制限
- **OECD + World Bank**: 各国実績値、無料

---

**結論**: FMPは予想値については不明点が多く、確実に予想値を取得できるとは言えません。

Trading Economics ($100/月) または完全無料の代替案（FRED + OECD + World Bank）を推奨します。

**Sources:**
- [FMP Pricing Plans](https://site.financialmodelingprep.com/pricing-plans)
- [FMP Economics Data](https://site.financialmodelingprep.com/datasets/economics)
- [FMP Economics Calendar](https://site.financialmodelingprep.com/developer/docs/stable/economics-calendar)
- [FMP Economics Indicators](https://site.financialmodelingprep.com/developer/docs/stable/economics-indicators)
