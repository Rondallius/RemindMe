"""model.py - the data of one task."""

from dataclasses import dataclass


@dataclass
class Task:
    """One task of the list."""

    STATUS = "Pending"

    name: str
    description: str = ""
    reminder_seconds: int = 0
    task_id: int | None = None
    created_at: str = ""
    status: str = "Pending"

    def is_completed(self):
        return self.status == CompletedTask.STATUS

    def status_label(self):
        """Text shown in the Status column."""
        return self.STATUS

    def countdown_seconds(self):
        """How many seconds this task counts down."""
        return self.reminder_seconds

    def reminder_text(self):
        """The reminder time as HH:MM:SS, for example 00:05:30."""
        return seconds_to_text(self.reminder_seconds)

    def alarm_message(self):
        """Text of the reminder popup."""
        return f"\U0001F514 Reminder: {self.name} - Time is up!"


class CompletedTask(Task):
    """A task the user has finished: it never counts down again."""

    STATUS = "Completed"

    def status_label(self):
        return self.STATUS

    def countdown_seconds(self):
        return 0

    def alarm_message(self):
        return f"Reminder: {self.name} was already completed."


def seconds_to_text(total_seconds):
    """Turns seconds into HH:MM:SS text: 90 -> '00:01:30'."""
    seconds = max(0, int(total_seconds))
    hours, rest = divmod(seconds, 3600)
    minutes, rest = divmod(rest, 60)
    return f"{hours:02d}:{minutes:02d}:{rest:02d}"
