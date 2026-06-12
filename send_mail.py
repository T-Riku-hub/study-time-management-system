import smtplib
from email.message import EmailMessage
import os
from datetime import datetime
from dotenv import load_dotenv

#total_time : 計測した勉強時間
#data_str : year/month/dayの形式の文字列
#today_study_time : 勉強した日の合計の勉強時間
#send_file : 送信する画像ファイルのパス
def send_email(total_time,date_str,today_study_time,send_file="result_test.png"):
    load_dotenv()
    sender_email = os.environ.get("EMAIL_ADDR")
    receiver_email = sender_email
    app_password = os.environ.get("EMAIL_APP_PASSWORD")

    #メールを作成 
    msg = EmailMessage()
    msg['Subject'] = 'ラズパイ5からのE-mail'
    msg['From'] = sender_email
    msg['To'] = receiver_email    
    hour = int(total_time/3600)
    minute = int((total_time%3600)/60)
    sec=  (total_time%3600)%60
    msg.set_content(
        f"今回の勉強時間 : {hour}h {minute}m {sec}s\n{date_str}の勉強時間 : {today_study_time}"
        )
    with open(send_file,"rb") as f:
        msg.add_attachment(f.read(), maintype='image', subtype='png', filename=send_file)
        
    # --- smtplibでメールを送信 ---
    # GmailのSMTPサーバーに接続
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        # 通信を暗号化
        smtp.starttls()
        # ログイン
        smtp.login(sender_email, app_password)
        # メールを送信
        smtp.send_message(msg)
    
if __name__=="__main__":
    #テストデータ
    total_time=5679
    now=datetime.now()
    date_str=f"{now.year}/{now.month}/{now.day}"
    today_study_str="4h 7m 40s"
    send_email(total_time=total_time,date_str=date_str,today_study_time=today_study_str)
    print("Email 送信完了")
