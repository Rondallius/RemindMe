from .model import Task


# Repository: handles the database operations.
# It only reads and writes rows. The rules are in the model and the service.
# Every method does the same three steps: open, run the SQL, save and close.
class TaskRepository:
    def __init__(self, database):
        # Keeps the Database object, to open connections.
        self.database = database

    def add(self, task):
        # Saves a new task to the database.
        # The ? marks send the values separately, so user input cannot
        # change the SQL.
        connection = self.database.connect()
        cursor = connection.execute(
            """
            INSERT INTO tasks
                (name, description, reminder_seconds, created_at, status, task_type)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                task.name,
                task.description,
                task.reminder_seconds,
                task.created_at,
                task.status,
                task.task_type,
            ),
        )
        connection.commit()

        # SQLite gives the new id. It is stored on the task object, so the
        # Timer can use it to start the countdown of this task.
        task.id = cursor.lastrowid
        connection.close()
        return task

    def get_all(self):
        # Gets all tasks from the database, oldest task first.
        connection = self.database.connect()
        rows = connection.execute(
            """
            SELECT id, name, description, reminder_seconds, created_at, status, task_type
            FROM tasks
            ORDER BY id
            """
        ).fetchall()
        connection.close()

        # Turns every database row into a Task object.
        tasks = []
        for row in rows:
            task = Task(
                id=row[0],
                name=row[1],
                description=row[2],
                reminder_seconds=row[3],
                created_at=row[4],
                status=row[5],
                task_type=row[6],
            )
            tasks.append(task)
        return tasks

    def update_status(self, task_id, status):
        # Updates the status of one task.
        connection = self.database.connect()
        connection.execute(
            "UPDATE tasks SET status = ? WHERE id = ?", (status, task_id)
        )
        connection.commit()
        connection.close()

    def complete_all(self):
        # Updates all Pending tasks at once.
        connection = self.database.connect()
        connection.execute(
            "UPDATE tasks SET status = ? WHERE status = ?", ("Completed", "Pending")
        )
        connection.commit()
        connection.close()

    def delete(self, task_id):
        # Removes one task from the database.
        connection = self.database.connect()
        connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        connection.commit()
        connection.close()