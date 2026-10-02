"""database.py - the SQLite file, the connection and the table creation."""

import sqlite3
from pathlib import Path


class TaskDatabase:
    """Knows where tasks.db is and how to create the tasks table."""

    def __init__(self, database_path=None):
        # tasks.db is created next to this file, SQLite builds it by itself.
        self.database_path = Path(database_path) if database_path else Path(__file__).resolve().parent / "tasks.db"

    def connect(self):
        """Opens the connection to tasks.db (SQLite creates the file if needed)."""
        return sqlite3.connect(self.database_path)

    def create_tables(self):
        """CREATE TABLE - makes the tasks table when it is missing."""
        with self.connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    name             TEXT    NOT NULL,
                    description      TEXT,
                    reminder_seconds INTEGER NOT NULL,
                    created_at       TEXT    NOT NULL,
                    status           TEXT    NOT NULL
                )
            """)
