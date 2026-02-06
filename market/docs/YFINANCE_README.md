# yfinance による経済指標取得

investpyはメンテナンス停止のため、**yfinance + pandas-datareader** を使用します。

## investpy との比較

| 項目 | investpy | yfinance + pandas-datareader |
|------|----------|------------------------------|
| **メンテナンス** | ❌ 2020年で停止 | ✅ 継続中 |
| **Python 3.12対応** | ❌ 非対応 | ✅ 対応 |
| **依存関係** | selenium + chromedriver | HTTPリクエストのみ |
| **データソース** | Investing.com | Yahoo Finance + FRED |
| **経済指標** | ○ | ✅ FREDで公式データ |
| **株価データ** | ○ | ✅ Yahoo Finance |
| **コモディティ** | ○ | ✅ Yahoo Finance |
| **安定性** | ⚠️ | ✅ |

## セットアップ

### 1. ライブラリのインストール

```bash
pip install yfinance pandas-datareader pandas
```

または:

```bash
pip install -r market/requirements_yfinance.txt
```

### 2. スクリプトの実行

```bash
cd /data/data/com.termux/files/home/knowledge
python3 market/fetch_indicators_yfinance.py
```

## 取得できるデータ

### FRED経済指標
- GDP
- 失業率
- CPI（消費者物価指数）
- 非農業部門雇用者数
- 連邦資金金利
- マネーサプライM2
- 鉱工業指数
- 消費者信頼感
- 住宅着工件数

### 米国国債金利
- 10年国債
- 5年国債
- 13週国債
- 30年国債

### 市場指数
- S&P 500
- ダウ Jones
- NASDAQ
- VIX

### コモディティ
- 金
- 銀
- WTI原油
- 天然ガス

## 出力ファイル

```
market/daily/
├── indicators_YYYYMMDD_HHMMSS.json
├── indicators_YYYYMMDD_HHMMSS.md
├── latest.json  （最新データ、上書き）
└── latest.md
```

## 自動実行設定

### Termux + cron

```bash
# cronの編集
crontab -e

# 毎日9時に実行
0 9 * * * cd /data/data/com.termux/files/home/knowledge && /data/data/com.termux/files/usr/bin/python3 market/fetch_indicators_yfinance.py >> /data/data/com.termux/files/home/knowledge/market/logs/fetch.log 2>&1
```

### GitHub Actions

`.github/workflows/economic-indicators.yml` は既に作成済みですが、スクリプト名を変更する場合：

```yaml
      - name: Fetch economic indicators
        run: |
          python market/fetch_indicators_yfinance.py
```

## investpyを使いたい場合

どうしてもinvestpyを使いたい場合の注意点：

1. **Python 3.9以下**が必要
   ```bash
   pyenv install 3.9.16
   pyenv local 3.9.16
   ```

2. **chromedriver**のインストールが必要
   ```bash
   # Linux
   sudo apt-get install chromium-chromedriver

   # Mac
   brew install chromedriver
   ```

3. **investpy**のインストール
   ```bash
   pip install investpy
   ```

4. **ただし動作保証なし**
   - Investing.comの構造変更で動作しない可能性大
   - メンテナンスが停止しているためバグ修正されない

## サンプルコード（investpy版）

参考までにinvestpyを使う場合のコード：

```python
from investpy import economic_calendar
from datetime import datetime

# 今日の経済指標を取得
today = datetime.now().strftime('%d/%m/%Y')
calendar = economic_calendar.EconomicCalendar(
    time_filter='time_only',
    time_filter='all'
)

data = calendar.get_economic_calendar(
    countries=['united states', 'japan'],
    from_date='01/01/2026',
    to_date=today
)

print(data)
```

**注意**: このコードは動作しない可能性が高いです。

## 推奨構成

### 構成A: ローカル実行
```
yfinance + pandas-datareader → Pythonスクリプト → JSON/Markdown保存
```

### 構成B: GitHub Actions
```
yfinance + pandas-datareader → GitHub Actions → Gitコミット
```

### 構成C: GAS
```
FRED API → Google Apps Script → スプレッドシート
```

## トラブルシューティング

### エラー: "No module named 'yfinance'"

```bash
pip install yfinance pandas-datareader
```

### エラー: "HTTP Error 401"

- Yahoo Financeのレート制限に達しました
- 数分待ってから再試行してください

### エラー: "FRED data not available"

- インターネット接続を確認してください
- FRED APIは認証なしで利用可能です

## 結論

**yfinance + pandas-datareader** を推奨します。

理由：
- メンテナンスが継続されている
- Python 3.12対応
- 依存関係がシンプル
- 複数のデータソース（Yahoo Finance + FRED）

investpyは使用せず、この構成で運用することを強く推奨します。
