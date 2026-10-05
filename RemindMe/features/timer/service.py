from PyQt6.QtCore import QObject, QTimer, pyqtSignal

# The snooze length is defined once, in the Notification feature.
from features.notification.model import SNOOZE_SECONDS
from .model import Countdown
from .repository import TimerRepository


# Service: handles the countdowns and detects when a task is due.
# The Timer counts the time. The Notification feature shows the reminder.
class TimerService(QObject):
    # Sent when a countdown reaches zero.
    # Notification listens to it and shows the reminder.
    reminder_due = pyqtSignal(object)

    # Sent every second, so the screen can show the new time.
    countdown_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Keeps the running countdowns in memory.
        self.repository = TimerRepository()
        # One clock for all the countdowns. It ticks once per second.
        self.clock = QTimer(self)
        self.clock.setInterval(1000)
        self.clock.timeout.connect(self.tick)

    def start_countdown(self, task):
        # Starts the countdown of a new task.
        self.save_countdown(task, task.reminder_seconds)

    def snooze(self, task):
        # Starts a new 5-minute countdown for the SAME task.
        self.save_countdown(task, SNOOZE_SECONDS, True)

    def stop_countdown(self, task_id):
        # Stops the countdown of a completed or deleted task.
        self.repository.delete(task_id)
        self.update_clock()

    def stop_all(self):
        # Stops every countdown, for example when the program closes.
        self.repository.clear()
        self.clock.stop()
        self.countdown_updated.emit()

    def get_seconds_left(self, task_id):
        # Returns the time left of a task, or None if it has no countdown.
        countdown = self.repository.get(task_id)
        if countdown is None:
            return None
        return countdown.seconds_left

    def get_countdowns(self):
        # Returns all the running countdowns.
        return self.repository.get_all()

    def save_countdown(self, task, seconds, is_snooze=False):
        # Saves a countdown and starts the clock if it is not running.
        countdown = Countdown(task, seconds, is_snooze)
        self.repository.add(task.id, countdown)
        if not self.clock.isActive():
            self.clock.start()
        self.countdown_updated.emit()

    def tick(self):
        # Runs once per second: takes one second off every countdown.
        # get_all() gives a copy of the list, so it is safe to remove a
        # countdown while we are still going through the list.
        for countdown in self.repository.get_all():
            countdown.seconds_left = countdown.seconds_left - 1

            if countdown.seconds_left <= 0:
                # The time is up. The countdown is stopped first, so the same
                # task cannot be reminded twice.
                self.repository.delete(countdown.task.id)
                # Sends a signal: "this task is due".
                # The Notification feature shows the reminder.
                self.reminder_due.emit(countdown.task)

        self.update_clock()

    def update_clock(self):
        # Stops the clock when no countdowns are left,
        # and tells the screen to refresh.
        if not self.repository.get_all():
            self.clock.stop()
        self.countdown_updated.emit()