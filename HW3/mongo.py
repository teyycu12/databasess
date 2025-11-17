import pymongo

# 1. 貼上你剛剛複製的連線字串
# 2. 把 <username> 換成你步驟二設定的「帳號」
# 3. 把 <password> 換成你步驟二設定的「密碼」
CONNECTION_STRING = "mongodb+srv://hw3_user:hw3_userpassword@cluster0.4oe0smy.mongodb.net/?appName=Cluster0"

# 建立連線
client = pymongo.MongoClient(CONNECTION_STRING)

# 指定/建立一個資料庫 (例如叫 "hw3_db")
db = client["hw3_db"]

# 指定/建立一個集合 (collection，類似 SQL 的 table，例如叫 "users")
collection = db["users"]

# 測試連線與寫入 (這就是 insert_one)
try:
    collection.insert_one({"name": "Test User", "status": "OK"})
    print("MongoDB 連線並寫入成功！")
except Exception as e:
    print(f"連線失敗: {e}")