"""repository.py - the SQL of the program (INSERT, SELECT, UPDATE, DELETE)."""


class TaskRepository:
    """Saves and reads the tasks in the tasks table."""

    def __init__(self, database):
        self.database = database

    def add(self, task):
        """INSERT - saves one task and returns the id SQLite gave it."""
        sql = ("INSERT INTO tasks "
               "(name, description, reminder_seconds, created_at, status) "
               "VALUES (?, ?, ?, ?, ?)")
        with self.database.connect() as connection:
            cursor = connection.execute(
                sql,
                (task.name, task.description, task.reminder_seconds,
                 task.created_at, task.status))
            return cursor.lastrowid

    def get_all(self):
        """SELECT - returns every task as a list of rows."""
        sql = ("SELECT id, name, description, reminder_seconds, created_at, "
               "status FROM tasks ORDER BY id")
        with self.database.connect() as connection:
            return connection.execute(sql).fetchall()

    def update_status(self, task_id, status):
        """UPDATE - changes the status of one task."""
        sql = "UPDATE tasks SET status = ? WHERE id = ?"
        with self.database.connect() as connection:
            connection.execute(sql, (status, task_id))

    def complete_all_pending(self):
        """UPDATE - finishes every task that is still pending."""
        sql = "UPDATE tasks SET status = 'Completed' WHERE status = 'Pending'"
        with self.database.connect() as connection:
            connection.execute(sql)

    def delete(self, task_id):
        """DELETE - removes one task from the table."""
        sql = "DELETE FROM tasks WHERE id = ?"
        with self.database.connect() as connection:
            connection.execute(sql, (task_id,))
