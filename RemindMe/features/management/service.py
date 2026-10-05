from .repository import TaskRepository


# Service: handles the Management logic (add, complete and delete).
# The flow is: View -> Service -> Repository -> Database.
class TaskService:
    def __init__(self, database):
        # Creates the repository that stores the tasks.
        self.repository = TaskRepository(database)

    def add_task(self, task):
        # Creates the task and saves it to the database.
        return self.repository.add(task)

    def get_tasks(self):
        # Gets all tasks, for the table.
        return self.repository.get_all()

    def complete_task(self, task):
        # Marks one task as Completed.
        task.status = "Completed"
        self.repository.update_status(task.id, task.status)

    def complete_all_tasks(self):
        # Marks all Pending tasks as Completed.
        self.repository.complete_all()

    def delete_task(self, task):
        # Removes the task from the database.
        self.repository.delete(task.id)