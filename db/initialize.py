from db.connection import get_connection


FACILITIES = [
    ("室內星際飛車", "Indoor Facilities", "正常開放"),
    ("室內旋轉木馬", "Indoor Facilities", "正常開放"),
    ("室內碰碰車", "Indoor Facilities", "正常開放"),
    ("室內咖啡杯", "Indoor Facilities", "正常開放"),
    ("摩天輪", "Outdoor Facilities", "正常開放"),
    ("大怒神", "Outdoor Facilities", "正常開放"),
    ("海盜船", "Outdoor Facilities", "正常開放"),
    ("小火車", "Outdoor Facilities", "正常開放"),
    ("飛天盪鞦韆", "Outdoor Facilities", "正常開放"),
    ("急流泛舟", "Outdoor Facilities", "正常開放"),
    ("商店街", "Public Areas", "正常開放"),
    ("活動廣場", "Public Areas", "正常開放"),
]


def initialize_database():
    """建立設施與公告資料表，並加入預設設施。"""
    connection = get_connection()

    try:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS facilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    設施名稱 TEXT NOT NULL UNIQUE,
                    設施類別 TEXT NOT NULL,
                    設施狀態 TEXT NOT NULL
                )
                """
            )

            connection.executemany(
                """
                INSERT OR IGNORE INTO facilities (
                    設施名稱,
                    設施類別,
                    設施狀態
                )
                VALUES (?, ?, ?)
                """,
                FACILITIES,
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS announcements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    published_at TEXT NOT NULL,
                    publisher TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL
                )
                """
            )
    finally:
        connection.close()
