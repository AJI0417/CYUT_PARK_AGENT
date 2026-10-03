from db.connection import get_connection


def get_all_announcements():
    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT id, published_at, publisher, title, content
            FROM announcements
            ORDER BY published_at DESC, id DESC
            """
        ).fetchall()
    finally:
        connection.close()


def create_announcement(published_at, publisher, title, content):
    connection = get_connection()

    try:
        with connection:
            connection.execute(
                """
                INSERT INTO announcements (
                    published_at,
                    publisher,
                    title,
                    content
                )
                VALUES (?, ?, ?, ?)
                """,
                (published_at, publisher, title, content),
            )
    finally:
        connection.close()


def delete_announcement_by_id(announcement_id):
    connection = get_connection()

    try:
        with connection:
            cursor = connection.execute(
                """
                DELETE FROM announcements
                WHERE id = ?
                """,
                (announcement_id,),
            )

            return cursor.rowcount > 0
    finally:
        connection.close()
