from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from features.management.model import Task
from .model import SNOOZE_MINUTES, REAL_LIFE_TASK


# Every button of a reminder window gets the same height, so the three
# answers line up neatly under each other.
BUTTON_HEIGHT = 38


# View: shows the reminder window.
# The task type decides which of the two designs is used.
class ReminderView(QWidget):
    # Sent when the user presses "Snooze 5 Minutes".
    # The window itself is sent, so the service knows which task it is.
    snoozed = pyqtSignal(object)

    # Sent when the user presses "Dismiss".
    dismissed = pyqtSignal(object)

    # Sent when the user presses "Complete Task".
    completed = pyqtSignal(object)

    def __init__(self, task: Task):
        super().__init__()
        # The task shown in this window.
        self.task = task
        # Makes sure the user can answer only once, so a task cannot be
        # completed and snoozed at the same time.
        self.answered = False
        # The reminder stays on top of the main window.
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        # The task type decides which colors are used.
        if task.task_type == REAL_LIFE_TASK:
            self.setObjectName("realLifeTaskView")
        else:
            self.setObjectName("digitalTaskView")
        self.build_ui()
        self.setStyleSheet(Path(__file__).with_name("style.qss").read_text())

    def build_ui(self):
        # Builds the Digital Task window or the Real-Life Task window.
        if self.task.task_type == REAL_LIFE_TASK:
            self.build_real_life_ui()
        else:
            self.build_digital_ui()

    def build_digital_ui(self):
        # Digital Task reminder: blue, screen/computer themed.
        # The layout is now balanced in the same way as the Real-Life Task
        # window: a header band, a card with the highlighted task name, the
        # description and the three buttons. The buttons stay stacked under
        # each other, which is what makes this design different from the
        # orange Real-Life Task window.
        self.setWindowTitle("RemindMe - Digital Task")
        self.setMinimumWidth(520)

        # --- The blue header band ---
        # The icon and the two lines of text share one blue band, so the
        # header looks like one block instead of a loose label.
        header = QFrame()
        header.setObjectName("digitalTaskHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 14, 18, 14)
        header_layout.setSpacing(14)

        icon = QLabel("\U0001F5A5")
        icon.setObjectName("digitalTaskHeaderIcon")
        header_layout.addWidget(icon, 0, Qt.AlignmentFlag.AlignVCenter)

        header_text = QVBoxLayout()
        header_text.setSpacing(2)
        title = QLabel("DIGITAL TASK")
        title.setObjectName("digitalTaskHeaderTitle")
        subtitle = QLabel("Screen and computer reminder")
        subtitle.setObjectName("digitalTaskHeaderSubtitle")
        header_text.addWidget(title)
        header_text.addWidget(subtitle)
        header_layout.addLayout(header_text, 1)

        # --- The card: the white box around the task ---
        self.task_name_label = QLabel(self.task.name)
        self.task_name_label.setObjectName("digitalTaskName")
        self.task_name_label.setWordWrap(True)

        self.description_label = QLabel(self.task.description)
        self.description_label.setObjectName("digitalTaskDescription")
        self.description_label.setWordWrap(True)
        # Hides the description when the task has none.
        self.description_label.setVisible(bool(self.task.description))

        # A thin line that separates the task text from the buttons.
        separator = QFrame()
        separator.setObjectName("digitalTaskSeparator")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)

        card = QFrame()
        card.setObjectName("digitalTaskCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(26, 22, 26, 22)
        card_layout.setSpacing(12)
        card_layout.addWidget(self.task_name_label)
        card_layout.addWidget(self.description_label)
        card_layout.addSpacing(4)
        card_layout.addWidget(separator)
        card_layout.addSpacing(4)
        # The buttons are stacked in this design, the same width as the card.
        for button in self.create_buttons():
            card_layout.addWidget(button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)
        layout.addWidget(header)
        layout.addWidget(card)

    def build_real_life_ui(self):
        # Real-Life Task reminder: wide, orange, buttons in a row.
        self.setWindowTitle("RemindMe - Real-Life Task")
        self.setMinimumWidth(600)

        header = QLabel("\U0001F9D8  REAL-LIFE TASK")
        header.setObjectName("realLifeTaskHeader")

        # The name in capital letters, so it is easy to read.
        self.task_name_label = QLabel(self.task.name.upper())
        self.task_name_label.setObjectName("realLifeTaskName")
        self.task_name_label.setWordWrap(True)

        self.description_label = QLabel(self.task.description)
        self.description_label.setObjectName("realLifeTaskDescription")
        self.description_label.setWordWrap(True)
        self.description_label.setVisible(bool(self.task.description))

        # In this design the three buttons are in a row.
        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        for button in self.create_buttons():
            buttons.addWidget(button)

        # The card is the white box around the task.
        card = QFrame()
        card.setObjectName("realLifeTaskCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(8)
        card_layout.addWidget(self.task_name_label)
        card_layout.addWidget(self.description_label)
        card_layout.addSpacing(14)
        card_layout.addLayout(buttons)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)
        layout.addWidget(header)
        layout.addWidget(card)

    def create_buttons(self):
        # Creates the three answers: Snooze, Complete Task and Dismiss.
        # Both designs use these same three buttons.
        self.snooze_button = QPushButton(f"Snooze {SNOOZE_MINUTES} Minutes")
        self.snooze_button.setObjectName("primaryButton")
        self.snooze_button.setMinimumHeight(BUTTON_HEIGHT)
        self.snooze_button.clicked.connect(self.snooze)

        self.complete_button = QPushButton("Complete Task")
        self.complete_button.setObjectName("secondaryButton")
        self.complete_button.setMinimumHeight(BUTTON_HEIGHT)
        self.complete_button.clicked.connect(self.complete)

        self.dismiss_button = QPushButton("Dismiss")
        self.dismiss_button.setObjectName("secondaryButton")
        self.dismiss_button.setMinimumHeight(BUTTON_HEIGHT)
        self.dismiss_button.clicked.connect(self.dismiss)

        return [self.snooze_button, self.complete_button, self.dismiss_button]

    def snooze(self):
        # The user pressed Snooze. The service starts a new countdown.
        self.answer_once(self.snoozed)

    def dismiss(self):
        # The user pressed Dismiss. The service closes the reminder.
        self.answer_once(self.dismissed)

    def complete(self):
        # The user pressed Complete Task. The service completes the SAME task.
        self.answer_once(self.completed)

    def answer_once(self, signal):
        # Sends the answer to the service, but only the first time.
        # This single check is what stops a task from being both snoozed
        # and completed, so it is written in one place and used by all
        # three buttons.
        if self.answered:
            return
        self.answered = True
        signal.emit(self)
        self.close()

    def closeEvent(self, event):
        # Closing the window with X works like Dismiss.
        if not self.answered:
            self.answered = True
            self.dismissed.emit(self)
        super().closeEvent(event)