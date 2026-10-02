"""view.py - the two windows: MainWindow and the Add Task dialog."""

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (QAbstractItemView, QDialog, QHBoxLayout,
                             QHeaderView, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QTextEdit, QVBoxLayout,
                             QWidget)

from features.task.model import seconds_to_text
from features.task.service import TaskServiceError

YES_NO = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No


class MainWindow(QMainWindow):
    """The RemindMe window: the task table, the buttons and the countdown."""

    def __init__(self, service):
        super().__init__()
        self.service = service
        self.tasks = []            # the tasks shown in the table
        self.countdowns = {}       # task id -> seconds still left
        self.running_tasks = {}    # task id -> the task that counts down

        self.setWindowTitle("RemindMe")
        self.resize(920, 470)

        self.build_widgets()
        self.connect_signals()

        # One timer for the whole window: it ticks once per second.
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.on_timer_tick)

        self.refresh_table()

    # ---------------- building the window ----------------
    def build_widgets(self):
        banner = self.build_banner()

        self.table = QTableWidget(0, 5)
        self.table.setObjectName("taskTable")
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(True)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Task Name", "Description", "Reminder Time", "Status"])
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # The Description column takes the spare width of the window.
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 45)
        self.table.setColumnWidth(1, 160)

        self.table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)

        self.add_button = QPushButton("Add Task")
        self.delete_button = QPushButton("Delete Task")
        self.complete_button = QPushButton("Mark Complete")
        self.refresh_button = QPushButton("Refresh")
        self.exit_button = QPushButton("Exit")

        button_column = QVBoxLayout()
        for button in (self.add_button, self.delete_button,
                       self.complete_button, self.refresh_button,
                       self.exit_button):
            button.setMinimumWidth(130)
            button_column.addWidget(button)
        button_column.addStretch()

        self.info_label = QLabel("Countdown: none")
        self.info_label.setObjectName("infoLabel")

        table_column = QVBoxLayout()
        table_column.setSpacing(8)
        table_column.addWidget(self.table)
        table_column.addWidget(self.info_label)

        row_layout = QHBoxLayout()
        row_layout.setSpacing(14)
        row_layout.addLayout(table_column, 4)
        row_layout.addLayout(button_column, 1)

        page_layout = QVBoxLayout()
        page_layout.setContentsMargins(16, 16, 16, 12)
        page_layout.setSpacing(12)
        page_layout.addWidget(banner)
        page_layout.addLayout(row_layout, 1)

        content = QWidget()
        content.setObjectName("mainContent")
        content.setLayout(page_layout)
        self.setCentralWidget(content)
        self.statusBar().showMessage("Ready")

    def build_banner(self):
        """The blue banner with the title. Its colours live in style.qss."""
        banner = QWidget()
        banner.setObjectName("appHeader")

        title = QLabel("RemindMe: Task Reminder System")
        title.setObjectName("appTitle")
        subtitle = QLabel("Manage your tasks and reminders")
        subtitle.setObjectName("appSubtitle")

        banner_layout = QVBoxLayout(banner)
        banner_layout.setContentsMargins(18, 10, 18, 10)
        banner_layout.setSpacing(2)
        banner_layout.addWidget(title)
        banner_layout.addWidget(subtitle)
        return banner

    def connect_signals(self):
        self.add_button.clicked.connect(self.open_add_dialog)
        self.delete_button.clicked.connect(self.delete_task)
        self.complete_button.clicked.connect(self.mark_complete)
        self.refresh_button.clicked.connect(self.refresh_table)
        # Exit does what the X of the window does: it asks before closing.
        self.exit_button.clicked.connect(self.close)

    # ---------------- add task ----------------
    def open_add_dialog(self):
        dialog = TaskDialog(self.service, self)
        dialog.task_saved.connect(self.add_task)
        dialog.exec()

    def add_task(self, task):
        """Slot for the dialog signal: save the task and count it down."""
        try:
            self.service.add_task(task)
        except TaskServiceError as error:
            QMessageBox.critical(self, "Database Error", str(error))
            return
        self.refresh_table()
        self.start_countdown(task)
        self.statusBar().showMessage(
            f"Saved task '{task.name}' ({task.reminder_text()})", 5000)

    # ---------------- show the tasks ----------------
    def refresh_table(self):
        """Slot for 'Refresh': read every task and show it in the table."""
        try:
            tasks = self.service.get_tasks()
        except TaskServiceError as error:
            QMessageBox.critical(self, "Database Error", str(error))
            return

        # Remember the selected task so the selection survives the rebuild.
        selected_id = None
        if 0 <= self.table.currentRow() < len(self.tasks):
            selected_id = self.tasks[self.table.currentRow()].task_id

        self.tasks = tasks
        self.table.setRowCount(0)
        for task in self.tasks:
            row = self.table.rowCount()
            self.table.insertRow(row)
            # The ID column shows the position in the list, not the database id.
            values = [row + 1, task.name, task.description,
                      self.reminder_text(task), task.status_label()]
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if column == 0:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, column, item)

        self.table.resizeRowsToContents()
        if selected_id is not None:
            for row, task in enumerate(self.tasks):
                if task.task_id == selected_id:
                    self.table.selectRow(row)
                    break
        self.update_info_label()

    def reminder_text(self, task):
        """The Reminder Time column: the time left while it is running."""
        if task.task_id in self.countdowns:
            return seconds_to_text(self.countdowns[task.task_id])
        return task.reminder_text()

    def selected_task(self):
        """The task the user selected, or None when nothing is selected."""
        row = self.table.currentRow()
        if row < 0 or row >= len(self.tasks):
            QMessageBox.information(self, "No Task Selected",
                                    "Please select a task in the table first.")
            return None
        return self.tasks[row]

    # ---------------- mark complete ----------------
    def mark_complete(self):
        """Slot for 'Mark Complete'."""
        task = self.selected_task()
        if task is None:
            return
        if task.is_completed():
            QMessageBox.information(self, "Already Completed",
                                    f"'{task.name}' is already completed.")
            return
        try:
            self.service.mark_complete(task)
        except TaskServiceError as error:
            QMessageBox.critical(self, "Database Error", str(error))
            return
        self.stop_countdown(task.task_id)
        self.refresh_table()
        self.statusBar().showMessage(
            f"'{task.name}' marked as completed", 5000)

    # ---------------- delete ----------------
    def delete_task(self):
        """Slot for 'Delete Task': asks first, then deletes the task."""
        task = self.selected_task()
        if task is None:
            return
        answer = QMessageBox.question(
            self, "Delete Task", f"Do you really want to delete '{task.name}'?",
            YES_NO, QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            self.service.delete_task(task)
        except TaskServiceError as error:
            QMessageBox.critical(self, "Database Error", str(error))
            return
        self.stop_countdown(task.task_id)
        self.refresh_table()
        self.statusBar().showMessage(f"Deleted task '{task.name}'", 5000)

    # ---------------- countdown and alarm ----------------
    def start_countdown(self, task):
        """Puts a task in the countdown. A completed task counts 0 seconds."""
        seconds = task.countdown_seconds()
        if seconds <= 0 or task.task_id is None:
            return
        self.countdowns[task.task_id] = seconds
        self.running_tasks[task.task_id] = task
        if not self.timer.isActive():
            self.timer.start()
        self.refresh_table()

    def stop_countdown(self, task_id):
        """Takes one task out of the countdown."""
        self.countdowns.pop(task_id, None)
        self.running_tasks.pop(task_id, None)
        if not self.countdowns:
            self.timer.stop()

    def on_timer_tick(self):
        """Slot of the timer: once per second every countdown loses 1."""
        finished = []
        for task_id in list(self.countdowns):
            self.countdowns[task_id] -= 1
            if self.countdowns[task_id] <= 0:
                finished.append(task_id)

        for task_id in finished:
            task = self.running_tasks.pop(task_id, None)
            self.countdowns.pop(task_id, None)
            if task is not None:
                QMessageBox.information(self, "Time is up!", task.alarm_message())

        if not self.countdowns:
            self.timer.stop()

        # Only the Reminder Time column is rewritten, so the row the user
        # selected stays selected while the countdown runs.
        for row, task in enumerate(self.tasks):
            item = self.table.item(row, 3)
            if item is not None:
                item.setText(self.reminder_text(task))
        self.update_info_label()

    def update_info_label(self):
        """Shows the running countdowns under the table."""
        if not self.countdowns:
            self.info_label.setText("Countdown: none")
            return
        parts = []
        for task_id, seconds in self.countdowns.items():
            task = self.running_tasks.get(task_id)
            name = task.name if task is not None else str(task_id)
            parts.append(f"{name} {seconds_to_text(seconds)}")
        self.info_label.setText("Countdown: " + "   |   ".join(parts))

    # ---------------- closing the window ----------------
    def closeEvent(self, event):
        """Asks first: 'Yes' finishes the pending tasks, 'No' stays open."""
        answer = QMessageBox.question(
            self, "Close Program",
            "Closing the program will immediately mark all pending tasks as "
            "COMPLETED. Do you want to continue?",
            YES_NO, QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            event.ignore()
            return
        try:
            self.service.complete_all_pending()
        except TaskServiceError as error:
            QMessageBox.critical(self, "Database Error", str(error))
        self.timer.stop()
        event.accept()


class TaskDialog(QDialog):
    """The Add Task form: it collects and checks the typed data."""

    # Sent when the typed data is correct. It carries a Task object.
    task_saved = pyqtSignal(object)

    def __init__(self, service, parent=None):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Add Task")
        self.setMinimumWidth(380)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Example: Study Math")

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Optional notes about the task")
        self.description_input.setMaximumHeight(70)

        self.reminder_input = QLineEdit()
        self.reminder_input.setPlaceholderText("HH:MM:SS   Example: 00:05:30")
        self.reminder_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.cancel_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Task Name:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.description_input)
        layout.addWidget(QLabel("Reminder Time (HH:MM:SS):"))
        layout.addWidget(self.reminder_input)
        layout.addLayout(button_row)
        self.setLayout(layout)

        self.save_button.clicked.connect(self.save_task)
        self.cancel_button.clicked.connect(self.reject)
        self.name_input.setFocus()

    def save_task(self):
        """Slot for 'Save': check the data, then send it to MainWindow."""
        try:
            task = self.service.create_task(
                self.name_input.text(),
                self.description_input.toPlainText(),
                self.reminder_input.text())
        except (ValueError, TaskServiceError) as error:
            QMessageBox.warning(self, "Invalid Input", str(error))
            return
        self.task_saved.emit(task)
        self.accept()
