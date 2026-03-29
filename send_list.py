import pandas as pd
from datetime import datetime, timedelta

# 公開したCSVのURL
CSV_URL = "ここにステップ1のURLを貼る"

def run():
    df = pd.read_csv(CSV_URL)
    # 明日の日付 (例: "3/30")
    tomorrow = (datetime.now() + timedelta(hours=9, days=1)).strftime('%-m/%-d')
    
    # 明日の分を抽出
    tomorrow_df = df[df['希望日'].str.contains(tomorrow, na=False)]
    
    if not tomorrow_df.empty:
        print(f"【明日の予約リスト: {tomorrow}】")
        print(tomorrow_df[['園児名', '預かり終了時間', 'お迎えの方']].to_string(index=False))
        # ここにメール送信ロジックを追加可能
    else:
        print(f"{tomorrow}の予約はありません。")

if __name__ == "__main__":
    run()