"""service.py - the rules of the program (validation and use of the database)."""

import sqlite3
from datetime import datetime

from features.task.model import CompletedTask, Task


class TaskServiceError(Exception):
    """A problem that the user should see as a message box."""


def parse_duration(text):
    """Turns HH:MM:SS into seconds: '00:05:30' -> 330.

    Raises ValueError with a message the user can read.
    """
    cleaned = (text or "").strip()
    parts = cleaned.split(":")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValueError("Reminder time must be written as HH:MM:SS "
                         "(example: 00:05:30).")
    hours, minutes, seconds = (int(part) for part in parts)
    if minutes > 59:
        raise ValueError("Minutes (MM) must be between 00 and 59.")
    if seconds > 59:
        raise ValueError("Seconds (SS) must be between 00 and 59.")
    total = hours * 3600 + minutes * 60 + seconds
    if total <= 0:
        raise ValueError("Reminder time must be more than 00:00:00.")
    return total


def task_from_row(row):
    """Builds a Task (or a CompletedTask) from one row of the tasks table."""
    task_id, name, description, reminder_seconds, created_at, status = row
    values = dict(name=name, description=description or "",
                  reminder_seconds=reminder_seconds, task_id=task_id,
                  created_at=created_at or "", status=status)
    if status == CompletedTask.STATUS:
        return CompletedTask(**values)
    return Task(**values)


class TaskService:
    """Everything the program does with tasks: add, list, complete, delete."""

    def __init__(self, repository):
        self.repository = repository

    def create_task(self, name, description, reminder_text):
        """Checks the typed data and returns a Task that is ready to save."""
        name = (name or "").strip()
        if name == "":
            raise TaskServiceError("Please type a task name.")
        return Task(name=name, description=(description or "").strip(),
                    reminder_seconds=parse_duration(reminder_text))

    def add_task(self, task):
        """INSERT the task and keep the id that SQLite gave it."""
        task.status = Task.STATUS
        task.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            task.task_id = self.repository.add(task)
        except sqlite3.Error as error:
            raise TaskServiceError(f"Database error while saving: {error}")
        return task

    def get_tasks(self):
        """SELECT every task and turn the rows into Task objects."""
        try:
            rows = self.repository.get_all()
        except sqlite3.Error as error:
            raise TaskServiceError(f"Database error while reading: {error}")
        return [task_from_row(row) for row in rows]

    def mark_complete(self, task):
        """UPDATE one task to the status 'Completed'."""
        try:
            self.repository.update_status(task.task_id, CompletedTask.STATUS)
        except sqlite3.Error as error:
            raise TaskServiceError(f"Database error while updating: {error}")
        task.status = CompletedTask.STATUS

    def complete_all_pending(self):
        """UPDATE every pending task to 'Completed' (used when closing)."""
        try:
            self.repository.complete_all_pending()
        except sqlite3.Error as error:
            raise TaskServiceError(f"Database error while updating: {error}")

    def delete_task(self, task):
        """DELETE one task from the database."""
        try:
            self.repository.delete(task.task_id)
        except sqlite3.Error as error:
            raise TaskServiceError(f"Database error while deleting: {error}")
