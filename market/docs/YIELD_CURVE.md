# Government Bond Yield Curves / 国債イールドカーブ

## 概要

このスクリプトはinvestpyを使用して、世界各国の国債利回りデータを取得し、イールドカープを可視化します。

## 対象国

- 日本
- 米国 (United States)
- ドイツ (Germany)
- フランス (France)
- イギリス (United Kingdom)
- オーストラリア (Australia)

## 期間構成

各国のイールドカーブは以下の期間で構成されています：

### 日本
- 2年、5年、10年、20年、30年物国債

### 米国
- 2年、5年、10年、30年物財務省証券

### ドイツ
- 2年、5年、10年、30年物国債

### フランス
- 2年、5年、10年物国債

### イギリス
- 2年、5年、10年物ギルト

### オーストラリア
- 2年、5年、10年物国債

## 出力内容

スクリプトは以下のファイルを生成します：

1. **JSONファイル**
   - `yield_curve_YYYYMMDD_HHMMSS.json` - タイムスタンプ付きデータ
   - `yield_curve_latest.json` - 最新のデータ

2. **Markdownレポート**
   - `yield_curve_YYYYMMDD_HMSS.md` - タイムスタンプ付きレポート
   - `yield_curve_latest.md` - 最新のレポート

3. **グラフ**
   - `yield_curves.png` - 各国のイールドカープ（利回り曲線）
   - `yield_changes.png` - 前日比のヒストグラム

## データフォーマット

### JSON出力例

```json
{
  "japan": {
    "country": "japan",
    "country_name": "Japan",
    "country_name_ja": "日本",
    "fetch_date": "2026-02-06T...",
    "bonds": [
      {
        "name": "Japan 2Y",
        "period": 2,
        "yield": 0.5,
        "previous_yield": 0.48,
        "change": 0.02,
        "change_pct": 4.17
      }
    ]
  }
}
```

## GitHub Actionsによる自動実行

このスクリプトはGitHub Actionsで毎日自動実行されます。

### 実行スケジュール

- 毎日 9:00 JST (00:00 UTC) に実行
- 手動実行も可能（GitHubのActionsタブから）

### ワークフローファイル

`.github/workflows/yield_curve.yml` で設定されています。

## 手動実行方法

### 前提条件

- Python 3.9以下（investpyはPython 3.10以上で動作しない可能性があります）
- Chrome と ChromeDriver

### インストール

```bash
pip install investpy pandas matplotlib numpy
```

### 実行

```bash
python market/scripts/fetch_yield_curve.py
```

## 出力データの場所

すべての出力ファイルは `market/data/` ディレクトリに保存されます。

## 注意点

1. **investpyのメンテナンス状況**: investpyは2020年からメンテナンスが停止しており、Investing.comの構造変更により動作しなくなる可能性があります。

2. **Pythonバージョン**: Python 3.9以下での使用を推奨します。

3. **Seleniumの依存関係**: investpyは内部でSeleniumを使用しているため、ChromeとChromeDriverが必要です。

4. **ネットワーク接続**: データ取得にはインターネット接続が必要です。

## イールドカープの見方

イールドカープは、横軸に残存期間（満期までの期間）、縦軸に利回りをとったグラフです。

- **順イールド（正常なカープ）**: 長期金利 > 短期金利（通常の状態）
- **逆イールド（逆イールドカープ）**: 短期金利 > 長期金利（景気後退の兆候とされる）

## 前日比ヒストグラム

前日比のヒストグラムでは、各期間の利回りの前日からの変化を表示します：

- 緑のバー: 利回り上昇（プラス）
- 赤のバー: 利回り低下（マイナス）

## ライセンス

このプロジェクトの一部として作成されています。
