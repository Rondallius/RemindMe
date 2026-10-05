from PyQt6.QtCore import QObject

from .repository import NotificationRepository
from .view import ReminderView


# Service: shows the reminder and handles the answer of the user.
#
# The Timer feature counts the time and says "this task is due".
# The Notification feature shows the reminder and reacts to Snooze,
# Complete Task or Dismiss. They are two features because counting time
# and reacting to the user are two different jobs.
class NotificationService(QObject):
    def __init__(self, timer_service, task_service):
        super().__init__()
        # Used to start a new countdown when the user snoozes.
        self.timer_service = timer_service
        # Used by "Complete Task" to mark the same task as Completed.
        # It is the existing Management service, so there is only one
        # completion system in the whole program.
        self.task_service = task_service
        # Keeps the ids of the reminders that are open.
        self.repository = NotificationRepository()
        # Keeps the reminder windows, so they can all be closed later.
        self.open_windows = []

    def show_reminder(self, task):
        # The Timer feature says this task is due, so the reminder is shown.
        # The task type decides which of the two reminder designs is used.
        if self.repository.has(task.id):
            # This task already has a reminder open, so it is not shown twice.
            return

        window = ReminderView(task)
        # The view only reports the answer. The service does the real work.
        window.snoozed.connect(self.snooze)
        window.dismissed.connect(self.dismiss)
        window.completed.connect(self.complete)

        self.open_windows.append(window)
        self.repository.add(task.id)

        # Shows the window and brings it to the front so it is noticed.
        window.show()
        window.raise_()
        window.activateWindow()

    def snooze(self, window):
        # The user pressed "Snooze 5 Minutes":
        # close the reminder and start a new 5-minute countdown for the
        # SAME task. The same task object is reused, so no second task
        # is created in the database.
        task = window.task
        self.close_window(window)

        # While the reminder was open, the task could already have been
        # completed or deleted in the main window. Only a task that is still
        # Pending may be snoozed, otherwise a finished task would be
        # reminded a second time.
        if not self.is_still_pending(task):
            return

        self.timer_service.snooze(task)

    def is_still_pending(self, task):
        # Asks the Management service whether the task is still in the
        # database and still waiting to be done.
        return any(
            saved.id == task.id and saved.status == "Pending"
            for saved in self.task_service.get_tasks()
        )

    def complete(self, window):
        # The user pressed "Complete Task":
        # close the reminder, mark the SAME task as Completed and stop its
        # countdown, so the task can never remind again.
        task = window.task
        self.close_window(window)
        self.task_service.complete_task(task)
        self.timer_service.stop_countdown(task.id)

    def dismiss(self, window):
        # The user pressed "Dismiss":
        # close the reminder only. The task stays Pending
        # and no new countdown starts.
        self.close_window(window)

    def close_window(self, window):
        # Removes the reminder from memory and closes its window.
        task = window.task
        if window in self.open_windows:
            self.open_windows.remove(window)
        self.repository.delete(task.id)
        window.close()
        window.deleteLater()

    def close_all(self):
        # Closes every reminder window when the program closes.
        # answered is set first, so the windows do not answer again.
        for window in list(self.open_windows):
            window.answered = True
            self.close_window(window)