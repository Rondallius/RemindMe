from pathlib import Path

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QBrush, QColor, QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .model import Task, parse_reminder, seconds_to_text
# The task types come from the Notification feature.
from features.notification.model import TASK_TYPES
# Shows the countdown of every task on the Management screen.
from features.timer.view import TimerView


# The ID column only shows small row numbers, so it stays narrow.
ID_COLUMN_WIDTH = 42

# The share of the width that each column gets, for Name, Description, Timer,
# Type and Status. Description gets the biggest share, but every other column
# keeps enough room to stay readable.
COLUMN_SHARES = (0.15, 0.36, 0.14, 0.21, 0.14)

# The smallest width a column may shrink to while its text still fits.
COLUMN_MINIMUMS = (80, 150, 100, 140, 105)

# The heights that keep the form small, so the table gets most of the window.
# The single-line inputs and the buttons are set to the same height, so
# everything in the form lines up in a neat column.
INPUT_HEIGHT = 30
DESCRIPTION_HEIGHT = 96
BUTTON_HEIGHT = 30
COUNTDOWN_HEIGHT = 30

# The widths of the left side of the form. The three single-line inputs are
# INPUT_WIDTH wide, and they never grow wider than LEFT_SIDE_WIDTH. The
# Description on the right takes all the space that is left over.
INPUT_WIDTH = 250
LEFT_SIDE_WIDTH = 300

# The colors of a task whose status is Completed.
# A green row makes a finished task easy to see in the table, and it is still
# easy to tell apart from a Pending task, which keeps the normal row color.
COMPLETED_BACKGROUND = QColor("#c8f0d4")  # clear light green row
COMPLETED_TEXT = QColor("#14532d")  # dark green text
COMPLETED_STATUS_TEXT = QColor("#15803d")  # strong green for the status word


# View: handles the GUI (the form, the buttons and the task table).
# The view only uses the services. It never works with the database.
class ManagementView(QWidget):
    def __init__(self, service, timer_service):
        super().__init__()
        self.setObjectName("managementView")
        self.service = service  # Adds, completes and deletes the tasks.
        self.timer_service = timer_service  # Starts and stops the countdowns.

        # The tasks shown in the table, in the same order as the table rows.
        # The row number in the table is the position in this list, so the real
        # database id is always taken from the task object and never from the
        # table.
        self.tasks = []

        self.build_ui()
        self.setStyleSheet(Path(__file__).with_name("style.qss").read_text())

        # Every second the Timer column, the Status column and the countdown
        # label under the table are refreshed.
        self.timer_service.countdown_updated.connect(self.refresh_countdown)
        self.timer_service.countdown_updated.connect(self.timer_view.refresh)

        # Shows the tasks that are already in the database.
        self.refresh()

    def build_ui(self):
        # Creates all the widgets of this screen.
        layout = QVBoxLayout(self)
        # main.py already sets the window margins, so this screen adds none.
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # --- The Add Task form ---
        # The form has two sides: the left side holds Name, Reminder Time and
        # Task Type, and the right side holds the bigger Description box.
        form_row = QHBoxLayout()
        form_row.setContentsMargins(0, 0, 0, 0)
        form_row.setSpacing(12)

        # LEFT SIDE: the three single-line inputs, one under the other.
        left_form = QFormLayout()
        left_form.setContentsMargins(0, 0, 0, 0)
        # A small gap keeps the rows together without wasting height.
        left_form.setVerticalSpacing(4)
        left_form.setHorizontalSpacing(8)
        # Keeps the labels lined up with their input fields.
        left_form.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Example: Study Math")
        self.name_input.setFixedHeight(INPUT_HEIGHT)

        self.reminder_input = QLineEdit()
        self.reminder_input.setPlaceholderText("00:05:30")
        self.reminder_input.setFixedHeight(INPUT_HEIGHT)

        self.type_input = QComboBox()
        self.type_input.addItems(TASK_TYPES)
        self.type_input.setFixedHeight(INPUT_HEIGHT)

        # The left side stays narrow, so the Description gets most of the width.
        # INPUT_WIDTH makes the three fields a little wider than their default
        # size, so a longer task name and reminder time still fit inside them.
        for input_widget in (self.name_input, self.reminder_input, self.type_input):
            input_widget.setFixedWidth(INPUT_WIDTH)

        left_form.addRow("Name", self.name_input)
        left_form.addRow("Reminder Time", self.reminder_input)
        left_form.addRow("Task Type", self.type_input)
        form_row.addLayout(left_form)

        # RIGHT SIDE: the Description, which is much bigger than the other inputs.
        right_form = QVBoxLayout()
        right_form.setContentsMargins(0, 0, 0, 0)
        right_form.setSpacing(3)
        right_form.addWidget(QLabel("Description"))

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Optional notes about the task")
        # The Description is the tallest field of the form. It is still a
        # QTextEdit, so a long description can be typed and wraps.
        self.description_input.setFixedHeight(DESCRIPTION_HEIGHT)
        right_form.addWidget(self.description_input)
        # The 1 makes the Description take the space that is left on the right.
        form_row.addLayout(right_form, 1)

        layout.addLayout(form_row)

        # --- Add Task / Complete Task / Delete Task, all in one row ---
        actions = QHBoxLayout()
        actions.setSpacing(8)

        add_button = QPushButton("Add Task")
        add_button.setObjectName("primaryButton")
        add_button.setFixedHeight(BUTTON_HEIGHT)
        add_button.clicked.connect(self.add_task)
        actions.addWidget(add_button)

        complete_button = QPushButton("Complete Task")
        complete_button.setObjectName("completeButton")
        complete_button.setFixedHeight(BUTTON_HEIGHT)
        complete_button.clicked.connect(self.complete_task)
        actions.addWidget(complete_button)

        delete_button = QPushButton("Delete Task")
        delete_button.setObjectName("dangerButton")
        delete_button.setFixedHeight(BUTTON_HEIGHT)
        delete_button.clicked.connect(self.delete_task)
        actions.addWidget(delete_button)
        layout.addLayout(actions)

        # --- The task table: one row per task ---
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Name", "Description", "Timer", "Type", "Status"]
        )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        # The table is read-only. Tasks are changed with the buttons.
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # A long description wraps onto more lines instead of being cut off.
        self.table.setWordWrap(True)

        # The ID column already shows the row number, so the built-in row
        # numbers on the far left are hidden.
        self.table.verticalHeader().setVisible(False)
        # Every row becomes as tall as its own text needs, so a long
        # description grows its row instead of being cut off.
        self.table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        # A floor, so a one-line row is not clipped. Rows with more text
        # are still free to grow past it.
        self.table.verticalHeader().setMinimumSectionSize(26)

        # The ID column holds small numbers only, so it stays narrow and fixed.
        self.table.setColumnWidth(0, ID_COLUMN_WIDTH)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Fixed
        )
        # The other columns get their width from resize_table_columns().
        for column in range(1, self.table.columnCount()):
            self.table.horizontalHeader().setSectionResizeMode(
                column, QHeaderView.ResizeMode.Interactive
            )

        # The 3 is the stretch factor: the table is the most important part of
        # the screen, so it takes all the space that is left and grows with the
        # window. The 1 next to the countdown keeps the countdown at the bottom.
        layout.addWidget(self.table, 3)

        # Shows the countdown of every task under the table.
        # It stays at the bottom and stays small, so it does not steal height
        # from the table.
        self.timer_view = TimerView(self.timer_service)
        self.timer_view.setFixedHeight(COUNTDOWN_HEIGHT)
        layout.addWidget(self.timer_view, 1)

        # The table only has its final size after the window is shown, so the
        # column widths are set one moment later.
        self.update_column_widths()
        # A scrollbar appearing makes the table narrower, so they are set again.
        self.table.verticalScrollBar().rangeChanged.connect(
            self.update_column_widths
        )

    def update_column_widths(self):
        # When Qt says the size changed, the table is not the right size yet,
        # so the columns are shared out one moment later.
        QTimer.singleShot(0, self.resize_table_columns)

    def resize_table_columns(self):
        # Shares the available width between the columns after the ID column.
        # Every column keeps at least its own minimum, so Timer, Type and
        # Status stay readable instead of being squeezed by a long description.
        available = self.table.viewport().width() - self.table.columnWidth(0)
        used_width = 0

        for column in range(1, self.table.columnCount() - 1):
            share = COLUMN_SHARES[column - 1]
            minimum = COLUMN_MINIMUMS[column - 1]
            width = int(available * share)
            if width < minimum:
                width = minimum
            self.table.setColumnWidth(column, width)
            used_width = used_width + width

        # The last column takes exactly what is left, so the columns always end
        # at the edge of the table instead of overflowing it.
        last_column = self.table.columnCount() - 1
        last_width = available - used_width
        if last_width < COLUMN_MINIMUMS[last_column - 1]:
            last_width = COLUMN_MINIMUMS[last_column - 1]
        self.table.setColumnWidth(last_column, last_width)

    def resizeEvent(self, event):
        # Keeps the column widths in step with the window size.
        super().resizeEvent(event)
        self.update_column_widths()

    def check_required_fields(self):
        # The Name and the Reminder Time are both required, so they are checked
        # before the reminder time is parsed. This keeps a missing field
        # separate from a wrongly formatted one: an empty field never shows the
        # HH:MM:SS format message.
        has_name = bool(self.name_input.text().strip())
        has_time = bool(self.reminder_input.text().strip())

        if not has_name and not has_time:
            QMessageBox.warning(
                self, "Missing Information",
                "Please input a task name and reminder time."
            )
            return False
        if not has_name:
            QMessageBox.warning(self, "Missing Task Name", "Please input a task name.")
            return False
        if not has_time:
            QMessageBox.warning(
                self, "Missing Reminder Time", "Please input a reminder time."
            )
            return False
        return True

    def add_task(self):
        # Reads the form, creates the task and saves it.
        # The two required inputs are checked first, so an empty field is
        # reported as "missing information" and never as a wrong format.
        if not self.check_required_fields():
            return

        try:
            task = Task(
                self.name_input.text(),
                self.description_input.toPlainText(),
                parse_reminder(self.reminder_input.text()),
                self.type_input.currentText(),
            )
        except ValueError as error:
            # Shows the error message of the Task model.
            QMessageBox.warning(self, "Invalid Task", str(error))
            return

        # The task is saved first, because the countdown needs its id.
        self.service.add_task(task)

        # Empties the form for the next task.
        self.name_input.clear()
        self.description_input.clear()
        self.reminder_input.clear()

        # Shows the task in the table and starts its countdown.
        self.refresh()
        self.timer_service.start_countdown(task)

    def complete_task(self):
        # Completes the selected task and stops its countdown.
        task = self.selected_task()
        if task is None:
            return
        self.service.complete_task(task)
        self.timer_service.stop_countdown(task.id)
        self.refresh()

    def delete_task(self):
        # Deletes the selected task after the user confirms.
        # The countdown stops too, so the task can no longer be reminded.
        task = self.selected_task()
        if task is None:
            return

        # The dialog is built by hand instead of QMessageBox.question(), so
        # the Yes button can be named and styled as the destructive action.
        # The message, the buttons and the behaviour are the same as before.
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle("Delete Task")
        dialog.setText(f"Do you really want to delete '{task.name}'?")
        dialog.setInformativeText("This cannot be undone.")
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        # No is the default, so pressing Enter never deletes by accident.
        dialog.setDefaultButton(QMessageBox.StandardButton.No)

        yes_button = dialog.button(QMessageBox.StandardButton.Yes)
        # The red object name is styled in style.qss, so the destructive
        # button is red and the Cancel button stays neutral.
        yes_button.setObjectName("confirmDeleteButton")
        no_button = dialog.button(QMessageBox.StandardButton.No)
        no_button.setObjectName("cancelDeleteButton")
        # A dialog is its own top-level window, so Qt does not hand it the
        # style sheet of the Management screen. The same style.qss is given to
        # the dialog, so the red button rule below is applied. The dialog is
        # created as a child of this view, so the "#managementView ..." rules
        # in style.qss still match it.
        dialog.setStyleSheet(Path(__file__).with_name("style.qss").read_text())

        dialog.exec()
        if dialog.clickedButton() is not yes_button:
            return

        self.service.delete_task(task)
        self.timer_service.stop_countdown(task.id)
        self.refresh()

    def selected_task(self):
        # Gets the selected task from the table.
        # The ID column only shows the row number, so the real database id is
        # NEVER read from the table. The row number is used to find the task in
        # the list that filled the table, and the task object keeps its id.
        row = self.table.currentRow()
        if row < 0 or row >= len(self.tasks):
            QMessageBox.information(
                self, "No Task Selected", "Please select a task in the table first."
            )
            return None
        return self.tasks[row]

    def reminder_text(self, task):
        # Shows the time left, or the original time if there is no countdown.
        seconds_left = self.timer_service.get_seconds_left(task.id)
        if seconds_left is None:
            return seconds_to_text(task.reminder_seconds)
        return seconds_to_text(seconds_left)

    def refresh_countdown(self):
        # Runs every second and updates the Timer column and the Status
        # column. The Status column is updated too, so a task that was
        # completed from a reminder window also shows "Completed" here.
        tasks = self.service.get_tasks()
        self.tasks = tasks

        for row, task in enumerate(tasks):
            timer_item = self.table.item(row, 3)
            if timer_item is not None:
                timer_item.setText(self.reminder_text(task))

            status_item = self.table.item(row, 5)
            if status_item is not None:
                status_item.setText(task.status)

            # A task can also be completed from its reminder window, so the
            # green row color is refreshed here too.
            self.style_row(row, task)

    def style_row(self, row, task):
        # Paints one row of the table.
        # A Pending row keeps the normal look of the table. A Completed row is
        # painted green, so a finished task is easy to recognize. Only the
        # colors of the row are changed; the table itself is not rebuilt.
        is_completed = task.status == "Completed"

        for column in range(self.table.columnCount()):
            item = self.table.item(row, column)
            if item is None:
                continue

            if is_completed:
                item.setBackground(QBrush(COMPLETED_BACKGROUND))
                item.setForeground(QBrush(COMPLETED_TEXT))
                # Bold text makes the finished task stand out even more.
                item.setFont(QFont(item.font().family(), item.font().pointSize(), 600))
            else:
                # An empty brush means "no color set by the code", so the
                # normal colors of style.qss are used again. This matters
                # because this method runs on every countdown tick.
                item.setBackground(QBrush())
                item.setForeground(QBrush())
                item.setFont(QFont(item.font().family(), item.font().pointSize(), 400))

            # The Status word itself gets the stronger green.
            if column == 5 and is_completed:
                item.setForeground(QBrush(COMPLETED_STATUS_TEXT))

    def refresh(self):
        # Updates the task table with all the tasks of the database.
        tasks = self.service.get_tasks()
        # Keeps the list that belongs to the rows, so a selected row can be
        # turned back into the right task with its real database id.
        self.tasks = tasks
        self.table.setRowCount(len(tasks))

        for row, task in enumerate(tasks):
            values = [
                # The ID column shows the row number, NOT the database id.
                # The database id stays inside the task object, untouched.
                row + 1,
                task.name,
                task.description,
                self.reminder_text(task),
                task.task_type,
                task.status,
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if column == 0:
                    # The small ID column shows centred row numbers.
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, column, item)

            # A Completed task is painted green, a Pending task keeps the
            # normal colors of the table.
            self.style_row(row, task)