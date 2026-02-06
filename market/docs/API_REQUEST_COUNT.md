# Trading Economics API リクエスト回数

## 基本ルール

**1回のAPI呼び出し = 1リクエスト**

カレンダーAPI（`/calendar`）は、日付範囲を指定すると、その範囲の全イベントが1回で返ってきます。

---

## 具体例

### 1ヶ月分を取得
```bash
python3 fetch_calendar_range.py --month 2026-02
```
→ **1リクエスト**

### 1年分を取得
```bash
python3 fetch_calendar_range.py --start 2026-01-01 --end 2026-12-31
```
→ **1リクエスト**

### 特定の日付範囲
```bash
python3 fetch_calendar_range.py --days 365
```
→ **1リクエスト**

### 国を指定
```bash
python3 fetch_calendar_range.py --country japan --month 2026-02
```
→ **1リクエスト**（国はパラメータなので）

---

## 複数国を取得する場合

現在のスクリプトは**1国のみ**指定可能です。

複数国を取得する場合は、国ごとにリクエストが必要です：

```python
# 各国ごとにリクエスト
countries = ['united states', 'japan', 'china', 'united kingdom']

for country in countries:
    events = fetch_by_date_range(start, end, country)
    # ↑ これが国の数だけリクエストになる
```

**例**:
- 4カ国（米国、日本、中国、英国）→ **4リクエスト**
- 10カ国 → **10リクエスト**

---

## 無料枠

| プラン | 月間リクエスト数 | 価格 |
|--------|------------------|------|
| **Free** | 1,000 | 無料 |
| Basic | 10,000 | $25/月 |
| Pro | 無制限 | 要問い合わせ |

**1,000リクエスト/月** = 約 **33リクエスト/日**

---

## 使用パターン別

### パターンA: 1国のみ

```bash
# 米国の2026年1年分
python3 fetch_calendar_range.py --country "united states" --start 2026-01-01 --end 2026-12-31
```
→ **1リクエスト**

### パターンB: 主要4カ国

```bash
# 4カ国の2026年2月
# (スクリプトを修正して4カ国ループする場合)
```
→ **4リクエスト**（1カ国×4）

### パターンC: 主要7カ国（G7）

```bash
# G7の2026年通年
```
→ **7リクエスト**

---

## 効率的な使い方

### 方法1: 国指定なし（全国）

```bash
# 全国のイベントを取得
# （ただしデータ量が膨大になる）
```
→ **1リクエスト**で全国取得可能

```python
# 国指定なしで呼び出し
params = {
    'c': f'guest:{api_key}',
    'f': 'json',
    'start': start_date,
    'end': end_date
    # 'country' を指定しない
}
```

### 方法2: フィルタを活用

```bash
# 高重要度のみ
python3 fetch_calendar_range.py --importance high --days 30
```
→ **1リクエスト**（データ量は減る）

---

## 複数国を1リクエストで取得するスクリプト

現在のスクリプトを改良して、**国指定なし**で全国を一括取得できます：

```python
def fetch_all_countries(self, start_date: str, end_date: str) -> Dict:
    """
    全国のイベントを1回のリクエストで取得
    """
    params = {
        'c': f'guest:{self.api_key}',
        'f': 'json',
        'start': start_date,
        'end': end_date
        # 'country' を指定しない → 全国取得
    }

    response = requests.get(self.base_url, params=params)
    data = response.json()

    # 国別にグループ化
    by_country = {}
    for item in data:
        country = item.get('Country', 'Other')
        if country not in by_country:
            by_country[country] = []
        by_country[country].append(item)

    return by_country
```

これなら**1リクエスト**で全ての国のデータが取得できます。

---

## 実際の使用例

### 毎日の運用（1ヶ月先まで）

```bash
# 毎日実行
python3 fetch_calendar_range.py --days 30
```
→ **1回/日 = 30リクエスト/月**
→ 無料枠内（1,000/月）で余裕

### 週次の運用（3ヶ月先まで）

```bash
# 毎週実行
python3 fetch_calendar_range.py --days 90
```
→ **4回/月 = 4リクエスト/月**
→ 全く問題ない

### 月次の運用（1年分）

```bash
# 毎月実行
python3 fetch_calendar_range.py --start 2026-01-01 --end 2026-12-31
```
→ **1回/月 = 12リクエスト/月**
→ 問題なし

---

## まとめ

| 操作 | リクエスト数 |
|------|-------------|
| 1国×1年分 | 1 |
| 1国×1ヶ月分 | 1 |
| 全国×1年分 | 1 |
| 4国×1年分（ループ） | 4 |
| 全国×1年分（一括） | 1 |

**最も効率的**: 国指定なしで全国を一括取得 → **1リクエスト**

無料枠1,000リクエスト/月なら、毎日30日分を取得しても余裕です。

複数国を一括取得するスクリプトを作成しますか？
