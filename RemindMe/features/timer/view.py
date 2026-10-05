from pathlib import Path

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from features.management.model import seconds_to_text


# View: shows all the running countdowns.
class TimerView(QWidget):
    def __init__(self, service):
        super().__init__()
        self.setObjectName("timerView")
        self.service = service
        self.build_ui()
        self.setStyleSheet(Path(__file__).with_name("style.qss").read_text())
        self.refresh()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel()
        self.label.setObjectName("countdownLabel")
        layout.addWidget(self.label)

    def refresh(self):
        # Shows every countdown, for example:
        # "Countdown: Study Math 00:04:58 | Buy milk 00:04:30 (snoozed)"
        countdowns = self.service.get_countdowns()
        if not countdowns:
            self.label.setText("Countdown: none")
            return

        texts = []
        for countdown in countdowns:
            # "(snoozed)" means this countdown came from the Snooze button.
            mark = " (snoozed)" if countdown.is_snooze else ""
            texts.append(
                countdown.task.name + " " + seconds_to_text(countdown.seconds_left) + mark
            )

        self.label.setText("Countdown: " + "   |   ".join(texts))