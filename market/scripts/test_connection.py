#!/usr/bin/env python3
"""ネット接続テスト"""

import urllib.request
import sys

def test_connection(url: str, name: str):
    """URLへの接続をテスト"""
    print(f"Testing {name}...")
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.status
            content_length = len(response.read())
            print(f"  ✓ Status: {status}, Content: {content_length} bytes")
            return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Network Connection Test")
    print("=" * 60)
    print()

    sites = [
        ("https://httpbin.org/get", "HTTP Test"),
        ("https://www.google.com", "Google"),
        ("https://www.investing.com", "Investing.com"),
        ("https://www.tradingview.com", "TradingView"),
        ("https://api.stlouisfed.org/fred/series/observations?series_id=GDP&api_key=guest&limit=1", "FRED API"),
    ]

    results = []
    for url, name in sites:
        results.append((name, test_connection(url, name)))
        print()

    print("=" * 60)
    print("Summary:")
    print("=" * 60)
    for name, success in results:
        status = "✓ OK" if success else "✗ FAIL"
        print(f"{status} - {name}")

    # 成功したサイトの数を返す
    success_count = sum(1 for _, s in results if s)
    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
