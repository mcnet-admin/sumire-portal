const fs = require('fs');

// 1. データ読み込み
const data = JSON.parse(fs.readFileSync('data/reservations.json', 'utf8'));

// 2. 日付の計算（確定リスト用：明日）
const now = new Date();
const jstOffset = 9 * 60 * 60 * 1000;
const tomorrowJST = new Date(now.getTime() + jstOffset + (24 * 60 * 60 * 1000));
const tomorrowStr = tomorrowJST.toISOString().split('T')[0];

// 3. 【第1部】明日（確定分）の抽出
const finalSelection = {};
data.forEach(row => {
    if (row.date === tomorrowStr) {
        finalSelection[row.name] = row;
    }
});
const targetList = Object.values(finalSelection).filter(r => !r.mode.includes("取消"));

// 4. 【第1部】HTML作成（確定リスト）
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

// 5. 【第2部】最新の操作ログ（直近20件を確実に出す）
let logTable = `
  <h3 style="color: #d93025; margin-top: 40px; border-left: 5px solid #d93025; padding-left: 10px;">
    【事務用：最新の操作ログ履歴（20件）】
  </h3>
  <table border="1" style="border-collapse: collapse; width: 100%; font-size: 0.85em; color: #555;">
    <tr style="background-color: #fce8e6;">
      <th style="padding: 5px;">受付時刻</th><th style="padding: 5px;">園児名</th>
      <th style="padding: 5px;">操作内容</th><th style="padding: 5px;">利用対象日</th>
    </tr>`;

// データを新しい順に並び替えて、直近20件を表示
const recentLogs = [...data].reverse().slice(0, 20);

recentLogs.forEach(r => {
    const displayTime = r.timestamp ? r.timestamp.replace('T', ' ').substring(0, 16) : '不明';
    logTable += `
    <tr>
      <td style="padding: 5px; text-align: center;">${displayTime}</td>
      <td style="padding: 5px;">${r.name}</td>
      <td style="padding: 5px; color: ${r.mode.includes('取消') ? 'red' : 'black'};">${r.mode}</td>
      <td style="padding: 5px;">${r.date}</td>
    </tr>`;
});
logTable += `</table></div>`;

console.log(htmlContent + logTable);
