const fs = require('fs');

// 1. データ読み込み
const data = JSON.parse(fs.readFileSync('data/reservations.json', 'utf8'));

// 2. 日本時間(JST)での「今日」と「明日」を計算
const now = new Date();
const jstOffset = 9 * 60 * 60 * 1000; // 9時間
const nowJST = new Date(now.getTime() + jstOffset);
const todayStr = nowJST.toISOString().split('T')[0]; // 日本の今日 (2026-04-06)

const tomorrowJST = new Date(nowJST.getTime() + (24 * 60 * 60 * 1000));
const tomorrowStr = tomorrowJST.toISOString().split('T')[0]; // 日本の明日 (2026-04-07)

// 3. 【第1部】明日（確定分）の抽出
const finalSelection = {};
data.forEach(row => {
    if (row.date === tomorrowStr) {
        finalSelection[row.name] = row; // 最新で上書き
    }
});
const targetList = Object.values(finalSelection).filter(r => !r.mode.includes("取消"));

// 4. 【第1部】HTML作成
let htmlContent = `
<div style="font-family: sans-serif; color: #333;">
  <h2 style="color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 5px;">
    【${tomorrowStr}】すみれクラブ利用確定者リスト
  </h2>
  <table border="1" style="border-collapse: collapse; width: 100%; margin-bottom: 30px;">
    <tr style="background-color: #f8f9fa;">
      <th style="padding: 8px;">クラス</th><th style="padding: 8px;">園児名</th>
      <th style="padding: 8px;">区分</th><th style="padding: 8px;">お迎え</th><th style="padding: 8px;">備考</th>
    </tr>`;

targetList.forEach(r => {
    htmlContent += `
    <tr>
      <td style="padding: 8px;">${r.class}</td>
      <td style="padding: 8px; font-weight: bold;">${r.name}</td>
      <td style="padding: 8px;">${r.mode}</td>
      <td style="padding: 8px;">${r.time_frame}</td>
      <td style="padding: 8px; font-size: 0.85em;">${r.memo || ''}</td>
    </tr>`;
});
htmlContent += `</table><p>合計: <strong>${targetList.length}名</strong></p>`;

// 5. 【第2部】本日（全操作ログ）の抽出
let logTable = `
  <h3 style="color: #d93025; margin-top: 40px; border-left: 5px solid #d93025; padding-left: 10px;">
    【事務用：本日の全操作ログ】
  </h3>
  <table border="1" style="border-collapse: collapse; width: 100%; font-size: 0.85em; color: #555;">
    <tr style="background-color: #fce8e6;">
      <th style="padding: 5px;">時刻</th><th style="padding: 5px;">園児名</th>
      <th style="padding: 5px;">操作</th><th style="padding: 5px;">対象日</th><th style="padding: 5px;">備考</th>
    </tr>`;

// 全データから「今日」のタイムスタンプを持つものを探す
data.forEach(r => {
    if (r.timestamp && r.timestamp.includes(todayStr)) {
        const timeOnly = r.timestamp.split('T')[1].substring(0, 5);
        logTable += `
        <tr>
          <td style="padding: 5px; text-align: center;">${timeOnly}</td>
          <td style="padding: 5px;">${r.name}</td>
          <td style="padding: 5px; color: ${r.mode.includes('取消') ? 'red' : 'black'};">${r.mode}</td>
          <td style="padding: 5px;">${r.date}</td>
          <td style="padding: 5px;">${r.memo || ''}</td>
        </tr>`;
    }
});
logTable += `</table></div>`;

// 6. 結合して最終出力
console.log(htmlContent + logTable);
