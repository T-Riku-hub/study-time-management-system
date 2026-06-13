import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv
import os

def summarize_daily_study_time(df_base):
    now = datetime.now()
    #インデックスをDatetimeIndex型にする.
    df_base.index = pd.DatetimeIndex(
        pd.to_datetime(df_base["Date"], format="%Y-%m-%d"))
    #同じ日付ごとに勉強時間をまとめたdataframeを作成
    #この時に勉強時間が0の日付が自動で生成される
    df_sum = df_base.resample("D").sum()
    #インデックスをDatetimeIndexから文字列に変換
    df_sum["Date"]=df_sum.index.astype(str)
    #文字列は「%Y-%m-%d」になっているのでそれを m/d の形式に変換
    df_sum["Date"] = df_sum["Date"].str.replace(
        "20.?.?-","",regex=True)
    df_sum["Date"] = df_sum["Date"].str.replace("-","/")
    #その日の合計の勉強時間をインデックスを用いて抽出
    df_today = df_sum.loc[now.strftime("%Y-%m-%d")]
    hour = int(df_today["hour"])
    minute  = int(df_today["min"])
    sec = int(df_today["sec"])
    minute += sec//60
    sec = sec%60
    hour += minute//60
    minute = minute%60
    #その日の合計の勉強時間(str)
    total_time_str = f"{hour}h {minute}m {sec}s"
    #m/d の形式に変換した列をインデックスにする
    df_sum.set_index("Date",inplace=True)
    #過去7日間のデータを取得
    return df_sum[-7:],total_time_str
    
def plot_png_file():
    load_dotenv()
    conn = mysql.connector.connect(
    host=os.environ.get("SQL_SERVER"),
    user="pi",
    password=os.environ.get("SQL_PASSWORD"),
    database="mydatabase"
    )
    #カーソルを取得
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM study_time_test")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    #ベースとなるデータフレームを準備
    df = pd.DataFrame(result,columns=["Date","hour","min","sec"])
    df_sum_reslut,study_time_str = summarize_daily_study_time(df)
    #7日間分の勉強時間のデータを処理
    sum_hour = df_sum_reslut["hour"].sum(numeric_only=True)
    sum_minute = df_sum_reslut["min"].sum(numeric_only=True)
    sum_sec = df_sum_reslut["sec"].sum(numeric_only=True)
    sum_minute += sum_sec//60
    sum_sec = sum_sec%60
    sum_hour += sum_minute//60
    sum_minute = sum_minute%60
    #7日間の合計時間
    sum_study_time=sum_hour+round(sum_minute/60.0,1)
    #csv形式の7日間分の勉強時間のデータ
    csv_str = df_sum_reslut.iloc[:,0:2].to_csv()
    #x軸:日付, y軸 勉強時間 として棒グラフを準備
    plt.bar(df_sum_reslut.index,df_sum_reslut["hour"]
            +round(df_sum_reslut["min"]/60.0,2))
    plt.xlabel("Date")
    plt.ylabel("Hour[h]")
    y_axis=[0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6]
    plt.yticks(y_axis)
    #グラフを保存
    plt.savefig("result.png")
    return study_time_str,csv_str,sum_study_time
    
def plot_bar():
    load_dotenv()
    conn = mysql.connector.connect(
    host=os.environ.get("SQL_SERVER"),
    user="pi",
    password=os.environ.get("SQL_PASSWORD"),
    database="mydatabase"
    )
    #カーソルを取得
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM study_time_test")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    #ベースとなるdataframeを作成
    df = pd.DataFrame(result,columns=["Date","hour","min","sec"])
    df_sum_reslut,study_time_str = summarize_daily_study_time(df)
    #7日間分の勉強時間のデータを処理
    sum_hour = df_sum_reslut["hour"].sum(numeric_only=True)
    sum_minute = df_sum_reslut["min"].sum(numeric_only=True)
    sum_sec = df_sum_reslut["sec"].sum(numeric_only=True)
    sum_minute += sum_sec//60
    sum_sec = sum_sec%60
    sum_hour += sum_minute//60
    sum_minute = sum_minute%60
    #result = f"{sum_hour}:{sum_minute}:{sum_sec}"
    #7日間の合計時間
    sum_study_time=sum_hour+round(sum_minute/60.0,1)
    #csv形式の7日間分の勉強時間のデータ
    csv_str = df_sum_reslut.iloc[:,0:2].to_csv()
    #棒グラフを作成
    plt.bar(df_sum_reslut.index,df_sum_reslut["hour"]+round(df_sum_reslut["min"]/60.0,2))
    plt.xlabel("Date")
    plt.ylabel("Hour[h]")
    y_axis=[0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6]
    plt.yticks(y_axis)
    plt.savefig("result_test.png")
    plt.show()
    return study_time_str,csv_str,sum_study_time
	
if __name__=="__main__":
    print("今日の勉強時間")
    study_time,csv_str,sum_study_time = plot_bar()
    print(study_time)
    print("csv形式の7日間分のデータ")
    print(csv_str)
    print(f"7日間の合計時間:{sum_study_time}h")
    print(f"足らない時間{20-sum_study_time}h")
    print(f"1日で何時間勉強しないといけないのか:{round((20-sum_study_time)/7.0,1)}h")
    
    
