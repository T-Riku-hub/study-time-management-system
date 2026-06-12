#gemini api を使うテスト

from google import genai
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
message=""
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt=f"""
    過去7日間の合計の勉強時間は、12.2時間でした。
    目標は7日間で20時間で7.8時間不足しています。
    以下はユーザの過去7日間の勉強時間です。
    Date,hour,min
    05/23,1,105
    05/24,4,113
    05/25,0,0
    05/26,0,0
    05/27,0,0
    05/28,0,0
    05/29,2,90
    以下の条件に従って、データ分析の結果を日本語で簡潔に要約してください。
    1. 3文以内の分析
    2. 計算過程は不要
    3. 箇条書きは使わない
    4. 「今後7日間で1日あたりどれくらい追加で勉強すればよいか」を最後に含める
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    message = response.text
    print(response.text)
except Exception as e:
    print("例外発生")
    response=None
    response="Geminiとの接続が不安定のため、分析が出来ませんでした"
    message = response
    print(e)
finally:
    message +="\n\n"
    message += "今までの記録はこちら:\n"
    message +="https://app.notion.com/p/375b130eba8f80b6a754da026a69f19a?v=375b130eba8f80da9037000c7d871506"

    sender_email = os.environ.get("EMAIL_ADDR")
    receiver_email = sender_email
    app_password = os.environ.get("EMAIL_APP_PASSWORD")

    #メールを作成 
    msg = EmailMessage()
    msg['Subject'] = 'ラズパイ5からのE-mail'
    msg['From'] = sender_email
    msg['To'] = receiver_email    

    msg.set_content(message)
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        # 通信を暗号化
        smtp.starttls()
        # ログイン
        smtp.login(sender_email, app_password)
        # メールを送信
        smtp.send_message(msg)
    print("メールの送信が完了しました")