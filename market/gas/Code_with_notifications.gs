/**
 * Google Apps Script - 経済指標取得（通知機能付き）
 *
 * 機能:
 * - FRED APIから経済指標を取得
 * - Google Sheetsに保存
 * - Slack/Emailで通知
 * - 毎日自動実行可能
 */

// ============= 設定 =============

const FRED_API_KEY = 'YOUR_FRED_API_KEY';
const SLACK_WEBHOOK_URL = 'YOUR_SLACK_WEBHOOK_URL'; // 任意

const SHEET_NAME = 'Indicators';
const ENABLE_SLACK = false; // Slack通知を有効にする場合はtrue
const ENABLE_EMAIL = false; // Email通知を有効にする場合はtrue
const EMAIL_TO = 'your-email@example.com';

// 取得する経済指標
const INDICATORS = {
  'GDP': 'GDP',
  'UNRATE': 'UNRATE',
  'CPIAUCSL': 'CPIAUCSL',
  'PAYEMS': 'PAYEMS',
  'FEDFUNDS': 'FEDFUNDS',
  'UMCSENT': 'UMCSENT',
  'INDPRO': 'INDPRO',
};

// 変化率の閾値（これを超えると通知）
const THRESHOLD_CHANGE = 2.0; // 2%以上の変化で通知

// ============= メイン関数 =============

/**
 * 経済指標を取得して保存 + 通知
 */
