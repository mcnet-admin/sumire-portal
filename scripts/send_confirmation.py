import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email():
    # --- 【直接書き換え設定】 ---
    # 送信元のGmailアドレス
    SENDER_EMAIL = "mcnet-admin@mclean.ed.jp"
    # 先ほど発行した16桁のアプリパスワード（スペースはあってもなくてもOK）
    SENDER_PASS = "bayu gwmz lvcg vffv"
    # --------------------------

    # 1. データの読み込み
    json_path = 'data/reservations.json'
    if not os.path.exists(json_path):
        print("JSONファイルが見つかりません")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"JSON読み込みエラー: {e}")
        return

    if not data:
        print("データが空です")
        return

    # 最新の1件を取得
    latest = data[-1]
    
    # 宛先設定
    to_email = "mcnet-admin@mclean.ed.jp" 

    # 2. モードに応じて文面を切り替え
    mode = latest.get('mode', '新規')
    type_name = latest.get('type', '通常版')
    
    subject = f"【マクリン幼稚園】すみれクラブ予約{mode}受付（{latest['name']}さん）"
    
    body = f"""
{latest['class']} {latest['name']} 様

すみれクラブ（{type_name}）の予約{mode}を以下の通り受け付けました。

--------------------------------------------------
■操作内容：{mode}
■利用希望日：{latest['date']}
■送信日時：{latest['timestamp']}
--------------------------------------------------

※本メールは送信専用です。
変更・取消は締切時刻までにポータル画面よりお手続きください。
"""

    # 3. メール送信処理
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        print(f"送信開始: {SENDER_EMAIL} から {to_email} へ")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASS)
        server.send_message(msg)
        server.quit()
        print(f"メール送信成功: {mode}")
    except Exception as e:
        print(f"メール送信失敗: {e}")

if __name__ == "__main__":
    send_email()