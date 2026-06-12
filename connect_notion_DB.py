from notion_client import Client
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
notion = Client(auth=os.environ.get("NOTION_TOKEN"))
database_id = os.environ["NOTION_DATABASE_ID"]

results = notion.databases.retrieve(database_id=database_id)
results = notion.data_sources.query(results["data_sources"][0]["id"])

'''
print("Date : hour : minute : sec : sum")
for page in results["results"]:
    date=page["properties"]["Date"]["date"]["start"]
    hour=page["properties"]["hour"]["number"]
    minute=page["properties"]["minute"]["number"]
    sec=page["properties"]["sec"]["number"]
    sum=page["properties"]["sum"]["formula"]["number"]
    print(f"{date} : {hour} : {minute} : {sec} {sum}")
'''


now = datetime.now()
try:
    new_page = notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Date":{
                "date":{
                    "start":str(now.strftime("%Y-%m-%d"))
                }
            },
            "hour":{
                "number" : 3
            },
            "minute":{
                "number":56
            },
            "sec":{
                "number":12
            }
        }
    )
except Exception as e:
    print(f"追加中にエラーが発生しました: {e}")