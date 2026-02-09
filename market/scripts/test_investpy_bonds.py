#!/usr/bin/env python3
"""
investpyで利用可能なbond namesを確認するテストスクリプト

GitHub Actionsで実行して、実際に利用可能なbond名を確認するために使用します。
"""

import investpy as inv
import json
from datetime import datetime

print("=" * 80)
print("investpy Bond Names Checker")
print("=" * 80)
print()

# 利用可能な全bond namesを取得
try:
    available_bonds = inv.get_bonds_list()
    print(f"Total available bonds: {len(available_bonds)}")
    print()
except Exception as e:
    print(f"Error getting bonds list: {e}")
    import traceback
    print(traceback.format_exc())
    available_bonds = []

# 各国のbondを確認
countries = {
    'japan': 'Japan',
    'united states': 'United States',
    'usa': 'USA',
    'germany': 'Germany',
    'france': 'France',
    'united kingdom': 'United Kingdom',
    'uk': 'UK',
    'australia': 'Australia'
}

results = {}

for country_key, country_name in countries.items():
    print(f"\n{'=' * 60}")
    print(f"{country_name} ({country_key})")
    print(f"{'=' * 60}")

    # その国のbondを検索
    country_bonds = []
    for bond in available_bonds:
        bond_lower = bond.lower()
        # 国名でフィルタリング
        if country_key.lower() in bond_lower or country_name.lower() in bond_lower:
            country_bonds.append(bond)

    if country_bonds:
        print(f"Found {len(country_bonds)} bonds:")
        sorted_bonds = sorted(country_bonds)
        for bond in sorted_bonds:
            print(f"  - {bond}")
        results[country_key] = sorted_bonds
    else:
        print(f"  No bonds found for {country_name}")
        results[country_key] = []

print()
print("=" * 80)
print("Saving results to JSON...")
print("=" * 80)

# 結果をJSONで保存
output = {
    'timestamp': datetime.now().isoformat(),
    'total_bonds': len(available_bonds),
    'all_bonds': available_bonds,
    'by_country': results
}

import os
os.makedirs('market/data', exist_ok=True)
with open('market/data/available_bonds.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print("Saved to market/data/available_bonds.json")

print()
print("=" * 80)
print("Done!")
print("=" * 80)
