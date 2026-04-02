import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os

def send_confirmation():
    # --- 1. 設定（GitHub ActionsのSecretsから読み込む設定） ---
    # MAIL_ADDRESS という箱から読み込む（なければデフォルトのアドレス）
    SENDER_EMAIL = os.environ.get('MAIL_ADDRESS', 'mcnet-admin@mclean.ed.jp')
    
    # MAIL_PASSWORD という箱から読み込む（これで wgda... が自動で入ります）
    SENDER_PASS = os.environ.get('MAIL_PASSWORD')

    # --- 2. データの読み込み ---
    try:
        with open('data/reservations.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not data:
            print("送信対象のデータがありません。")
            return
        
        # 最新の1件を取得
        latest = data[-1]
    except Exception as e:
        print(f"JSON読み込みエラー: {e}")
        return

    # --- 3. 宛先（保護者2名分）の整理 ---
    e01 = str(latest.get('parent_email01', "")).strip()
    e02 = str(latest.get('parent_email02', "")).strip()
    
    # 送信リストの作成
    to_list = []
    if e01 and e01.lower() != "nan": to_list.append(e01)
    if e02 and e02.lower() != "nan": to_list.append(e02)
    
    # 宛先が空の場合のバックアップ
    if not to_list:
        to_addr = "mcnet-admin@mclean.ed.jp"
        print("警告: 保護者メールアドレスが空のため、管理者に送信します。")
    else:
        # カンマ区切りの文字列にする（例: "user1@gmail.com, user2@gmail.com"）
        to_addr = ", ".join(to_list)

    # --- 4. メールの内容構築 ---
    subject = f"【すみれクラブ】予約受付完了のお知らせ（{latest['name']}様）"
    
    # 予約タイプによって件名や文面を変える
    if latest['type'] == "平日版":
        type_label = "【平日版（通常保育日）】"
    else:
        type_label = "【休日・長期休暇版】"

    body = f"""
{latest['name']} 様

すみれクラブの予約を以下の内容で受け付けました。

-----------------------------------------
{type_label}
■ お子様名：{latest['class']} {latest['name']}
■ 申込区分：{latest['mode']}
■ 利用日　：{latest['date']}
■ 受付日時：{latest['timestamp']}
-----------------------------------------

※内容に誤りがある場合や、急なキャンセルは園までお電話ください。
※このメールは送信専用です。

マクリン幼稚園 すみれクラブ事務局
"""

    # --- 5. 送信処理 ---
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_addr
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # SMTPサーバーへの接続（Gmail用）
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASS)
            # send_message の引数にはリスト形式で渡すのが確実
            server.send_message(msg)
            
        print(f"✅ メール送信成功: {to_addr}")
        
    except Exception as e:
        print(f"❌ メール送信失敗: {e}")

if __name__ == "__main__":
    send_confirmation()