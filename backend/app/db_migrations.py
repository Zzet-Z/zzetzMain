from __future__ import annotations

import sqlite3
from pathlib import Path


def _table_columns(cursor: sqlite3.Cursor, table_name: str) -> set[str]:
    cursor.execute(f"PRAGMA table_info({table_name})")
    return {row[1] for row in cursor.fetchall()}


def _rebuild_messages(cursor: sqlite3.Cursor) -> None:
    cursor.execute("ALTER TABLE messages RENAME TO messages_old")
    old_columns = _table_columns(cursor, "messages_old")
    cursor.execute(
        """
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token VARCHAR(64) NOT NULL REFERENCES sessions(token),
            role VARCHAR(16) NOT NULL,
            content TEXT NOT NULL,
            stage VARCHAR(32) NOT NULL DEFAULT 'final',
            created_at DATETIME NOT NULL,
            delivery_status VARCHAR(32) NOT NULL DEFAULT 'final'
        )
        """
    )
    delivery_status_select = (
        "COALESCE(delivery_status, stage, 'final')"
        if "delivery_status" in old_columns
        else "COALESCE(stage, 'final')"
    )
    cursor.execute(
        f"""
        INSERT INTO messages (id, session_token, role, content, stage, created_at, delivery_status)
        SELECT
            id,
            session_token,
            role,
            content,
            COALESCE(stage, 'final'),
            created_at,
            {delivery_status_select}
        FROM messages_old
        """
    )
    cursor.execute("DROP TABLE messages_old")


def _rebuild_documents(cursor: sqlite3.Cursor) -> None:
    cursor.execute("ALTER TABLE documents RENAME TO documents_old")
    old_columns = _table_columns(cursor, "documents_old")
    cursor.execute(
        """
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token VARCHAR(64) NOT NULL REFERENCES sessions(token),
            status VARCHAR(32) NOT NULL DEFAULT 'pending',
            version INTEGER NOT NULL DEFAULT 1,
            summary_text TEXT NOT NULL DEFAULT '',
            prd_markdown TEXT NOT NULL DEFAULT '',
            created_at DATETIME NOT NULL,
            parent_document_id INTEGER REFERENCES documents(id),
            root_document_id INTEGER REFERENCES documents(id),
            revision_number INTEGER NOT NULL DEFAULT 1
        )
        """
    )
    version_select = (
        "COALESCE(version, revision_number, 1)"
        if "revision_number" in old_columns
        else "COALESCE(version, 1)"
    )
    revision_select = (
        "COALESCE(revision_number, version, 1)"
        if "revision_number" in old_columns
        else "COALESCE(version, 1)"
    )
    parent_select = "parent_document_id" if "parent_document_id" in old_columns else "NULL"
    root_select = "root_document_id" if "root_document_id" in old_columns else "NULL"
    cursor.execute(
        f"""
        INSERT INTO documents (
            id,
            session_token,
            status,
            version,
            summary_text,
            prd_markdown,
            created_at,
            parent_document_id,
            root_document_id,
            revision_number
        )
        SELECT
            id,
            session_token,
            COALESCE(status, 'pending'),
            {version_select},
            COALESCE(summary_text, ''),
            COALESCE(prd_markdown, ''),
            created_at,
            {parent_select},
            {root_select},
            {revision_select}
        FROM documents_old
        """
    )
    cursor.execute("DROP TABLE documents_old")


def migrate_sqlite_schema(database_path: str | Path) -> None:
    database_path = Path(database_path)
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys=OFF")

    try:
        session_columns = _table_columns(cursor, "sessions")
        session_additions = {
            "admin_note": "ALTER TABLE sessions ADD COLUMN admin_note TEXT",
            "origin_session_token": "ALTER TABLE sessions ADD COLUMN origin_session_token VARCHAR(64)",
            "previous_document_id": "ALTER TABLE sessions ADD COLUMN previous_document_id INTEGER",
            "next_session_token": "ALTER TABLE sessions ADD COLUMN next_session_token VARCHAR(64)",
            "last_activity_at": "ALTER TABLE sessions ADD COLUMN last_activity_at DATETIME",
            "last_user_message_at": "ALTER TABLE sessions ADD COLUMN last_user_message_at DATETIME",
            "active_started_at": "ALTER TABLE sessions ADD COLUMN active_started_at DATETIME",
            "completed_at": "ALTER TABLE sessions ADD COLUMN completed_at DATETIME",
            "expires_at": "ALTER TABLE sessions ADD COLUMN expires_at DATETIME",
        }
        for column_name, statement in session_additions.items():
            if column_name not in session_columns:
                cursor.execute(statement)

        message_columns = _table_columns(cursor, "messages")
        if "delivery_status" not in message_columns:
            _rebuild_messages(cursor)

        document_columns = _table_columns(cursor, "documents")
        if {"parent_document_id", "root_document_id", "revision_number"} - document_columns:
            _rebuild_documents(cursor)

        conn.commit()
    finally:
        cursor.execute("PRAGMA foreign_keys=ON")
        conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Migrate SQLite schema for chat-first deployment")
    parser.add_argument("database_path", help="Path to SQLite database")
    args = parser.parse_args()

    migrate_sqlite_schema(args.database_path)
