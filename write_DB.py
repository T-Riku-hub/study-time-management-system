from notion_client import Client
import os
from dotenv import load_dotenv
from datetime import datetime
import mysql.connector

def write_notion_db(now,total_time):
    load_dotenv()
    notion = Client(auth=os.environ.get("NOTION_TOKEN"))
    database_id = os.environ["NOTION_DATABASE_ID"]

    results = notion.databases.retrieve(database_id=database_id)
    results = notion.data_sources.query(results["data_sources"][0]["id"])
    hour = int(total_time/3600)
    minute = int((total_time%3600)/60)
    sec=   (total_time%3600)%60
    
    try:
        new_page = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Date":{"date":{"start":str(now.strftime("%Y-%m-%d"))}},
                "hour":{"number" : hour},
                "minute":{"number":minute},
                "sec":{"number":sec}
            }
    )
    except Exception as e:
        print(f"追加中にエラーが発生しました: {e}")
    
def write_SQL(now,total_time):
    #接続
    conn = mysql.connector.connect(
    host="192.168.128.174",
    user="pi",
    password="raspberry",
    database="mydatabase"
    )
    #カーソルを取得
    cursor=conn.cursor()
    
    #書き込むデータ
    date_str=str(now.strftime("%Y-%m-%d"))
    hour = int(total_time/3600)
    minute = int((total_time%3600)/60)
    sec=   (total_time%3600)%60
    val = (date_str,hour,minute,sec)
    
    insert_query="""
    INSERT INTO study_time_test (Date, hour, minute, sec) VALUES (%s,%s,%s,%s)
    """
    
    cursor.execute(insert_query,val)
    conn.commit()
    # 接続を閉じる
    cursor.close()
    conn.close()
    
    
if __name__=="__main__":
    now=datetime.now()
    total_time=3281
    write_notion_db(now,total_time)
    print("Notionに書き込み完了")
    write_SQL(now,total_time)
    print("MySQLに書き込み完了")
    