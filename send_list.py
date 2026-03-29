import pandas as pd
import smtplib
import os
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- 設定 ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSPVeVgUBmaKhMR8WXcqA9vNETQdIA1M6K5xvJ6VeILGUqbLM2NR49cmHWVe_vv5OsTrn1Sn-3X8PbB/pub?gid=1888856738&single=true&output=csv"
TO_EMAIL = "mcnet-admin@mclaen.ed.jp"
FONT_URL = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/SubsetOTF/JP/NotoSansJP-Regular.otf"
FONT_PATH = "NotoSansJP-Regular.otf"

def download_font():
    if not os.path.exists(FONT_PATH):
        print("フォントをダウンロード中...")
        response = requests.get(FONT_URL)
        with open(FONT_PATH, 'wb') as f:
            f.write(response.content)
    pdfmetrics.registerFont(TTFont('NotoSans', FONT_PATH))

def create_pdf(df, date_str):
    filename = f"reservation_{date_str.replace('/', '-')}.pdf"
    download_font()
    
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # タイトル
    c.setFont('NotoSans', 18)
    c.drawString(50, height - 50, f"すみれクラブ予約名簿 ({date_str})")
    
    # テーブルヘッダー
    c.setFont('NotoSans', 10)
    y = height - 80
    c.drawString(50, y, "クラス")
    c.drawString(100, y, "園児名")
    c.drawString(250, y, "終了時間")
    c.drawString(350, y, "お迎え")
    c.line(50, y-5, 550, y-5)
    
    y -= 25
    # データ行
    for _, row in df.iterrows():
        if y < 50: # 改ページ処理
            c.showPage()
            y = height - 50
            c.setFont('NotoSans', 10)
        
        c.drawString(50, y, str(row.get('class', '')))
        c.drawString(100, y, str(row.get('name', '')))
        c.drawString(250, y, str(row.get('end time', '')))
        c.drawString(350, y, str(row.get('お迎えの方', ''))) # スプレッドシートの見出しに合わせる
        y -= 20
        
    c.save()
    return filename

def send_email_with_pdf(subject, body, attachment_path):
    from_email = os.environ.get("GMAIL_USER")
    password = os.environ.get("GMAIL_PASS")

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with open(attachment_path, "rb") as f:
        part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
        msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        print("メール送信成功")
    except Exception as e:
        print(f"メール送信失敗: {e}")

def run():
    try:
        df = pd.read_csv(CSV_URL)
        # 列名の改行コードや空白を削除
        df.columns = df.columns.str.strip()
        
        jst_now = datetime.utcnow() + timedelta(hours=9)
        tomorrow = (jst_now + timedelta(days=1)).strftime('%Y-%m-%d') # スプレッドシートの形式に合わせる
        
        # 「date」列から明日の日付を検索
        tomorrow_df = df[df['date'].str.contains(tomorrow, na=False)]
        
        if not tomorrow_df.empty:
            pdf_file = create_pdf(tomorrow_df, tomorrow)
            send_email_with_pdf(
                f"【自動送信】明日 {tomorrow} の予約名簿",
                f"関係者各位\n\nお疲れ様です。明日 {tomorrow} の予約名簿PDFを添付します。\nご確認をお願いいたします。",
                pdf_file
            )
        else:
            print(f"{tomorrow} の予約はありません。メール送信をスキップします。")
    except Exception as e:
        print(f"エラー発生: {e}")

if __name__ == "__main__":
    run()