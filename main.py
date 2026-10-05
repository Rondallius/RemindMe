import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# main.py creates the database, the three feature services and the main window.
# It is the only file that knows all three features.
from database.database import Database
from features.management.service import TaskService
from features.management.view import ManagementView
from features.notification.service import NotificationService
from features.timer.service import TimerService


# The main window of the application.
class RemindMeWindow(QDialog):
    def __init__(self, management, timer, notification):
        super().__init__()
        # Keeps the three services, so the window can use them and close them.
        self.management = management
        self.timer = timer
        self.notification = notification
        self.setWindowTitle("RemindMe")
        self.resize(940, 640)

        # This one line connects two features:
        # the Timer sends "reminder_due" and the Notification shows the reminder.
        timer.reminder_due.connect(notification.show_reminder)

        self.build_ui()

    def build_ui(self):
        # Creates the header and the Management screen.
        # The colors come from style.qss, not from this file.
        self.setObjectName("mainContent")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(14)

        # --- The blue header: title, subtitle and the Exit button ---
        header = QWidget()
        header.setObjectName("appHeader")
        header.setMinimumHeight(78)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(22, 14, 18, 14)
        header_layout.setSpacing(16)

        title_group = QVBoxLayout()
        title_group.setSpacing(2)
        title = QLabel("RemindMe")
        title.setObjectName("appTitle")
        subtitle = QLabel("Add tasks and get reminded when time is up")
        subtitle.setObjectName("appSubtitle")
        title_group.addWidget(title)
        title_group.addWidget(subtitle)
        # The 1 lets the title use all the space that the Exit button does not.
        header_layout.addLayout(title_group, 1)

        exit_button = QPushButton("Exit")
        exit_button.setObjectName("exitButton")
        exit_button.setFixedHeight(36)
        exit_button.clicked.connect(self.close)
        header_layout.addWidget(exit_button)
        layout.addWidget(header)

        # Adds the Management screen. It also shows every countdown.
        layout.addWidget(ManagementView(self.management, self.timer))

    def closeEvent(self, event):
        # Asks the user before closing.
        # Completing the tasks, stopping the timers and closing the reminders
        # makes sure nothing temporary is left behind.
        answer = QMessageBox.question(
            self,
            "Close Program",
            "Closing the program will mark all pending tasks as Completed. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            event.ignore()
            return

        self.management.complete_all_tasks()
        self.timer.stop_all()
        self.notification.close_all()
        event.accept()


# Starts the application.
def main():
    # 1. Creates the database file and the tasks table.
    database = Database()
    database.create_tables()

    # 2. Creates the PyQt application and loads the main style file.
    #    The style file now lives in features/management/, next to the screen
    #    it styles, so the path is built from this file's folder. It is
    #    absolute, so it still works when the program is started from the
    #    project root.
    app = QApplication(sys.argv)
    app.setStyleSheet(
        (Path(__file__).parent / "features" / "management" / "style.qss").read_text()
    )

    # 3. Creates the three feature services.
    #    Management saves the tasks in SQLite.
    #    Timer and Notification only keep temporary data in memory.
    management = TaskService(database)
    timer = TimerService()
    # The Notification service gets the Management service, so "Complete Task"
    # marks the existing task as Completed instead of using a second system.
    notification = NotificationService(timer, management)

    # 4. Creates the main window and shows it.
    #    show() is used instead of exec() on purpose: exec() would make this
    #    window modal, and Qt would then block clicks on the reminder windows.
    window = RemindMeWindow(management, timer, notification)
    window.show()

    # 5. Starts the Qt event loop. This keeps the program running.
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())