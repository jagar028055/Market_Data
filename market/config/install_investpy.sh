#!/bin/bash
# investpyの手動インストールスクリプト

echo "investpyのインストールを開始します..."
echo ""

# Pythonパッケージのインストール先をユーザーディレクトリに設定
export PYTHONUSER=$(echo ~/)
export PATH=$PATH:~/usr/local/bin

echo "Step 1: pipでパッケージをインストール..."
python3 -m pip install --user investpy pandas lxml 2>&1 | tail -20

echo ""
echo "Step 2: インストール確認..."
python3 -c "import investpy; print('investpy version:', investpy.__version__)" 2>&1 || echo "investpy not installed"

echo ""
echo "Step 3: chromedriverを確認..."
which chromium || echo "chromium not found - install with: pkg install chromium"

echo ""
echo "完了！"
echo ""
echo "次のコマンドで実行できます："
echo "cd /data/data/com.termux/files/home/knowledge"
echo "python3 market/fetch_investpy.py"
