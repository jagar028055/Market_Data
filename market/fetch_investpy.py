#!/usr/bin/env python3
"""
経済指標取得スクリプト（investpy版）

investpyを使って経済カレンダー（予想値付き）を取得します。

注意:
- investpyは2020年からメンテナンス停止
- Python 3.9以下を推奨
- selenium + chromedriver が必要
- Investing.comの構造変更で動作しない可能性があります

インストール:
    pip install investpy pandas

chromedriverのインストール（Linux）:
    sudo apt-get install chromium-chromedriver

または（Mac）:
    brew install chromedriver
"""

import investpy as inv
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# 経済指標の翻訳辞書
INDICATOR_TRANSLATIONS = {
    # 米国指標
    "JOLTS Job Openings": "JOLTS求人件数",
    "Jobless Claims 4-Week Avg.": "失業保険申請4週間平均",
    "Initial Jobless Claims": "新規失業保険申請件数",
    "Continuing Jobless Claims": "失業保険継続受給件数",
    "Challenger Job Cuts (YoY)": "チャレンジャー解雇通知（前年比）",
    "Challenger Job Cuts": "チャレンジャー解雇通知",
    "ADP Non-Farm Employment Change": "ADP非農業部門雇用者数変化",
    "Non-Farm Payrolls": "非農業部門雇用者数",
    "Unemployment Rate": "失業率",
    "Labor Force Participation Rate": "労働参加率",
    "Average Hourly Earnings (MoM)": "平均時間給（前月比）",
    "Average Hourly Earnings (YoY)": "平均時間給（前年比）",
    "Natural Gas Storage": "天然ガス在庫",
    "EIA Crude Oil Inventories": "EIA原油在庫",
    "Crude Oil Inventories": "原油在庫",
    "Crude Oil Imports": "原油輸入量",
    "Cushing Crude Oil Inventories": "クッシング原油在庫",
    "EIA Refinery Crude Runs (WoW)": "EIA製油所原油処理量（前週比）",
    "EIA Refinery Crude Runs": "EIA製油所原油処理量",
    "EIA Weekly Distillates Stocks": "EIA週間留出油在庫",
    "Distillate Fuel Production": "留出油生産量",
    "Distillate Inventories": "留出油在庫",
    "Gasoline Production": "ガソリン生産量",
    "Gasoline Inventories": "ガソリン在庫",
    "Heating Oil Stockpiles": "暖房油在庫",
    "EIA Weekly Refinery Utilization Rates (WoW)": "EIA週間製油所稼働率（前週比）",
    "Refinery Utilization": "製油所稼働率",
    "API Weekly Crude Oil Stock": "API週間原油在庫",
    "Weekly Jobless Claims": "週間失業保険申請件数",
    "4-Week Bill Auction": "4週間T-bill入札",
    "8-Week Bill Auction": "8週間T-bill入札",
    "13-Week Bill Auction": "13週間T-bill入札",
    "17-Week Bill Auction": "17週間T-bill入札",
    "26-Week Bill Auction": "26週間T-bill入札",
    "52-Week Bill Auction": "52週間T-bill入札",
    "2-Year Note Auction": "2年債入札",
    "3-Year Note Auction": "3年債入札",
    "5-Year Note Auction": "5年債入札",
    "7-Year Note Auction": "7年債入札",
    "10-Year Note Auction": "10年債入札",
    "30-Year Bond Auction": "30年債入札",
    "3-Month LIBOR": "3ヶ月LIBOR",
    "6-Month LIBOR": "6ヶ月LIBOR",
    "Fed Balance Sheet": "FRBバランスシート",
    "Fed's Balance Sheet": "FRBバランスシート",
    "ISM Manufacturing PMI": "ISM製造業PMI",
    "ISM Non-Manufacturing PMI": "ISM非製造業PMI",
    "ISM Manufacturing Employment": "ISM製造業雇用",
    "ISM Non-Manufacturing Employment": "ISM非製造業雇用",
    "ISM Manufacturing New Orders": "ISM製造業新規受注",
    "ISM Non-Manufacturing New Orders": "ISM非製造業新規受注",
    "ISM Manufacturing Prices": "ISM製造業物価",
    "ISM Non-Manufacturing Prices": "ISM非製造業物価",
    "ISM Manufacturing Production": "ISM製造業生産",
    "ISM Non-Manufacturing Business Activity": "ISM非製造業事業活動",
    "ISM Manufacturing Inventories": "ISM製造業在庫",
    "ISM Manufacturing Export Orders": "ISM製造業輸出受注",
    "ISM Manufacturing Imports": "ISM製造業輸入",
    "Richmond Manufacturing Index": "リッチモンド連銀製造業指数",
    "Richmond Services Index": "リッチモンド連銀サービス業指数",
    "Dallas Fed Manufacturing Index": "ダラス連銀製造業指数",
    "Dallas Fed Services Index": "ダラス連銀サービス業指数",
    "Kansas City Fed Manufacturing Index": "カンザスシティ連銀製造業指数",
    "Philadelphia Fed Manufacturing Index": "フィラデルフィア連銀製造業指数",
    "New York Fed Manufacturing Index": "ニューヨーク連銀製造業指数",
    "Chicago PMI": "シカゴ購買部協会指数",
    "Empire State Manufacturing Index": "エンパイアステート製造業指数",
    "S&P Global Manufacturing PMI": "S&Pグローバル製造業PMI",
    "S&P Global Services PMI": "S&Pグローバルサービス業PMI",
    "S&P Global Composite PMI": "S&Pグローバル総合PMI",
    "Markit Manufacturing PMI": "マーキット製造業PMI",
    "Markit Services PMI": "マーキットサービス業PMI",
    "Markit Composite PMI": "マーキット総合PMI",
    "Final Manufacturing PMI": "最終製造業PMI",
    "Fed MBS Purchases": "FRB MBS購入額",
    "Fed Treasury Purchases": "FRB米国債購入額",
    "Reserve Balances with Federal Reserve Banks": "連銀準備預金残高",
    "Total Vehicle Sales": "自動車販売台数",
    "Motor Vehicle Sales": "自動車販売台数",
    "CFTC USD speculative net positions": "CFTCドル投機ネットポジション",
    "CFTC EUR speculative net positions": "CFTCユーロ投機ネットポジション",
    "CFTC JPY speculative net positions": "CFTC円投機ネットポジション",
    "CFTC GBP speculative net positions": "CFTCポンド投機ネットポジション",
    "CFTC CHF speculative net positions": "CFTCフラン投機ネットポジション",
    "CFTC CAD speculative net positions": "CFTCカナダドル投機ネットポジション",
    "CFTC AUD speculative net positions": "CFTC豪ドル投機ネットポジション",
    "CFTC NZD speculative net positions": "CFTC NZドル投機ネットポジション",
    "CFTC Gold speculative net positions": "CFTC金投機ネットポジション",
    "CFTC Silver speculative net positions": "CFTC銀投機ネットポジション",
    "CFTC Copper speculative net positions": "CFTC銅投機ネットポジション",
    "CFTC Crude Oil speculative net positions": "CFTC原油投機ネットポジション",
    "CFTC Natural Gas speculative net positions": "CFTC天然ガス投機ネットポジション",
    "CFTC Corn speculative net positions": "CFTCコーン投機ネットポジション",
    "CFTC Wheat speculative net positions": "CFTC小麦投機ネットポジション",
    "CFTC Soybeans speculative net positions": "CFTC大豆投機ネットポジション",
    "CFTC S&P 500 speculative net positions": "CFTC S&P500投機ネットポジション",
    "CFTC Nasdaq 100 speculative net positions": "CFTCナスダック100投機ネットポジション",
    "CFTC Dow Jones speculative net positions": "CFTCダウ投機ネットポジション",
    "CFTC Russell 2000 speculative net positions": "CFTCラッセル2000投機ネットポジション",
    "CFTC Aluminium speculative net positions": "CFTCアルミニウム投機ネットポジション",
    "Michigan Consumer Sentiment": "ミシガン大学消費者信頼感指数",
    "Michigan Consumer Expectations": "ミシガン大学消費者期待指数",
    "Michigan Current Conditions": "ミシガン大学現状指数",
    "Michigan 1-Year Inflation Expectations": "ミシガン大学1年インフレ期待",
    "Michigan 5-Year Inflation Expectations": "ミシガン大学5年インフレ期待",
    "MBA Mortgage Applications": "MBA住宅ローン申請指数",
    "MBA Purchase Index": "MBA購入指数",
    "U.S. Baker Hughes Oil Rig Count": "ベーカーヒューズ原油掘削リグ数",
    "U.S. Baker Hughes Total Rig Count": "ベーカーヒューズ総リグ数",
    "Baker Hughes Oil Rig Count": "ベーカーヒューズ原油掘削リグ数",
    "Baker Hughes Total Rig Count": "ベーカーヒューズ総リグ数",
    "Consumer Credit": "消費者信用",
    "U.S. President Trump Speaks": "トランプ大統領講演",
    "Fed Chair Powell Speaks": "パウエルFRB議長講演",
    "FOMC Meeting Minutes": "FOMC議事要旨",
    "FOMC Member Bostic Speaks": "FOMCメンバー・ボスティック講演",
    "FOMC Member Waller Speaks": "FOMCメンバー・ウォーラー講演",
    "FOMC Member Goolsbee Speaks": "FOMCメンバー・グールズビー講演",
    "FOMC Member Barr Speaks": "FOMCメンバー・バー講演",
    "FOMC Member Bowman Speaks": "FOMCメンバー・ボウマン講演",
    "FOMC Member Kugler Speaks": "FOMCメンバー・クグラー講演",
    "FOMC Member Musalem Speaks": "FOMCメンバー・ムサレム講演",
    "Fed Governor Jefferson Speaks": "ジェファーソンFRB理事講演",
    "Fed Governor Bowman Speaks": "ボウマンFRB理事講演",
    "Fed Governor Cook Speaks": "クックFRB理事講演",
    "Fed Governor Kugler Speaks": "クグラーFRB理事講演",
    "Non-Farm Payrolls": "非農業部門雇用者数",
    "Unemployment Rate": "失業率",
    "Fed Interest Rate Decision": "FF金利",
    "CPI (YoY)": "CPI（前年比）",
    "Core CPI (YoY)": "コアCPI（前年比）",
    "Retail Sales (MoM)": "小売売上高（前月比）",
    "Core Retail Sales (MoM)": "コア小売売上高（前月比）",
    "GDP (QoQ)": "GDP（前期比）",
    "GDP Annualized": "GDP（年率）",
    "ISM Manufacturing PMI": "ISM製造業PMI",
    "ISM Services PMI": "ISM非製造業PMI",
    "ADP Non-Farm Employment Change": "ADP雇用統計",
    "Initial Jobless Claims": "新規失業保険申請件数",
    "Continuing Jobless Claims": "失業保険継続受給件数",
    "Consumer Confidence": "消費者信頼感指数",
    "Consumer Sentiment": "ミシガン大消費者信頼感指数",
    "Building Permits": "建設許可件数",
    "Housing Starts": "住宅着工戸数",
    "Existing Home Sales (MoM)": "中古住宅販売件数（前月比）",
    "New Home Sales": "新築住宅販売件数",
    "Durable Goods Orders (MoM)": "耐久財受注（前月比）",
    "Core Durable Goods Orders (MoM)": "コア耐久財受注（前月比）",
    "Industrial Production (MoM)": "鉱工業生産指数（前月比）",
    "Capacity Utilization Rate": "設備稼働率",
    "Business Inventories (MoM)": "企業在庫（前月比）",
    "Wholesale Inventories (MoM)": "卸売在庫（前月比）",
    "Trade Balance": "貿易収支",
    "PPI (MoM)": "PPI（前月比）",
    "Core PPI (MoM)": "コアPPI（前月比）",
    "FOMC Meeting Minutes": "FOMC議事要旨",
    "Fed Chair Powell Speaks": "パウエルFRB議長講演",

    # 日本指標
    "Foreign Bonds Buying": "外国債購入",
    "Foreign Investments in Japanese Stocks": "対内株式投資",
    "30-Year JGB Auction": "30年国債入札",
    "10-Year JGB Auction": "10年国債入札",
    "5-Year JGB Auction": "5年国債入札",
    "2-Year JGB Auction": "2年国債入札",
    "Car Registration (YoY)": "新車登録（前年比）",
    "BoJ Interest Rate Decision": "日銀政策金利",
    "BoJ Summary of Opinions": "日銀意見要旨",
    "BoJ Governor Ueda Speaks": "植田日銀総裁講演",
    "BoJ Deputy Governor Himino Speaks": "日冰副総裁講演",
    "BoJ Deputy Governor Uchida Speaks": "内田日銀副総裁講演",
    "Tokyo CPI (YoY)": "東京CPI（前年比）",
    "Household Spending (YoY)": "家計支出（前年比）",
    "Household Spending (MoM)": "家計支出（前月比）",
    "Foreign Reserves (USD)": "外貨準備",
    "Foreign Reserves": "外貨準備高",
    "Leading Index": "先行指数",
    "Coincident Indicator": "一致指数",
    "Coincident Indicator (MoM)": "一致指数（前月比）",
    "Leading Index (MoM)": "先行指数（前月比）",
    "Tertiary Industry Index (MoM)": "第3次産業活動指数（前月比）",
    "Machine Orders (MoM)": "機械受注（前月比）",
    "Machine Tool Orders (YoY)": "工作機械受注（前年比）",
    "CFTC JPY speculative net positions": "CFTC円投機ネットポジション",
    "JGB Yield": "日本国債利回り",
    "Unemployment Rate": "失業率",
    "Jobs/Applications Ratio": "有効求人倍率",
    "Consumer Price Index (YoY)": "CPI（前年比）",
    "Core CPI (YoY)": "コアCPI（前年比）",
    "Core-Core CPI (YoY)": "コアコアCPI（前年比）",
    "GDP (QoQ)": "GDP（前期比）",
    "GDP Annualized": "GDP（年率）",
    "Industrial Production (MoM)": "鉱工業生産指数（前月比）",
    "Retail Sales (YoY)": "小売売上高（前年比）",
    "Retail Sales (MoM)": "小売売上高（前月比）",
    "Trade Balance": "貿易収支",
    "Current Account": "経常収支",
    "Machine Orders (MoM)": "機械受注（前月比）",
    "PPI (MoM)": "企業物価指数（前月比）",
    "Manufacturing PMI": "製造業PMI",
    "Services PMI": "サービス業PMI",
    "Tertiary Industry Index (MoM)": "第3次産業活動指数（前月比）",
    "BoJ Interest Rate Decision": "日銀政策金利",
    "BoJ Summary of Opinions": "日銀意見要旨",
    "BoJ Governor Ueda Speaks": "植田日銀総裁講演",
    "Tokyo CPI (YoY)": "東京CPI（前年比）",

    # 英国・欧州指標
    "S&P Global Construction PMI": "S&Pグローバル建設業PMI",
    "S&P Global Services PMI": "S&Pグローバルサービス業PMI",
    "S&P Global Composite PMI": "S&Pグローバル総合PMI",
    "BoE MPC vote cut": "BoE MPC投票・利下げ",
    "BoE MPC vote hike": "BoE MPC投票・利上げ",
    "BoE MPC vote unchanged": "BoE MPC投票・現状維持",
    "BoE MPC Member Pill Speaks": "BoE MPCメンバー・ピル講演",
    "BoE MPC Member Mann Speaks": "BoE MPCメンバー・マン講演",
    "BoE MPC Member Ramsden Speaks": "BoE MPCメンバー・ラムスデン講演",
    "BoE MPC Member Haskel Speaks": "BoE MPCメンバー・ハスケル講演",
    "BoE MPC Member Greene Speaks": "BoE MPCメンバー・グリーン講演",
    "BoE MPC Member Dhingra Speaks": "BoE MPCメンバー・ディングラ講演",
    "Mortgage Rate (GBP)": "住宅ローン金利（ポンド）",
    "United Kingdom New Passenger Cars Registration": "英国新車登録台数",
    "All Car Sales": "乗用車販売台数",
    "All Truck Sales": "トラック販売台数",
    "Halifax House Price Index (MoM)": "Halifax住宅価格指数（前月比）",
    "Halifax House Price Index (YoY)": "Halifax住宅価格指数（前年比）",
    "Nationwide HPI (MoM)": "Nationwide住宅価格指数（前月比）",
    "Nationwide HPI (YoY)": "Nationwide住宅価格指数（前年比）",
    "RICS House Price Balance": "RICS住宅価格バランス",
    "Rightmove House Price Index (MoM)": "Rightmove住宅価格指数（前月比）",
    "BRC Retail Sales Monitor (YoY)": "BRC小売売上高モニター（前年比）",
    "NIESR GDP Estimate": "NIESR GDP推計",
    "GfK Consumer Confidence": "GfK消費者信頼感",
    "CFTC GBP speculative net positions": "CFTCポンド投機ネットポジション",
    "British Retail Consortium (BRC)": "英国小売業協会(BRC)",
    "RICS House Price Balance": "RICS住宅価格バランス",
    "M4 Money Supply (MoM)": "M4マネーサプライ（前月比）",
    "M4 Money Supply (YoY)": "M4マネーサプライ（前年比）",
    "Mortgage Approvals": "住宅ロード承認件数",
    "Net Lending to Individuals": "個人向け純貸出",
    "CBI Industrial Trends Orders": "CBI産業景況感",
    "CBI Distributive Trades Survey": "CBI流通業調査",
    "Manufacturing PMI": "製造業PMI",
    "Services PMI": "サービス業PMI",
    "Construction PMI": "建設業PMI",
    "GDP (MoM)": "GDP（前月比）",
    "GDP (MoM)": "GDP（前月比）",
    "GDP (YoY)": "GDP（前年比）",
    "CPI (YoY)": "CPI（前年比）",
    "Core CPI (YoY)": "コアCPI（前年比）",
    "HPI (YoY)": "住宅価格指数（前年比）",
    "Claimant Count Change": "失業保険申請件数の変化",
    "Average Earnings Index +Bonus": "平均賃金（ボーナス含む）",
    "Average Earnings Index Excluding Bonus": "平均賃金（ボーナス除く）",
    "Manufacturing PMI": "製造業PMI",
    "Services PMI": "サービス業PMI",
    "Construction PMI": "建設業PMI",
    "Industrial Production (MoM)": "鉱工業生産（前月比）",
    "Trade Balance": "貿易収支",
    "BoE Interest Rate Decision": "BoE政策金利",
    "BoE MPC Meeting Minutes": "BoE議事要旨",
    "BoE Gov Bailey Speaks": "ベイリーBoE総裁講演",
    "Retail Sales (MoM)": "小売売上高（前月比）",
    "Retail Sales (YoY)": "小売売上高（前年比）",
    "ILO Unemployment Rate": "ILO失業率",

    # 一般的な指標
    "PMI": "PMI",
    "Consumer Confidence": "消費者信頼感",
    "Business Confidence": "企業信頼感",
    "Interest Rate Decision": "政策金利",
    "Central Bank Speech": "中銀総裁講演",
    "Inflation Report": "インフレ報告書",
    "Monetary Policy Summary": "金融政策概要",
    "Fiscal Balance": "財政収支",
    "Government Budget Value": "政府財政収支",
    "Government Debt to GDP": "政府債務対GDP比",
    "Current Account": "経常収支",
    "Foreign Direct Investment": "海外直接投資",
}

