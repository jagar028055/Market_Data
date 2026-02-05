# GAS 経済指標取得スクリプト

Google Apps Scriptを使って経済指標を自動収集するスクリプト。

## 特徴

- ✅ **無料** - Googleアカウントがあれば無料
- ✅ **サーバーレス** - サーバー管理不要
- ✅ **自動実行** - 毎日自動でデータ収集
- ✅ **Google Sheets** - データはスプレッドシートに保存
- ✅ **スマホから確認** - スプレッドシートアプリで閲覧可能

## セットアップ

### 1. FRED APIキーを取得（無料）

1. https://fred.stlouisfed.org/ にアクセス
2. 「Register」で無料アカウント作成
3. ログイン後、「My Account」 > 「API Key」でキーを取得

### 2. Google Sheetsを作成

1. Google Sheetsを新規作成
2. 「拡張機能」>「Apps Script」をクリック

### 3. スクリプトを設置

1. `Code.gs`の内容をコピーして貼り付け
2. `FRED_API_KEY`を自分のキーに書き換え
3. 保存（💾マークまたはCtrl+S）

### 4. 実行

1. 関数選択で `fetchEconomicIndicators` を選択
2. 「実行」をクリック
3. 最初の実行時は権限の許可が必要

### 5. シートを確認

スプレッドシートに戻ると「Indicators」シートが追加され、データが保存されています。

## 自動実行設定

毎日自動実行するには：

```javascript
// 毎日9時に実行
createDailyTrigger(9, 0);
```

これを実行すると、毎日AM9:00に自動でデータ収集されます。

## 使用可能な関数

| 関数 | 説明 |
|------|------|
| `fetchEconomicIndicators()` | 経済指標を取得して保存 |
| `getLatestIndicators()` | 最新データをログ表示 |
| `initializeSheet()` | シートを初期化（データ全削除） |
| `createDailyTrigger(hour, min)` | 自動実行トリガー作成 |
| `deleteAllTriggers()` | トリガー全削除 |
| `showInstructions()` | インストール手順を表示 |

## 取得できる経済指標

| 指標 | シリーズID | 頻度 |
|------|-----------|------|
| GDP | GDP | 四半期 |
| 失業率 | UNRATE | 月次 |
| CPI（消費者物価指数） | CPIAUCSL | 月次 |
| 非農業部門雇用者数 | PAYEMS | 月次 |
| 連邦資金金利 | FEDFUNDS | 日次 |
| 鉱工業指数 | INDPRO | 月次 |
| 小売売上 | RSXFS | 月次 |
| 住宅着工件数 | HOUST | 月次 |

## 出力例

シートには以下の形式で保存されます：

| Timestamp | Indicator | Latest Date | Latest Value | Previous Value | Change (%) |
|-----------|-----------|-------------|--------------|----------------|------------|
| 2026-02-05 | GDP | 2025-10-01 | 24563.5 | 24351.2 | +0.87% |
| 2026-02-05 | UNRATE | 2025-12-01 | 4.1 | 4.2 | -2.38% |

## トラブルシューティング

### エラー: "API key is invalid"
- FRED_API_KEYが正しく設定されているか確認

### エラー: "HTTP Error 400"
- APIキーの有効期限が切れている可能性があります
- キーの再取得が必要な場合があります

### トリガーが実行されない
- `ScriptApp.getProjectTriggers()` でトリガーを確認
- タイムゾーンが「Asia/Tokyo」になっているか確認

## カスタマイズ

### 新しい指標を追加

```javascript
const INDICATORS = {
  // 既存の指標...
  '新指標名': 'FREDシリーズID',
};
```

FREDシリーズIDは https://fred.stlouisfed.org/searchresults で検索できます。

### 通知を追加

SlackやEmailへの通知機能も追加可能です。

## ライセンス

個人利用のみ。Google Apps Scriptの利用規約に従ってください。