function fetchAndNotify() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);

  // シート初期化
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    setupSheet(sheet);
  }

  const timestamp = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy-MM-dd HH:mm:ss');
  let allData = [];
  let significantChanges = [];

  // 各指標を取得
  for (const [name, seriesId] of Object.entries(INDICATORS)) {
    try {
      const data = getFredData(seriesId);

      if (data && data.latest) {
        let changePercent = '';
        let changeNum = 0;

        if (data.previous && data.previous.value && data.latest.value) {
          const latestVal = parseFloat(data.latest.value);
          const prevVal = parseFloat(data.previous.value);
          if (!isNaN(latestVal) && !isNaN(prevVal) && prevVal !== 0) {
            changeNum = (latestVal - prevVal) / prevVal * 100;
            changePercent = changeNum.toFixed(2) + '%';
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

        allData.push({
          name,
          latest: data.latest.value,
          latestDate: data.latest.date,
          previous: data.previous ? data.previous.value : 'N/A',
          changePercent: changePercent || 'N/A',
          changeNum
        });

        // 大きな変化があった場合
        if (Math.abs(changeNum) >= THRESHOLD_CHANGE) {
          significantChanges.push(allData[allData.length - 1]);
        }
      }
    } catch (e) {
      Logger.log(`Error fetching ${name}: ${e}`);
    }
  }

  // 通知送信
  if (ENABLE_SLACK && allData.length > 0) {
    postToSlack(allData, significantChanges);
  }

  if (ENABLE_EMAIL && allData.length > 0) {
    sendEmailNotification(allData, significantChanges);
  }

  Logger.log(`${allData.length}個の指標を取得しました`);
  return allData;
}

/**
 * Slackに通知
 */
function postToSlack(allData, significantChanges) {
  if (!SLACK_WEBHOOK_URL || SLACK_WEBHOOK_URL === 'YOUR_SLACK_WEBHOOK_URL') {
    Logger.log('Slack Webhook URLが設定されていません');
    return;
  }

  let message = '📊 *経済指標更新*\n\n';

  if (significantChanges.length > 0) {
    message += '🚨 *注目すべき変化*\n\n';
    for (const item of significantChanges) {
      const emoji = item.changeNum >= 0 ? ':arrow_up:' : ':arrow_down:';
      message += `${emoji} *${item.name}*: ${item.latest} (${item.changePercent})\n`;
    }
    message += '\n';
  }

  message += '*全指標*\n\n';
  for (const item of allData) {
    message += `• ${item.name}: ${item.latest}`;
    if (item.changePercent !== 'N/A') {
      message += ` (${item.changePercent})`;
    }
    message += '\n';
  }

  const payload = {
    text: message,
    username: 'Economic Bot',
    icon_emoji: ':chart_with_upwards_trend:',
    unfurl_links: false
  };

  try {
    UrlFetchApp.fetch(SLACK_WEBHOOK_URL, {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });
    Logger.log('Slack通知を送信しました');
  } catch (e) {
    Logger.log(`Slack通知エラー: ${e}`);
  }
}

/**
 * Emailで通知
 */
function sendEmailNotification(allData, significantChanges) {
  let htmlBody = `
    <h2>📊 経済指標更新</h2>
    <p>更新時刻: ${Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy-MM-dd HH:mm:ss')}</p>
  `;

  if (significantChanges.length > 0) {
    htmlBody += '<h3>🚨 注目すべき変化</h3><ul>';
    for (const item of significantChanges) {
      const emoji = item.changeNum >= 0 ? '↗' : '↘';
      htmlBody += `<li>${emoji} <strong>${item.name}</strong>: ${item.latest} (${item.changePercent})</li>`;
    }
    htmlBody += '</ul>';
  }

  htmlBody += '<h3>全指標</h3><table border="1" cellpadding="5">';
  htmlBody += '<tr><th>指標</th><th>最新値</th><th>前回値</th><th>変化率</th></tr>';

  for (const item of allData) {
    const changeColor = item.changeNum >= 0 ? 'green' : 'red';
    htmlBody += `
      <tr>
        <td>${item.name}</td>
        <td>${item.latest}</td>
        <td>${item.previous}</td>
        <td style="color: ${changeColor}">${item.changePercent}</td>
      </tr>
    `;
  }

  htmlBody += '</table>';

  try {
    MailApp.sendEmail({
      to: EMAIL_TO,
      subject: '📊 経済指標更新',
      htmlBody: htmlBody
    });
    Logger.log('Email通知を送信しました');
  } catch (e) {
    Logger.log(`Email通知エラー: ${e}`);
  }
}

/**
 * FRED APIからデータを取得
 */
function getFredData(seriesId) {
  const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${seriesId}&api_key=${FRED_API_KEY}&file_type=json&limit=2&sort_order=desc`;

  const response = UrlFetchApp.fetch(url, {
    muteHttpExceptions: true
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

/**
 * シートの初期設定
 */
function setupSheet(sheet) {
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

  sheet.getRange(1, 1, 1, 8)
    .setFontWeight('bold')
    .setBackground('#4285F4')
    .setFontColor('#FFFFFF');

  sheet.setFrozenRows(1);
}

/**
 * テスト: 通知を送信
 */
function testNotification() {
  const testData = [
    { name: 'GDP', latest: '24563.5', previous: '24351.2', changePercent: '+0.87%', changeNum: 0.87 },
    { name: 'UNRATE', latest: '4.1', previous: '4.2', changePercent: '-2.38%', changeNum: -2.38 },
  ];

  const significantChanges = [
    { name: 'UNRATE', latest: '4.1', previous: '4.2', changePercent: '-2.38%', changeNum: -2.38 }
  ];

  if (ENABLE_SLACK) {
    postToSlack(testData, significantChanges);
  }
  if (ENABLE_EMAIL) {
    sendEmailNotification(testData, significantChanges);
  }
}

/**
 * 毎日自動実行トリガー作成
 */
function createDailyTrigger(hour = 9, minute = 0) {
  // 既存トリガー削除
  ScriptApp.getProjectTriggers().forEach(t => {
    if (t.getHandlerFunction() === 'fetchAndNotify') {
      ScriptApp.deleteTrigger(t);
    }
  });

  // 新規作成
  ScriptApp.newTrigger('fetchAndNotify')
    .timeBased()
    .everyDays(1)
    .atHour(hour)
    .nearMinute(minute)
    .create();

  Logger.log(`毎日${hour}時${minute}分に実行するトリガーを作成しました`);
}