def translate_indicator(text: str) -> str:
    """指標名を日本語に翻訳（辞書にない場合は英語のまま）"""
    if not text:
        return text

    # 括弧で囲まれた月情報を削除してマッチング
    # 例: "Household Spending (YoY)  (Dec)" -> "Household Spending (YoY)"
    cleaned = text.strip()
    import re
    # 末尾の  (Month) や (Jan) のようなパターンを削除
    cleaned = re.sub(r'\s+\([A-Za-z]{3}\)$', '', cleaned)

    # 翻訳辞書を確認（クリーン後の文字列と元の文字列両方を試す）
    if cleaned in INDICATOR_TRANSLATIONS:
        return INDICATOR_TRANSLATIONS[cleaned]
    if text.strip() in INDICATOR_TRANSLATIONS:
        return INDICATOR_TRANSLATIONS[text.strip()]

    return text

class InvestpyCalendar:
    """investpyを使った経済カレンダー取得"""

    def __init__(self):
        self.results = {}

    def fetch_calendar(
        self,
        country: str = 'united states',
        days_from: int = 0,
        days_to: int = 7,
        time_filter: str = 'time_only',
        time_zone: str = None
    ):
        """
        経済カレンダーを取得

        Args:
            country: 国名（'united states', 'japan', 'china'等）
            days_from: 何日前から
            days_to: 何日後まで
            time_filter: 'time_only' または 'all'
            time_zone: タイムゾーン（例：'GMT +9:00'、Noneなら自動）
        """
        print(f"Fetching economic calendar for {country}...")
        print(f"Period: {days_from} days ago to {days_to} days ahead")
        if time_zone:
            print(f"Timezone: {time_zone}")
        print()

        try:
            calendar_data = inv.economic_calendar(
                countries=[country],
                from_date=self._get_date_str(days_from),
                to_date=self._get_date_str(days_to),
                time_filter=time_filter,
                time_zone=time_zone
            )

            # DataFrameに変換
            df = pd.DataFrame(calendar_data)

            if not df.empty:
                # 必要な列のみ抽出
                columns = ['date', 'time', 'country', 'event', 'importance', 'actual', 'forecast', 'previous', 'te_actual', 'te_forecast', 'te_previous']

                # 利用可能な列のみ使用
                available_columns = [col for col in columns if col in df.columns]

                # 重複排除用辞書 (time, event) -> event_data
                # 同じ時刻とイベント名の場合、より情報量が多い方を優先
                events_dict = {}
                for _, row in df[available_columns].iterrows():
                    event = {
                        'date': row.get('date', ''),
                        'time': row.get('time', ''),
                        'country': row.get('country', ''),
                        'event': translate_indicator(row.get('event', '')),
                        'importance': row.get('importance', ''),
                    }

                    # actual（実績）
                    if 'actual' in available_columns:
                        event['actual'] = row['actual']
                    elif 'te_actual' in available_columns:
                        event['actual'] = row['te_actual']

                    # forecast（予想）
                    if 'forecast' in available_columns:
                        event['forecast'] = row['forecast']
                    elif 'te_forecast' in available_columns:
                        event['forecast'] = row['te_forecast']

                    # previous（前回）
                    if 'previous' in available_columns:
                        event['previous'] = row['previous']
                    elif 'te_previous' in available_columns:
                        event['previous'] = row['te_previous']

                    # 重複排除: 同じ(time, event)の組み合わせの場合、より良いデータを優先
                    key = (event['time'], event['event'])
                    if key not in events_dict:
                        events_dict[key] = event
                    else:
                        # 既存のデータと比較して、より情報量が多い方を採用
                        existing = events_dict[key]
                        # 実績値がある方を優先
                        if event.get('actual') and not existing.get('actual'):
                            events_dict[key] = event
                        # 予想値がある方を優先
                        elif event.get('forecast') and not existing.get('forecast'):
                            events_dict[key] = event
                        # 前回値がある方を優先
                        elif event.get('previous') and not existing.get('previous'):
                            events_dict[key] = event

                events = list(events_dict.values())

                print(f"Found {len(events)} events")

                return {
                    'country': country,
                    'fetch_date': datetime.now().isoformat(),
                    'events': events
                }

            else:
                print("No data found")
                return None

        except Exception as e:
            print(f"Error: {e}")
            print()
            print("Common issues:")
            print("1. investpy not installed: pip install investpy")
            print("2. chromedriver not installed")
            print("3. Investing.com structure changed")
            print("4. Network connectivity issues")
            return None

    def fetch_three_days(self, country: str = 'united states', time_zone: str = None):
        """昨日・今日・明日の予定を取得"""
        data = self.fetch_calendar(
            country=country,
            days_from=-1,
            days_to=1,
            time_filter='time_only',
            time_zone=time_zone
        )

        if data and data['events']:
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
            today = datetime.now().strftime('%d/%m/%Y')
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')

            categorized = {
                'fetch_date': data['fetch_date'],
                'country': country,
                'yesterday': [e for e in data['events'] if e['date'] == yesterday],
                'today': [e for e in data['events'] if e['date'] == today],
                'tomorrow': [e for e in data['events'] if e['date'] == tomorrow]
            }

            return categorized

        return None

    def fetch_major_indicators(self, country: str = 'united states'):
        """主要経済指標を個別に取得"""

        indicators_list = inv.economic.get_events_data(
            country=country,
            event_types=[
                'gdp',
                'inflation',
                'unemployment',
                'interest rate',
                'cpi'
            ],
            from_date=self._get_date_str(-30),
            to_date=self._get_date_str(0)
        )

        print(f"Found {len(indicators_list)} indicators")

        return indicators_list

    def _get_date_str(self, days: int) -> str:
        """日付文字列を取得 (dd/mm/YYYY)"""
        date = datetime.now() + timedelta(days=days)
        return date.strftime('%d/%m/%Y')

    def save_json(self, data: dict, filename: str):
        """JSONで保存"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved to {filename}")

    def save_markdown(self, data: dict, filename: str):
        """Markdownで保存"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        lines = [
            f"# 経済カレンダー（investpy）",
            f"",
            f"**国**: {data.get('country', 'N/A')}",
            f"**取得日時**: {data.get('fetch_date', 'N/A')}",
            f"**データソース**: Investing.com via investpy",
            f"",
        ]

        if 'today' in data:
            lines.extend([
                f"## 今日の予定 ({datetime.now().strftime('%Y-%m-%d')})",
                f"",
                f"| 時刻 | 指標 | 重要度 | 予想 | 前回 | 実績 |",
                f"|------|----|--------|------|------|------|"
            ])

            for event in data['today']:
                lines.append(
                    f"| {event['time']} | {event['event']} | {event['importance']} | "
                    f"{event.get('forecast', 'N/A')} | {event.get('previous', 'N/A')} | "
                    f"{event.get('actual', 'N/A')} |"
                )

            lines.append("")

        if 'tomorrow' in data:
            lines.extend([
                f"## 明日の予定 ({(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')})",
                f"",
                f"| 時刻 | 指標 | 重要度 | 予想 | 前回 |",
                f"|------|----|--------|------|------|------|"
            ])

            for event in data['tomorrow']:
                lines.append(
                    f"| {event['time']} | {event['event']} | {event['importance']} | "
                    f"{event.get('forecast', 'N/A')} | {event.get('previous', 'N/A')} | "
                    f"{event.get('actual', 'N/A')} |"
                )

            lines.append("")

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"Saved to {filename}")


