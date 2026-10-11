import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "meetings.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

def get_connection():
    """DBに接続して返す。"""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON")

    return conn

def init_db():
    """schema.sql を読んでテーブルを作る。"""

    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_connection() as conn:
        conn.executescript(schema)

def insert_meeting(title, held_on, file_name, file_hash, raw_text):
    """meetingsに1行入れて、新しい会議idを返す。
    重複(hashが同じ)なら None。
    """

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO meetings (
                    title,
                    held_on,
                    file_name,
                    file_hash,
                    raw_text
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    title,
                    held_on,
                    file_name,
                    file_hash,
                    raw_text
                )
            )

            return cursor.lastrowid

    except sqlite3.IntegrityError:
        return None

def insert_chunks(meeting_id, chunks: list[str]):
    """段落リストを chunks にまとめて保存する。"""

    rows = []

    for index, content in enumerate(chunks):
        rows.append(
            (
                meeting_id,
                index,
                content
            )
        )

    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO chunks (
                meeting_id,
                chunk_index,
                content
            )
            VALUES (?, ?, ?)
            """,
            rows
        )

def get_search_pages() -> list[dict]:
    """chunksを講義の検索が使える辞書形式に変換して返す。"""

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                chunks.id AS chunk_id,
                meetings.id AS meeting_id,
                meetings.title AS title,
                meetings.held_on AS held_on,
                chunks.content AS content
            FROM chunks
            JOIN meetings
                ON chunks.meeting_id = meetings.id
            ORDER BY
                meetings.held_on DESC,
                chunks.chunk_index ASC
            """
        ).fetchall()

    pages = []

    for row in rows:
        content = row["content"]

        pages.append(
            {
                "id": row["chunk_id"],
                "meeting_id": row["meeting_id"],
                "title": row["title"],
                "description": "",
                "full_text": content,
                "keywords": [],
                "word_count": len(content),
                "crawled_at": row["held_on"],
                "url": str(row["meeting_id"]),
            }
        )

    return pages

def count_meetings() -> int:
    """登録されている会議数を返す。"""

    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS count FROM meetings"
        ).fetchone()

    return row["count"]

def get_meeting(meeting_id: int):

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                id,
                title,
                held_on,
                raw_text
            FROM meetings
            WHERE id = ?
            """,
            (meeting_id,)
        ).fetchone()

    if row is None:
        return None

    return dict(row)