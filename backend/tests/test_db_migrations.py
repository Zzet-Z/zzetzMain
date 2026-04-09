import sqlite3
from pathlib import Path

from app.db_migrations import migrate_sqlite_schema


def create_legacy_schema(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE sessions (
            token VARCHAR(64) PRIMARY KEY,
            locale VARCHAR(16) NOT NULL,
            status VARCHAR(32) NOT NULL,
            current_stage VARCHAR(32) NOT NULL,
            selected_template VARCHAR(64),
            selected_style VARCHAR(64),
            queued_at DATETIME,
            last_error TEXT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        );

        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token VARCHAR(64) NOT NULL,
            role VARCHAR(16) NOT NULL,
            content TEXT NOT NULL,
            stage VARCHAR(32) NOT NULL,
            created_at DATETIME NOT NULL
        );

        CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token VARCHAR(64) NOT NULL,
            status VARCHAR(32) NOT NULL,
            version INTEGER NOT NULL,
            summary_text TEXT NOT NULL,
            prd_markdown TEXT NOT NULL,
            created_at DATETIME NOT NULL
        );
        """
    )

    cur.execute(
        """
        INSERT INTO sessions
        (token, locale, status, current_stage, selected_template, selected_style, queued_at, last_error, created_at, updated_at)
        VALUES
        ('legacy-token', 'zh-CN', 'active', 'template', NULL, NULL, NULL, NULL, '2026-04-09 08:00:00', '2026-04-09 08:00:00')
        """
    )
    cur.execute(
        """
        INSERT INTO messages
        (session_token, role, content, stage, created_at)
        VALUES
        ('legacy-token', 'assistant', '欢迎使用。', 'system', '2026-04-09 08:00:01')
        """
    )
    cur.execute(
        """
        INSERT INTO documents
        (session_token, status, version, summary_text, prd_markdown, created_at)
        VALUES
        ('legacy-token', 'ready', 2, '旧摘要', '# 旧文档', '2026-04-09 08:00:02')
        """
    )

    conn.commit()
    conn.close()


def table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table_name})")
    return {row[1] for row in cur.fetchall()}


def test_migrate_sqlite_schema_upgrades_legacy_tables(tmp_path):
    db_path = tmp_path / "legacy.db"
    create_legacy_schema(db_path)

    migrate_sqlite_schema(db_path)

    conn = sqlite3.connect(db_path)
    try:
        session_columns = table_columns(conn, "sessions")
        message_columns = table_columns(conn, "messages")
        document_columns = table_columns(conn, "documents")

        assert "admin_note" in session_columns
        assert "origin_session_token" in session_columns
        assert "previous_document_id" in session_columns
        assert "next_session_token" in session_columns
        assert "expires_at" in session_columns

        assert "stage" in message_columns
        assert "delivery_status" in message_columns

        assert "version" in document_columns
        assert "parent_document_id" in document_columns
        assert "root_document_id" in document_columns
        assert "revision_number" in document_columns

        cur = conn.cursor()
        cur.execute("SELECT delivery_status FROM messages WHERE session_token='legacy-token'")
        assert cur.fetchone()[0] == "system"

        cur.execute("SELECT version, revision_number FROM documents WHERE session_token='legacy-token'")
        assert cur.fetchone() == (2, 2)
    finally:
        conn.close()


def test_migrate_sqlite_schema_is_idempotent(tmp_path):
    db_path = tmp_path / "legacy.db"
    create_legacy_schema(db_path)

    migrate_sqlite_schema(db_path)
    migrate_sqlite_schema(db_path)

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sessions")
        assert cur.fetchone()[0] == 1

        cur.execute("SELECT COUNT(*) FROM messages")
        assert cur.fetchone()[0] == 1

        cur.execute("SELECT COUNT(*) FROM documents")
        assert cur.fetchone()[0] == 1
    finally:
        conn.close()
