/**
 * Google Apps Script - 経済指標取得
 *
 * セットアップ:
 * 1. Google Sheetsを新規作成
 * 2. 拡張機能 > Apps Script を開く
 * 3. このコードを貼り付け
 * 4. FRED_API_KEYを自分のキーに変更
 * 5. fetchEconomicIndicators()を実行
 */

// ============= 設定 =============

const FRED_API_KEY = 'YOUR_API_KEY_HERE'; // https://fred.stlouisfed.org/docs/api/api_key.html で無料取得

const SHEET_NAME = 'Indicators';

// 取得する経済指標（FREDシリーズID）
const INDICATORS = {
  'GDP': 'GDP',                    // GDP（四半期）
  'UNRATE': 'UNRATE',              // 失業率（月次）
  'CPIAUCSL': 'CPIAUCSL',          // CPI（月次）
  'PAYEMS': 'PAYEMS',              // 非農業部門雇用者数（月次）
  'FEDFUNDS': 'FEDFUNDS',          // 連邦資金金利
  'UMCSENT': 'UMCSENT',            // ミシガン消費者信頼感指数
  'INDPRO': 'INDPRO',              // 鉱工業指数
  'RSXFS': 'RSXFS',                // 小売売上
  'HOUST': 'HOUST',                // 住宅着工件数
  'AAA10Y': 'AAA10Y',              // 米国10年国債金利
};

// ============= メイン関数 =============

/**
 * メイン: 全経済指標を取得してシートに保存
 */
function fetchEconomicIndicators() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);

  // シートが存在しない場合は作成
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    // ヘッダー行
    sheet.appendRow([
      'Timestamp',
      'Indicator',
      'Series ID',
      'Latest Date',
      'Latest Value',
      'Previous Date',
      'Previous Value',
      'Change (%)'
    ]);

    // ヘッダー書式設定
    sheet.getRange(1, 1, 1, 8).setFontWeight('bold').setBackground('#4285F4').setFontColor('#FFFFFF');
    sheet.setFrozenRows(1);
  }

  const timestamp = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy-MM-dd HH:mm:ss');
  let rowIndex = sheet.getLastRow() + 1;
  let results = [];

  // 各指標を取得
  for (const [name, seriesId] of Object.entries(INDICATORS)) {
    try {
      const data = getFredData(seriesId);

      if (data && data.latest) {
        // 変化率を計算
        let changePercent = '';
        if (data.previous && data.previous.value && data.latest.value) {
          const latestVal = parseFloat(data.latest.value);
          const prevVal = parseFloat(data.previous.value);
          if (!isNaN(latestVal) && !isNaN(prevVal) && prevVal !== 0) {
            changePercent = ((latestVal - prevVal) / prevVal * 100).toFixed(2) + '%';
          }
        }

        // シートに追加
        sheet.appendRow([
          timestamp,
          name,
          seriesId,
          data.latest.date,
          data.latest.value,
          data.previous ? data.previous.date : '',
          data.previous ? data.previous.value : '',
          changePercent
        ]);

        results.push({
          indicator: name,
          latest: `${data.latest.value} (${data.latest.date})`,
          previous: data.previous ? `${data.previous.value} (${data.previous.date})` : 'N/A',
          change: changePercent || 'N/A'
        });

        Logger.log(`${name}: ${data.latest.value}`);
      }
    } catch (e) {
      Logger.log(`Error fetching ${name}: ${e}`);
    }
  }

  // 最終更新時刻を記録
  sheet.getRange('A1').setValue('Last Update: ' + timestamp);

  // サマリーをログ出力
  Logger.log('='.repeat(50));
  Logger.log('経済指標取得完了');
  Logger.log('='.repeat(50));
  results.forEach(r => {
    Logger.log(`${r.indicator}: ${r.latest} | 前回: ${r.previous} | 変化: ${r.change}`);
  });

  return results;
}

/**
 * FRED APIからデータを取得
 * @param {string} seriesId - FREDシリーズID
 * @return {object} {latest, previous}
 */
function getFredData(seriesId) {
  const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${seriesId}&api_key=${FRED_API_KEY}&file_type=json&limit=2&sort_order=desc`;

  const response = UrlFetchApp.fetch(url, {
    muteHttpExceptions: true,
    headers: {
      'Accept': 'application/json'
    }
  });

  if (response.getResponseCode() !== 200) {
    Logger.log(`HTTP Error ${response.getResponseCode()} for ${seriesId}`);
    return null;
  }

  const data = JSON.parse(response.getContentText());

  if (data.observations && data.observations.length > 0) {
    return {
      latest: data.observations[0],
      previous: data.observations.length > 1 ? data.observations[1] : null
    };
  }

  return null;
}

// ============= 便利な関数 =============

/**
 * 最新データのみを取得（ログ用）
 */
function getLatestIndicators() {
  const results = fetchEconomicIndicators();

  console.log('\n📊 最新経済指標\n');
  results.forEach(r => {
    console.log(`${r.indicator}: ${r.latest}`);
    if (r.previous !== 'N/A') {
      console.log(`  前回: ${r.previous} (${r.change})`);
    }
    console.log('');
  });
}

/**
 * シートを初期化（データをクリア）
 */
function initializeSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);

  if (sheet) {
    sheet.clear();
    sheet.appendRow([
      'Timestamp',
      'Indicator',
      'Series ID',
      'Latest Date',
      'Latest Value',
      'Previous Date',
      'Previous Value',
      'Change (%)'
    ]);
    sheet.getRange(1, 1, 1, 8).setFontWeight('bold').setBackground('#4285F4').setFontColor('#FFFFFF');
    sheet.setFrozenRows(1);
  }

  Logger.log('シートを初期化しました');
}

/**
 * 毎日自動実行するトリガーを作成
 * @param {number} hour - 実行時刻（0-23）
 * @param {number} minute - 実行分（0-59）
 */
function createDailyTrigger(hour = 9, minute = 0) {
  // 既存のトリガーを削除
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(t => {
    if (t.getHandlerFunction() === 'fetchEconomicIndicators') {
      ScriptApp.deleteTrigger(t);
    }
  });

  // 新しいトリガーを作成
  ScriptApp.newTrigger('fetchEconomicIndicators')
    .timeBased()
    .everyDays(1)
    .atHour(hour)
    .nearMinute(minute)
    .create();

  Logger.log(`毎日${hour}時${minute}分に実行するトリガーを作成しました`);
}

/**
 * トリガーを全て削除
 */
function deleteAllTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(t => ScriptApp.deleteTrigger(t));
  Logger.log(`${triggers.length}個のトリガーを削除しました`);
}

/**
 * インストール手順を表示
 */
function showInstructions() {
  const instructions = `
===========================================
経済指標取得スクリプト - インストール手順
===========================================

【手順1: FRED APIキーの取得】

1. https://fred.stlouisfed.org/ にアクセス
2. 無料アカウントを作成
3. アカウント設定から API Key を取得
4. このスクリプトの FRED_API_KEY を書き換え

【手順2: 実行】

1. fetchEconomicIndicators() を実行
2. スプレッドシートにデータが保存される

【手順3: 自動実行（任意）】

1. createDailyTrigger(9, 0) を実行
2. 毎日9時に自動実行される

【トリガー確認・削除】

- 確認: ScriptApp.getProjectTriggers()
- 削除: deleteAllTriggers()

===========================================
  `;

  Logger.log(instructions);
  console.log(instructions);
}
