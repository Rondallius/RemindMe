# Repository: keeps the active notifications in memory.
# A reminder only exists while the program runs, so there is no table for it.
#
# The Notification feature is separate from the Timer feature:
# the Timer counts the time, the Notification shows the reminder
# and handles the answer of the user.
class NotificationRepository:
    def __init__(self):
        # The ids of the tasks that have a reminder window open.
        self.task_ids = []

    def add(self, task_id):
        # Called when a reminder is shown.
        self.task_ids.append(task_id)

    def has(self, task_id):
        # Prevents a duplicate reminder for the same task.
        return task_id in self.task_ids

    def delete(self, task_id):
        # Called when the reminder is closed (Snooze, Complete or Dismiss).
        if task_id in self.task_ids:
            self.task_ids.remove(task_id)

    def clear(self):
        # Called when the program closes.
        self.task_ids.clear()