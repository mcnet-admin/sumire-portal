const fs = require('fs');

// 1. データ読み込み
const data = JSON.parse(fs.readFileSync('data/reservations.json', 'utf8'));

// 2. 日本時間での「今日」と「明日」を正確に取得
const nowJST = new Date(Date.now() + ((new Date().getTimezoneOffset() + (9 * 60)) * 60 * 1000));
const todayStr = nowJST.toISOString().split('T')[0]; // 日本の今日

const tomorrowJST = new Date(nowJST.getTime() + (24 * 60 * 60 * 1000));
const tomorrowStr = tomorrowJST.toISOString().split('T')[0]; // 日本の明日

// --- 以下、第1部・第2部のロジック ---

// 3. 【第1部】明日（確定分）の抽出
const finalSelection = {};
data.forEach(row => {
    if (row.date === tomorrowStr) {
        finalSelection[row.name] = row; 
    }
});
const targetList = Object.values(finalSelection).filter(r => !r.mode.includes("取消"));

// 4. 【第1部】HTML作成（略：前回のコードと同じ）
let htmlContent = `...`; // （前回のテーブル作成コードをここに）

// 5. 【第2部】本日（ログ分）の抽出
// 判定を「今日の日付を含むか」に加えて、念のため最新の10件などは必ず出す、などの工夫も可能
let logEntries = data.filter(r => {
    // タイムスタンプが日本の「今日」であることを判定
    return r.timestamp && r.timestamp.includes(todayStr);
});

let logTable = `...`; // （前回のログテーブル作成コードをここに）

// 6. 結合して出力
console.log(htmlContent + logTable);
