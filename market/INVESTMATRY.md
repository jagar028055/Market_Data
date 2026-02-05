# investpyによる経済指標取得

investpyを使って予想値付きの経済カレンダーを取得します。

## investpyについて

**注意**: investpyは2020年からメンテナンスが停止しています。

| 項目 | 状況 |
|------|------|
| 最終更新 | 2020年 |
| Python対応 | 3.9以下推奨 |
| 依存関係 | selenium, lxml, pandas |
| 予想値 | ✅ 取得可能（構築次第） |

## セットアップ

### 1. Pythonバージョンの確認

```bash
python3 --version
```

**Python 3.10以上の場合**:
- pyenv等でPython 3.9をインストールする必要があります
- または、動作するか試してください

### 2. ライブラリのインストール

```bash
pip install investpy pandas lxml
```

### 3. chromedriverのインストール

**Linux (Termux)**:
```bash
pkg install chromium
# chromiumにchromedriverが含まれています
```

**Ubuntu/Debian**:
```bash
sudo apt-get install chromium-chromedriver
```

**Mac**:
```bash
brew install chromedriver
```

### 4. 動作確認

```bash
python3 -c "import investpy; print(investpy.__version__)"
```

## 使い方

### 今日・明日の予定を取得

```bash
python3 market/fetch_investpy.py
```

出力:
```
market/daily/
├── investpy_YYYYMMDD_HHMMSS.json
├── investpy_YYYYMMDD_HHMMSS.md
├── investpy_latest.json
└── investpy_latest.md
```

## 取得できるデータ

### カレンダー形式

| 項目 | 説明 |
|------|------|
| date | 日付 |
| time | 時刻 |
| country | 国 |
| event | 指標名 |
| importance | 重要度（low/medium/high） |
| actual | 実績値 |
| forecast | 予想値 |
| previous | 前回値 |

### 主要国コード

| 国 | コード |
|----|------|
| 米国 | united states |
| 日本 | japan |
| 中国 | china |
| ユーロ圏 | euro zone |
| ドイツ | germany |
| 英国 | united kingdom |

## カスタマイズ

### 国を変更

```python
# fetch_investpy.py 内を修正
data = calendar.fetch_today_tomorrow(country='japan')
```

### 期間を変更

```python
# 過去7日〜今後7日
data = calendar.fetch_calendar(
    country='united states',
    days_from=-7,
    days_to=7
)
```

## 注意点と制限

### ⚠️ 既知の問題

1. **Python 3.10+で動作しない**
   - Python 3.9を使用してください

2. **chromedriverエラー**
   - chromedriverのパスを通す必要があります
   - 環境変数 `PATH` に追加

3. **Investing.comの構造変更**
   - 2020年以降の変更で動作しない可能性
   - エラーが出たらInvesting.comのHTML構造が変わっている可能性

4. **スクレイピング対策**
   - リクエスト間隔を空ける
   - 複数回試す

### エラー対処法

#### エラー: No module named 'investpy'

```bash
pip install investpy
```

#### エラー: 'chromedriver' executable needs to be in PATH

```bash
# Linux
export PATH=$PATH:/usr/lib/chromium-browser
export PATH=$PATH:/usr/bin/chromedriver

# 実行
python3 market/fetch_investpy.py
```

#### エラー: WebDriverException

seleniumがブラウザを起動できないエラーです。

```python
# ヘッドレスモードで実行するようコードを修正
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)
```

#### Investing.comがブロックする

```python
# ユーザーエージェントを変更
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
```

## トラブルシューティング

### データが取得できない

1. investpyのバージョンを確認
   ```python
   import investpy; print(investpy.__version__)
   ```

2. Investing.comに直接アクセスして確認
   - サイトが稼働しているか
   - カレンダーページが存在するか

3. chromedriverのテスト
   ```bash
   chromedriver --version
   ```

### 予想値が含まれない

- Investing.comのデータ形式が変更された可能性
- `te_forecast` カラムを確認してください
- HTML構造を確認してください

## 代替手段

investpyが動作しない場合の代替案：

1. **FRED API**: 完全無料、実績値のみ
2. **OECD API**: 無料、実績値のみ
3. **Trading Economics API**: $100/月以上、予想値あり

## まとめ

investpyはまだ動作する可能性がありますが、以下の点に注意してください：

1. Python 3.9を使用すること
2. chromedriverを正しく設定すること
3. エラーが出た場合、サイト構造変更の可能性を考慮すること

動作しない場合は、無料のFRED + OECD + World Bankの組み合わせを推奨します。

## ファイル

- `fetch_investpy.py` - メインスクリプト
- `INVESTMATRY.md` - このファイル
