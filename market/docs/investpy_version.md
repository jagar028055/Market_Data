# investpy による経済指標取得

## investpy について

investpyはPythonの金融データライブラリですが、**現在はメンテナンスが停止**しています（2020年頃から更新なし）。

### 注意点

- ⚠️ **最終更新**: 2020年
- ⚠️ **依存関係**: selenium + chromedriverが必要
- ⚠️ **Pythonバージョン**: Python 3.9以下推奨（Python 3.12では問題あり）
- ⚠️ **スクレイピング**: Investing.comの構造変更で動作しない可能性

### より良い代替案

| ライブラリ | メンテナンス | 安定性 | おすすめ度 |
|------------|--------------|--------|------------|
| **yfinance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 🥇 |
| **pandas_datareader** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 🥈 |
| investpy | ❌ | ⚠️ | ❌ |

## 推奨: yfinance + pandas_datareader

これらを組み合わせることで、investpyと同等以上のデータが取得できます。

### 実装（yfinance版）
