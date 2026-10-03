import sqlite3

import config


def get_connection():
    """建立 SQLite 連線，並允許用欄位名稱取得資料。"""
    connection = sqlite3.connect(config.DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection
