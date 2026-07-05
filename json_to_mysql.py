import json
import pymysql

# 1. 讀取 JSON 檔案
try:
    with open('input.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)
    # 確保數據為列表格式（若 JSON 只有單一物件則轉為列表）
    if isinstance(posts, dict):
        posts = [posts]
except FileNotFoundError:
    print("錯誤：找不到 input.json 檔案")
    posts = []

if posts:
    # 2. 連線至 MySQL 資料庫
    connection = pymysql.connect(
        host='localhost',         # 請根據實際資料庫主機修改（如 '127.0.0.1'）
        user='username',
        password='password',
        database='blog_db',
        charset='utf8mb4',        # 使用 utf8mb4 支援 Emoji 與完整中文
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            # 3. 建立 post 資料表（如果不存在）
            create_table_query = """
            CREATE TABLE IF NOT EXISTS posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                summary TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(create_table_query)
            
            # 4. 準備插入 SQL 語句
            insert_query = "INSERT INTO posts (title, content, summary) VALUES (%s, %s, %s)"
            
            # 5. 解析 JSON 欄位並整理成元組列表
            data_to_insert = [
                (post.get('title'), post.get('content'), post.get('summary'))
                for post in posts
            ]
            
            # 6. 執行批量插入並提交交易
            cursor.executemany(insert_query, data_to_insert)
            connection.commit()
            print(f"成功安全匯入 {len(data_to_insert)} 筆文章數據！")

    except Exception as e:
        # 發生錯誤時回滾
        connection.rollback()
        print(f"資料庫操作失敗: {e}")
        
    finally:
        # 7. 關閉資料庫連線
        connection.close()