def main():
    """メイン処理"""

    print("=" * 60)
    print("経済指標取得（investpy版）")
    print("=" * 60)
    print()

    # investpyのバージョン確認
    try:
        import investpy
        print(f"investpy version: {investpy.__version__}")
    except ImportError:
        print("investpy not installed!")
        print("Install with: pip install investpy")
        return

    print()

    calendar = InvestpyCalendar()

    # タイムゾーン：東京時間（GMT+9）
    # GitHub ActionsはUTCで動作するため、明示的に指定
    time_zone = 'GMT +9:00'

    # 取得する国・地域
    countries = {
        'japan': 'jp',
        'united kingdom': 'uk',  # 英国（欧州代表）
        'united states': 'us'
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_base = "market/data/economic_calendar"
    json_dir = f"{output_base}/json"
    md_dir = f"{output_base}/markdown"

    all_results = {}

    for country, code in countries.items():
        print(f"\n{'=' * 60}")
        print(f"Processing: {country.upper()}")
        print(f"{'=' * 60}\n")

        data = calendar.fetch_three_days(country=country, time_zone=time_zone)

        if data:
            all_results[code] = data

            # 結果を表示
            print()
            print("=" * 60)
            print(f"{country.upper()} - 結果")
            print("=" * 60)

            if data.get('yesterday'):
                print(f"\n昨日の予定 ({len(data['yesterday'])} 件):")
                for event in data['yesterday'][:5]:  # 最初の5件のみ表示
                    print(f"  {event['time']}: {event['event']}")
                    if event.get('forecast'):
                        print(f"    予想: {event['forecast']}, 前回: {event.get('previous', 'N/A')}")
                if len(data['yesterday']) > 5:
                    print(f"  ... 他 {len(data['yesterday']) - 5} 件")

            if data.get('today'):
                print(f"\n今日の予定 ({len(data['today'])} 件):")
                for event in data['today'][:5]:  # 最初の5件のみ表示
                    print(f"  {event['time']}: {event['event']}")
                    if event.get('forecast'):
                        print(f"    予想: {event['forecast']}, 前回: {event.get('previous', 'N/A')}")
                if len(data['today']) > 5:
                    print(f"  ... 他 {len(data['today']) - 5} 件")

            print()

            if data.get('tomorrow'):
                print(f"\n明日の予定 ({len(data['tomorrow'])} 件):")
                for event in data['tomorrow'][:5]:  # 最初の5件のみ表示
                    print(f"  {event['time']}: {event['event']}")
                    if event.get('forecast'):
                        print(f"    予想: {event['forecast']}, 前回: {event.get('previous', 'N/A')}")
                if len(data['tomorrow']) > 5:
                    print(f"  ... 他 {len(data['tomorrow']) - 5} 件")
        else:
            print(f"Failed to fetch data for {country}")

    # 全データを統合して保存
    if all_results:
        import json
        os.makedirs(json_dir, exist_ok=True)
        os.makedirs(md_dir, exist_ok=True)

        # タイムスタンプ付きJSONファイル
        combined_file = f"{json_dir}/investpy_{timestamp}.json"
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"\n統合データを保存: {combined_file}")

        # 最新版JSONファイル
        latest_file = f"{json_dir}/investpy_latest.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"最新版JSONを保存: {latest_file}")

        # Markdownファイルを作成
        md_lines = [
            f"# 経済カレンダー（investpy）",
            f"",
            f"**取得日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**タイムゾーン**: GMT+9 (東京時間)",
            f"**データソース**: Investing.com via investpy",
            f"",
        ]

        for code, data in all_results.items():
            country_name = data.get('country', code).title()
            md_lines.extend([
                f"## {country_name.upper()}",
                f"",
            ])

            if data.get('yesterday'):
                yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                md_lines.extend([
                    f"### 昨日の予定 ({len(data['yesterday'])}件)",
                    f"",
                    f"| 時刻 | 指標 | 重要度 | 予想 | 前回 | 実績 |",
                    f"|------|----|--------|------|------|------|"
                ])
                for event in data['yesterday']:
                    md_lines.append(
                        f"| {event['time']} | {event['event']} | {event.get('importance', 'N/A')} | "
                        f"{event.get('forecast', 'N/A')} | {event.get('previous', 'N/A')} | "
                        f"{event.get('actual', 'N/A')} |"
                    )
                md_lines.append("")

            if data.get('today'):
                md_lines.extend([
                    f"### 今日の予定 ({len(data['today'])}件)",
                    f"",
                    f"| 時刻 | 指標 | 重要度 | 予想 | 前回 | 実績 |",
                    f"|------|----|--------|------|------|------|"
                ])
                for event in data['today']:
                    md_lines.append(
                        f"| {event['time']} | {event['event']} | {event.get('importance', 'N/A')} | "
                        f"{event.get('forecast', 'N/A')} | {event.get('previous', 'N/A')} | "
                        f"{event.get('actual', 'N/A')} |"
                    )
                md_lines.append("")

            if data.get('tomorrow'):
                md_lines.extend([
                    f"### 明日の予定 ({len(data['tomorrow'])}件)",
                    f"",
                    f"| 時刻 | 指標 | 重要度 | 予想 | 前回 |",
                    f"|------|----|--------|------|------|"
                ])
                for event in data['tomorrow']:
                    md_lines.append(
                        f"| {event['time']} | {event['event']} | {event.get('importance', 'N/A')} | "
                        f"{event.get('forecast', 'N/A')} | {event.get('previous', 'N/A')} |"
                    )
                md_lines.append("")

        # タイムスタンプ付きMarkdownファイル
        md_file = f"{md_dir}/investpy_{timestamp}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))
        print(f"Markdownを保存: {md_file}")

        # 最新版Markdownファイル
        md_latest_file = f"{md_dir}/investpy_latest.md"
        with open(md_latest_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))
        print(f"最新版Markdownを保存: {md_latest_file}")


if __name__ == "__main__":
    main()
