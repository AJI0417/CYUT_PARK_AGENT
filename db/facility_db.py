from db.connection import get_connection


ALLOWED_STATUSES = (
    "正常開放",
    "暫停開放",
    "設施維修中",
)


def get_all_facilities():
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, 設施名稱, 設施類別, 設施狀態
            FROM facilities
            ORDER BY id
            """
        ).fetchall()
    finally:
        connection.close()


def get_facility_ids():
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT id
            FROM facilities
            ORDER BY id
            """
        ).fetchall()
    finally:
        connection.close()

    return [row["id"] for row in rows]


def update_facility_statuses(updates):
    """updates 的格式為 [(新狀態, 設施 ID), ...]。"""
    connection = get_connection()

    try:
        with connection:
            connection.executemany(
                """
                UPDATE facilities
                SET 設施狀態 = ?
                WHERE id = ?
                """,
                updates,
            )
    finally:
        connection.close()
