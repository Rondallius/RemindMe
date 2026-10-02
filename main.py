"""main.py - the entry point. It only starts the program."""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from database.database import TaskDatabase
from features.task.repository import TaskRepository
from features.task.service import TaskService
from features.task.view import MainWindow

STYLE_FILE = Path(__file__).resolve().parent / "features" / "task" / "style.qss"


def main():
    database = TaskDatabase()
    database.create_tables()

    repository = TaskRepository(database)
    service = TaskService(repository)

    app = QApplication(sys.argv)
    if STYLE_FILE.exists():
        app.setStyleSheet(STYLE_FILE.read_text(encoding="utf-8"))

    window = MainWindow(service)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
