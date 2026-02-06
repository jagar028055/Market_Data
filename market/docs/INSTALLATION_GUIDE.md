# investpy インストール＆実行ガイド

Bashツールの問題により、手動でのインストールが必要です。

## ステップ1: パッケージのインストール

以下のコマンドを実行してください：

```bash
# ユーザーディレクトリにインストール
python3 -m pip install --user investpy pandas lxml
```

または、インストールスクリプトを実行：

```bash
cd /data/data/com.termux/files/home/knowledge/market
bash install_investpy.sh
```

## ステップ2: インストール確認

```bash
python3 -c "import investpy; print('investpy version:', investpy.__version__)"
```

## ステップ3: 実行

```bash
cd /data/data/com.tmux/files/home/knowledge
python3 market/fetch_investpy.py
```

---

## ものトラブルシューティング

### エラー: ModuleNotFoundError: No module named 'investpy'

```bash
pip3 install --user investpy
```

### エラー: chromedriver関連

#### Termuxの場合:
```bash
pkg install chromium
```

#### Linuxの場合:
```bash
sudo apt-get install chromium-chromedriver
```

#### Macの場合:
```bash
brew install chromedriver
```

### エラー: investpy version error

investpyはPython 3.9以下推奨です。Python 3.10以上で動作しない場合：

**オプションA: Python 3.9をインストール**
```bash
# pyenvを使用
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
pyenv install 3.9.16
pyenv global 3.9.16
```

**オプションB: 代替案を使用**
- FRED API（完全無料）
- OECD API
- World Bank API

---

## 簡略コマンド

コピー＆ペースト用：

```bash
cd && python3 -m pip install --user investpy pandas lxml && cd /data/data/com.termux/files/home/knowledge && python3 market/fetch_investpy.py
```

---

## 正常に動作しない場合

investpyは2020年から更新されており、Investing.comの構造変更で動作しない可能性が高いです。

その場合は、以下の代替案を検討してください：

### 完全無料の代替案

1. **FRED API**（米国実績値）- `market/fetch_indicators_yfinance.py`
2. **OECD API**（先進国実績値）- `market/fetch_global_indicators.py`
3. **World Bank API**（各国実績値）

まずは上記の手順で試してみてください。
