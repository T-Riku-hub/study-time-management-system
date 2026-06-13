import smtplib
from email.message import EmailMessage
import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai
#total_time : 計測した勉強時間(s)
#data_str : year/month/dayの形式の文字列
#today_study_time_str : 勉強した日の合計の勉強時間(文字列)
#csv_data : 7日間のデータをcsv形式にしたもの
#sum_study_time : 7日間の合計の勉強時間(h)
#send_file : 送信する画像ファイルのパス

def analyze_ai(sum_study_time,csv_data):
    load_dotenv()
    ai_message=""
    try:
        GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt=f"""
        ・過去7日間の合計の勉強時間は、{sum_study_time}時間でした。
        ・目標の勉強時間はは7日間で20時間で{20-sum_study_time}時間不足しています。
        以下はcsv形式のユーザの過去7日間の勉強時間です。
        {csv_data}
        最初の箇条書きの内容の後を含めた、データ分析の結果を以下の条件に従って日本語で簡潔に要約してください。
        1. 3文以内の分析結果
        2. 計算過程は不要
        3. 箇条書きは使わない
        4. 分析結果を踏まえた2文以内のアドバイス
        """
        response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
        )
        ai_message += response.text
    except Exception as e:
        ai_message += "エラーが発生したため、分析が出来ませんでした"
        print(e)  
    finally:
        return ai_message
    
def send_email(total_time, date_str, today_study_time_str, csv_data, sum_study_time, send_file="result_test.png"):
    load_dotenv()
    hour = int(total_time/3600)
    minute = int((total_time%3600)/60)
    sec=  (total_time%3600)%60
    message =f"今回の勉強時間 : {hour}h {minute}m {sec}s\n{date_str}の合計の勉強時間 : {today_study_time_str}\n"
    message += "\n---AIによる分析---\n"
    
    message +=analyze_ai(sum_study_time,csv_data)  
    message += "\n----------------\n\n"
    message += "今までの記録はこちら:\n"
    message +="https://app.notion.com/p/375b130eba8f80b6a754da026a69f19a?v=375b130eba8f80da9037000c7d871506"
    message +="\n"
    sender_email = os.environ.get("EMAIL_ADDR")
    receiver_email = sender_email
    app_password = os.environ.get("EMAIL_APP_PASSWORD")

    #メールを作成 
    msg = EmailMessage()
    msg['Subject'] = 'ラズパイ5からのE-mail'
    msg['From'] = sender_email
    msg['To'] = receiver_email    
    
    msg.set_content(message)
    #メールに画像を添付
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
    total_time=7777
    now=datetime.now()
    date_str=f"{now.year}/{now.month}/{now.day}"
    today_study_time_str="4h 7m 40s"
    csv_data="""
    Date,hour,min
        06/07,0,0
        06/08,0,0
        06/09,2,126
        06/10,0,0
        06/11,0,0
        06/12,0,0
        06/13,4,18
    """
    sum_study_time=8.4
    send_email(
    total_time=total_time,
    date_str=date_str,
    today_study_time_str=today_study_time_str,
    csv_data=csv_data,
    sum_study_time=sum_study_time)
    print("Email 送信完了")
