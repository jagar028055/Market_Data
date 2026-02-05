# GitHub Actions で経済指標を自動収集

GitHub Actions + FRED API で毎日自動的に経済指標を取得・保存します。

## 特徴

- ✅ **完全無料** - GitHub Actions + FRED API
- ✅ **自動実行** - 毎日9:00 JSTに自動実行
- ✅ **バージョン管理** - Gitで履歴管理
- ✅ **通知** - コミット履歴で確認可能
- ✅ **手動実行** - いつでも実行可能

## セットアップ手順

### 1. FRED APIキーを取得（5分）

1. https://fred.stlouisfed.org/ にアクセス
2. 「Register」で無料アカウント作成
3. ログイン後、「My Account」 > 「API Key」でキーを取得

### 2. GitHubリポジトリにSecretを設定

1. このリポジトリの「Settings」 > 「Secrets and variables」 > 「Actions」
2. 「New repository secret」をクリック
3. Name: `FRED_API_KEY`
4. Value: 取得したAPIキー
5. 「Add secret」をクリック

### 3. ワークフローの確認

既に `.github/workflows/economic-indicators.yml` が作成されています。

このファイルは以下のことを行います：
- 毎日9:00 JSTに自動実行
- FRED APIから経済指標を取得
- `market/daily/` にJSONとMarkdownで保存
- 自動コミット＆プッシュ

### 4. 手動実行（テスト）

**方法A: GitHub Web**
1. リポジトリの「Actions」タブ
2. 「Economic Indicators Fetcher」を選択
3. 「Run workflow」 > 「Run workflow」をクリック

**方法B: ローカルでテスト**
```bash
# 環境変数を設定
export FRED_API_KEY="your_api_key_here"

# スクリプト実行
python3 market/fetch_indicators.py
```

## 出力ファイル

実行すると以下のファイルが生成されます：

```
market/daily/
├── indicators_20260205_090000.json  # タイムスタンプ付き
├── indicators_20260205_090000.md
├── latest.json                      # 最新データ（上書き）
└── latest.md
```

## 取得できる経済指標

| 指標 | シリーズID | 説明 |
|------|-----------|------|
| GDP | GDP | 国内総生産 |
| 失業率 | UNRATE | 失業率 |
| CPI | CPIAUCSL | 消費者物価指数 |
| 非農業部門雇用者数 | PAYEMS | 雇用統計 |
| 連邦資金金利 | FEDFUNDS | FF金利 |
| 消費者信頼感 | UMCSENT | ミシガン消費者信頼感指数 |
| 鉱工業指数 | INDPRO | 鉱工業生産指数 |
| 小売売上 | RSXFS | 小売売上高 |
| 住宅着工件数 | HOUST | 住宅着工 |
| マネーサプライM2 | M2SL | マネーサプライ |
| 10年国債金利 | DFII10 | 10年国債金利 |

## 新しい指標を追加

`market/fetch_indicators.py` の `INDICATORS` 辞書に追加：

```python
INDICATORS = {
    'GDP': 'GDP',
    'UNRATE': 'UNRATE',
    'YOUR_NEW_INDICATOR': 'FRED_SERIES_ID',  # これを追加
}
```

FREDシリーズIDは https://fred.stlouisfed.org/searchresults で検索。

## 実行スケジュールの変更

`.github/workflows/economic-indicators.yml` の `cron` を編集：

```yaml
schedule:
  # 毎日9:00 JST
  - cron: '0 0 * * *'
  # 毎週月曜9:00 JSTにする場合
  - cron: '0 0 * * 1'
  # 3時間ごとにする場合
  - cron: '0 */3 * * *'
```

**注意**: cronの時刻はUTCです。JST = UTC + 9時間

## 通知を受け取る（任意）

### 方法1: Email通知

GitHubの通知設定でEmail通知を有効にします。

### 方法2: Slack通知

`.github/workflows/economic-indicators.yml` に追加：

```yaml
      - name: Slack notification
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: '経済指標を更新しました'
          webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
        if: always()
```

## トラブルシューティング

### エラー: "API key is invalid"

- FRED_API_KEY Secretが正しく設定されているか確認
- APIキーが有効期限切れでないか確認

### エラー: "403 Forbidden"

- FRED APIのレート制限を超えていませんか？
- ゲストキー: 120リクエスト/日
- 認証時: 80リクエスト/分

### ワークフローが実行されない

- Actionsタブでワークフローが有効になっているか確認
- cronの設定が正しいか確認

## 他の方法との比較

| 方法 | メリット | デメリット |
|------|----------|------------|
| **GitHub Actions** | 無料、簡単、バージョン管理 | GitHub必須 |
| GAS | スプレッドシートで見やすい | Googleアカウント必須 |
| Python + Cron | 完全ローカル | サーバー必要 |

## 次のステップ

1. FRED APIキーを取得
2. GitHub Secretに登録
3. Actionsで手動実行テスト
4. 自動実行を確認

準備できましたか？
