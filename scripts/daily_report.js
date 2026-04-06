const fs = require('fs');

// 1. データ読み込み
const data = JSON.parse(fs.readFileSync('data/reservations.json', 'utf8'));

// 2. 「明日」の日付を計算
const target = new Date();
target.setDate(target.getDate() + 1);
const targetStr = target.toISOString().split('T')[0];

// 3. データクレンジング（同一人物の最新意思を特定）
const cleanedData = {};
data.forEach(row => {
    if (row.date === targetStr) {
        // 名前をキーにして上書き。timestampが新しいものが最終的に残る
        // （既にソートされている前提ならそのまま、不安ならtimestamp比較を入れる）
        cleanedData[row.name] = row;
    }
});

// 4. 有効な予約（取消以外）を抽出
const finalRecords = Object.values(cleanedData).filter(r => !r.mode.includes("取消"));

// 5. HTML形式で「result05.pdf」風のリストを作成
let htmlContent = `
<h2 style="color: #1a73e8;">【${targetStr}】すみれクラブ利用確定者リスト</h2>
<p>※前日15:30時点の確定データです。これ以降の変更は電話対応となります。</p>
<table border="1" style="border-collapse: collapse; width: 100%; font-family: sans-serif;">
  <tr style="background-color: #f8f9fa;">
    <th style="padding: 10px;">クラス</th>
    <th style="padding: 10px;">園児名</th>
    <th style="padding: 10px;">受付区分</th>
    <th style="padding: 10px;">早朝</th>
    <th style="padding: 10px;">お迎え</th>
    <th style="padding: 10px;">料金</th>
    <th style="padding: 10px;">備考</th>
  </tr>`;

finalRecords.forEach(r => {
    htmlContent += `
    <tr>
      <td style="padding: 8px;">${r.class}</td>
      <td style="padding: 8px; font-weight: bold;">${r.name}</td>
      <td style="padding: 8px;">${r.mode}</td>
      <td style="padding: 8px;">${r.early || '-'}</td>
      <td style="padding: 8px;">${r.time_frame}</td>
      <td style="padding: 8px;">¥${(r.cost || 0).toLocaleString()}</td>
      <td style="padding: 8px; font-size: 0.9em;">${r.memo || ''}</td>
    </tr>`;
});

htmlContent += `</table>
<p style="margin-top: 20px;">合計利用人数: <strong>${finalRecords.length}名</strong></p>
<hr>
<p style="font-size: 12px; color: #666;">このメールはGitHub Actionsにより自動送信されました。</p>`;

// 生成したHTMLを標準出力に流す
console.log(htmlContent);
