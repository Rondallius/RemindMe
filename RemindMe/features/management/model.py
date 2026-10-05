import re
from dataclasses import dataclass
from datetime import datetime

from features.notification.model import DIGITAL_TASK, REAL_LIFE_TASK, TASK_TYPES


# The reminder time must be written as HH:MM:SS, with exactly two digits for
# hours, minutes and seconds. The pattern is matched against the whole text,
# so "3:3:3" and "003:03:03" are rejected, while "03:03:03" is accepted.
REMINDER_PATTERN = re.compile(r"^[0-9]{2}:[0-9]{2}:[0-9]{2}$")


# Turns HH:MM:SS into seconds. "00:05:30" becomes 330.
def parse_reminder(text):
    text = (text or "").strip()

    # Nothing was entered at all. This is checked before the format, so the
    # user is told that the reminder time is missing instead of being told
    # that the format is wrong.
    if not text:
        raise ValueError("Please input a reminder time.")

    # Hours, minutes and seconds must each have exactly two digits.
    if not REMINDER_PATTERN.match(text):
        raise ValueError("Reminder time must be written as HH:MM:SS (00:05:30).")

    hours = int(text[0:2])
    minutes = int(text[3:5])
    seconds = int(text[6:8])

    # Each problem gets its own message, so the user knows exactly what to fix.
    if minutes > 59:
        raise ValueError("Minutes must be between 00 and 59.")
    if seconds > 59:
        raise ValueError("Seconds must be between 00 and 59.")
    # The program only supports reminders inside one day, so the biggest
    # possible reminder time is 23:59:59.
    if hours > 23:
        raise ValueError("Reminder time cannot be more than 23:59:59.")

    return hours * 3600 + minutes * 60 + seconds


# Turns seconds back into HH:MM:SS, for the table and the countdown.
def seconds_to_text(total_seconds):
    seconds = max(0, int(total_seconds))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    rest = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{rest:02d}"


# Model: stores task data.
@dataclass
class Task:
    # id is the last field, because SQLite gives the id only after saving.
    name: str  # The task name.
    description: str  # Notes about the task.
    reminder_seconds: int  # The countdown time in seconds.
    task_type: str  # DIGITAL_TASK or REAL_LIFE_TASK.
    status: str = "Pending"  # Pending or Completed.
    created_at: str = ""  # Filled in automatically.
    id: int | None = None  # Set by the repository when the task is saved.

    # Runs right after the Task is created.
    # It checks the data, so a wrong task never reaches the database.
    def __post_init__(self):
        self.name = self.name.strip()
        self.description = self.description.strip()
        self.task_type = self.task_type.strip()

        if not self.name:
            raise ValueError("Task name is required.")
        if self.reminder_seconds <= 0:
            raise ValueError("Reminder time must be more than 00:00:00.")
        if self.task_type not in TASK_TYPES:
            raise ValueError(f"Task type must be {DIGITAL_TASK} or {REAL_LIFE_TASK}.")
        if self.status not in ("Pending", "Completed"):
            raise ValueError("Task status must be Pending or Completed.")

        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")