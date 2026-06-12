import time
import datetime
import csv
import os
import random

def write_csv(now,total_time):
    #もしcsvファイルが存在しなかったら作成して、列名を1行目に書き込む
    if os.path.isfile("result.csv")==False:
        with open("result.csv","w") as f:
            writer = csv.writer(f)
            writer.writerow(["Date","hour","min","sec"])
        
    #書き込むデータの初期化
    date_str=now.strftime("%Y-%m-%d")
    hour = 0
    minute = 0
    sec = 0
    
    #単位秒(s)なので、時間(h),分(m),秒(s)に変換する
    hour = int(total_time/3600)
    minute = int((total_time%3600)/60)
    sec=  (total_time%3600)%60

    #csvファイルに追記する
    with open("result.csv","a",newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date_str,hour,minute,sec])

def write_csv_test(now):
    if os.path.isfile("result_test.csv")==False:
        with open("result_test.csv","w") as f:
            writer = csv.writer(f)
            writer.writerow(["Date","hour","min","sec"])       
    date_str=now.strftime("%Y-%m-%d")
    hour = 0
    minute = 0
    sec = 0
    total_time=random.randint(1000,9999)    
    hour = int(total_time/3600)
    minute = int((total_time%3600)/60)
    sec=   (total_time%3600)%60
    with open("result_test.csv","a",newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date_str,hour,minute,sec])
    
if __name__ == "__main__":
    now = datetime.datetime.now()
    write_csv_test(now)