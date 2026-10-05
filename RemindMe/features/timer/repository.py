# Repository: keeps the active countdowns in memory.
# Countdowns are temporary, so they are not saved in the database.
# The key is the task id, so every task has at most one countdown.
class TimerRepository:
    def __init__(self):
        self.countdowns = {}

    def add(self, task_id, countdown):
        # Saves a countdown. The same task id is used again when it restarts.
        self.countdowns[task_id] = countdown

    def get(self, task_id):
        # Returns the countdown of a task, or None if it has none.
        return self.countdowns.get(task_id)

    def get_all(self):
        # Returns a copy of all the countdowns.
        return list(self.countdowns.values())

    def delete(self, task_id):
        # Removes the countdown when it ends or the task is completed
        # or deleted.
        self.countdowns.pop(task_id, None)

    def clear(self):
        # Removes all the countdowns.
        self.countdowns.clear()