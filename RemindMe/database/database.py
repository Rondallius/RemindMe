import sqlite3
from pathlib import Path


# Database: creates and connects to the SQLite database.
class Database:
    def __init__(self, database_path: str | Path | None = None) -> None:
        # The database file is tasks.db in this folder.
        if database_path is None:
            database_path = Path(__file__).resolve().parent / "tasks.db"
        self.database_path = Path(database_path)

    # Opens a connection to the database file.
    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    # Creates the tasks table if it does not exist yet.
    # IF NOT EXISTS means this can run again on every start without making a
    # second table. The connection is opened, used and then closed, exactly
    # like the repository does it.
    def create_tables(self) -> None:
        connection = self.connect()
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                reminder_seconds INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                task_type TEXT NOT NULL DEFAULT 'Digital Task'
            );
            """
        )
        connection.commit()
        connection.close()