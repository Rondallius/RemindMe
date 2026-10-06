<h1 align="center">RemindMe</h1>

## Project Description

RemindMe: Task Reminder System is a desktop application that helps users manage tasks and remember important activities. 
Users can add a task with a name, description, reminder time, and task type. The system provides a countdown and displays 
a notification when the reminder time is reached.

The system addresses the problem of forgetting tasks and important activities. It helps users keep track of their 
tasks and reminds them when a task is due, reducing the chance of missing important activities.

---

## Project Objectives

- To manage tasks by adding, viewing, completing, and deleting them.
- To store task information such as name, description, reminder time, task type, and status.
- To provide a live countdown for active tasks.
- To notify users when a task reaches its reminder time.
- To allow users to snooze, complete, or dismiss reminders.
- To support Digital Task and Real-Life Task types with different reminder designs.
- To store task information permanently using SQLite.
- To organize the system using Model, Repository, Service, and View layers.
- To demonstrate OOP, GUI, and database concepts using Python.

---

## Features

### 1. Task Management

- **Add Task** — Creates a new task with a name, description, reminder time, and task type.
- **View Tasks** — Displays all tasks and their current information.
- **Complete Task** — Marks a task as completed and stops its countdown.
- **Delete Task** — Removes a task from the system after confirmation.

### 2. Timer

- **Start Countdown** — Starts a countdown when a task is added.
- **Track Remaining Time** — Updates the remaining time every second.
- **Detect Reminder Time** — Detects when the countdown reaches zero and triggers the notification.
- **Snooze Countdown** — Starts a new 5-minute countdown when a reminder is snoozed.

### 3. Notifications

- **Display Reminder** — Shows a notification when a task reaches its reminder time.
- **Snooze** — Delays the reminder for 5 minutes.
- **Complete Task** — Marks the task as completed and stops future reminders.
- **Dismiss** — Closes the reminder while keeping the task pending.
- **Task-Specific Notifications** — Uses different reminder designs for Digital Tasks and Real-Life Tasks.

---

## Technologies Used

| **Category** | **Technology** |
|---|---|
| Programming language | Python 3.10 or later |
| GUI framework | PyQt6 |
| Database | SQLite (built into Python through the `sqlite3` module) |
| Other libraries and tools | Qt Style Sheets (QSS), `dataclasses`, `datetime`, `pathlib`, Git and GitHub |

`sqlite3`, `dataclasses`, `datetime` and `pathlib` are part of the Python standard
library, so **PyQt6 is the only third-party package that must be installed.**

---

## Project Structure

The structure below is the actual structure of this project.

```text
RemindMe/
│
├── database/
│   └── database.py
│
├── features/
│   ├── management/
│   │   ├── model.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   ├── style.qss
│   │   └── view.py
│   │
│   ├── timer/
│   │   ├── model.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   ├── style.qss
│   │   └── view.py
│   │
│   └── notification/
│       ├── model.py
│       ├── repository.py
│       ├── service.py
│       ├── style.qss
│       └── view.py
│
├── .gitignore
├── README.md
└── main.py
```

### File and Folder Explanations

| **File / Folder** | **Purpose** |
|---|---|
| **`main.py`** | **Starts** the application and **connects** the database, services, and main window. |
| **`.gitignore`** | Lists files that should **not be tracked by Git**. |
| **`database/database.py`** | Handles the **SQLite database** and creates the **tasks table**. |
| **`features/management/model.py`** | Stores **task data** and handles **task validation**. |
| **`features/management/repository.py`** | **Handles** task data and **stores it in the database**. |
| **`features/management/service.py`** | Handles the **logic** for task management. |
| **`features/management/style.qss`** | Controls the **style of the task management interface**. |
| **`features/management/view.py`** | Displays the **task management interface**. |
| **`features/timer/model.py`** | Stores **countdown data**. |
| **`features/timer/repository.py`** | **Handles** active countdowns and **stores them in memory**. |
| **`features/timer/service.py`** | Handles the **logic** for countdowns and due tasks. |
| **`features/timer/style.qss`** | Controls the **style** of the countdown display. |
| **`features/timer/view.py`** | Displays the **active countdowns**. |
| **`features/notification/model.py`** | Stores **notification data and task types**. |
| **`features/notification/repository.py`** | **Handles** active notifications and **stores them in memory**. |
| **`features/notification/service.py`** | Handles the **logic** for notifications, Snooze, Complete, and Dismiss. |
| **`features/notification/style.qss`** | Controls the **style** of the notification windows. |
| **`features/notification/view.py`** | Displays the **Digital Task and Real-Life Task notifications**. |

---

## Installation and Setup

### Requirements

- Python 3.10 or later
- Git
- PyQt6 

### Installation

1. Clone the repository:

```bash
git clone https://github.com/Rondallius/RemindMe.git
cd RemindMe
```

2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate the virtual environment.

Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

4. Install the required dependency:

```bash
pip install PyQt6
```

5. Run the application:

```bash
python main.py
```

When setup is successful, the **RemindMe: Task Reminder System** application window opens.

---

## How to Use the System

1. Open the application. All saved tasks are loaded into the table.
2. Enter the **Name** of the task.
3. Optionally enter a **Description**.
4. Enter the **Reminder Time** as `HH:MM:SS` (for example `00:05:30`).
5. Select **Digital Task** or **Real-Life Task** in the Task Type dropdown.
6. Click **Add Task**. The task is saved and its countdown starts.
7. Watch the countdown in the **Timer** column of the table and in the countdown label
   under the table.
8. When the countdown reaches zero, the reminder window opens. Use
   **Snooze 5 Minutes**, **Complete Task** or **Dismiss**.
9. To finish a task early, select its row and click **Complete Task** in the main
   window. To remove it, select the row and click **Delete Task**.

### Notes

- A task with an invalid name or an invalid reminder time is rejected with a warning
  message, and nothing is saved.
- Completing or deleting a task also stops its countdown, so a finished task never
  reminds again.
- Closing the window asks for confirmation and then marks all remaining `Pending` tasks
  as `Completed`.

---

## OOP Implementation

The project uses a layered architecture where each feature is divided into **Model, Repository, Service, and View** layers.

```text
View → Service → Repository → Database
```

`main.py` connects the different features, including the Timer and Notification services.

### Classes and Objects

The project contains 13 important classes. A class acts as a blueprint, while an object is an instance created from that class.

| **Class** | **Purpose** |
|---|---|
| `Database` | Handles the SQLite database connection and creates the `tasks` table. |
| `Task` | Stores task data and handles task validation. |
| `Countdown` | Stores data for an active countdown. |
| `TaskRepository` | Handles task data stored in the database. |
| `TimerRepository` | Handles active countdowns stored in memory. |
| `NotificationRepository` | Handles active notifications stored in memory. |
| `TaskService` | Handles the logic for adding, reading, completing, and deleting tasks. |
| `TimerService` | Handles the countdown logic and detects when tasks are due. |
| `NotificationService` | Handles notification logic, including Snooze, Complete, and Dismiss. |
| `ManagementView` | Displays the task management interface. |
| `TimerView` | Displays the active countdowns. |
| `ReminderView` | Displays the Digital Task and Real-Life Task notifications. |
| `RemindMeWindow` | Displays the main application window and connects the main features. |

### Objects and How They Relate

The classes create objects that work together through composition and object relationships.

| **Object** | **Relationship** |
|---|---|
| `TaskRepository` | Used by `TaskService` to handle task data. |
| `TimerRepository` and `QTimer` | Used by `TimerService` to manage active countdowns. |
| `NotificationRepository` | Used by `NotificationService` to manage active notifications. |
| `TimerView` | Used by `ManagementView` to display countdown information. |
| `Task` | Stored in the task list and referenced by a `Countdown`. |
| `ReminderView` | Created by `NotificationService` for each open reminder. |

A `Countdown` keeps the same `Task` object instead of creating a new task. This allows the countdown and the task management system to work with the same task data.

### Encapsulation

Encapsulation is used by keeping data and its related operations inside their respective classes.

- `Task` validates its own data before it is saved.
- `TaskRepository` hides the SQL database operations from other parts of the program.
- `TimerRepository` hides how active countdowns are stored in memory.
- `NotificationRepository` hides how active notifications are stored in memory.
- The views use services instead of directly accessing the database.

### Inheritance

The project uses inheritance from the **PyQt6 framework**.

| **Class** | **Inherited From** |
|---|---|
| `ManagementView` | `QWidget` |
| `TimerView` | `QWidget` |
| `ReminderView` | `QWidget` |
| `RemindMeWindow` | `QDialog` |
| `TimerService` | `QObject` |
| `NotificationService` | `QObject` |

`TimerService` needs `QObject` because it declares Qt signals. `NotificationService` also inherits from `QObject` so it can work with Qt's signal and slot system.

`Task` and `Countdown` use `@dataclass` and do not inherit from custom classes. There is no custom inheritance such as `CompletedTask(Task)` in the project.

### Polymorphism

Polymorphism is used indirectly through **PyQt6** using **method overriding**.

* `RemindMeWindow` overrides `closeEvent()` to ask for confirmation before closing.
* `ReminderView` overrides `closeEvent()` so closing the window acts as **Dismiss**.
* `ManagementView` overrides `resizeEvent()` to adjust the table layout.

The project does not use custom abstract classes or its own polymorphic class hierarchy.

---

## Database

### Database Structure

RemindMe stores its data in a local SQLite database, `database/tasks.db`. The `Database` class in `database/database.py` opens the connection and creates the `tasks` table on startup if it does not exist, so the database is created automatically when the application runs.

The project creates one table: `tasks`. SQLite also automatically creates an internal `sqlite_sequence` table because the task ID uses `AUTOINCREMENT`.

### Important Tables

**tasks**: stores each task record.

| **Column** | **Type** | **Description** |
| ---------- | -------- | --------------- |
| id | INTEGER, primary key, autoincrement | Unique task ID |
| name | TEXT, required | Task name |
| description | TEXT, required | Task description |
| reminder_seconds | INTEGER, required | Reminder countdown time in seconds |
| created_at | TEXT, required | Date and time the task was created |
| status | TEXT, required, default `Pending` | Task status |
| task_type | TEXT, required, default `Digital Task` | Task type, either Digital Task or Real-Life Task |

Active countdowns and open notifications are stored temporarily in memory through `TimerRepository` and `NotificationRepository`. They are not stored in the database.

### Database Operations

| **Operation** | **What the system does** | **Example SQL** |
| ------------- | ------------------------- | ---------------- |
| Create | Adds a new task and starts its countdown | `INSERT INTO tasks (name, description, reminder_seconds, created_at, status, task_type) VALUES (?, ?, ?, ?, ?, ?)` |
| Read | Loads all tasks and displays them in the task table | `SELECT id, name, description, reminder_seconds, created_at, status, task_type FROM tasks ORDER BY id` |
| Update | Changes a task's status to `Completed` | `UPDATE tasks SET status = ? WHERE id = ?` |
| Delete | Removes a task from the database | `DELETE FROM tasks WHERE id = ?` |
| Search | Not implemented. There is no search box and no `WHERE`-based SQL search. Tasks are only retrieved in id order with `ORDER BY id`. To act on a task, the user selects a row and `ManagementView.selected_task()` uses `table.currentRow()` to return the matching `Task`. | `SELECT id, name, description, reminder_seconds, created_at, status, task_type FROM tasks ORDER BY id` |


All database values are passed using `?` parameters, keeping user input separate from the SQL statements.

---

## Screenshots

### Main Task Management Screen


<img width="947" height="669" alt="MainTaskManagementScreenshot" src="https://github.com/user-attachments/assets/ba8df7f7-0634-452d-b218-baf7dde8259c" />


*Shows the main RemindMe window: the blue header with the Exit button, the Add Task form
(Name, Reminder Time, Task Type, Description), the Add Task / Complete Task / Delete Task
buttons, the task table with the columns ID, Name, Description, Timer, Type and Status,
and the countdown label under the table.*

### Digital Task Notification


<img width="511" height="478" alt="DigitalTaskNotification" src="https://github.com/user-attachments/assets/cccc4d1b-6852-4ba4-aaf2-fa3bd32976d8" />


*Shows the blue Digital Task reminder window that appears when a task with the type
`Digital Task` reaches its reminder time. It has a blue header, a white card with the
task name and description, and the Snooze / Complete Task / Dismiss buttons stacked under
each other.*

### Real-Life Task Notification


<img width="593" height="346" alt="RealLifeTaskNotification" src="https://github.com/user-attachments/assets/9f8c245d-3b98-4ef4-b729-01cf266e258a" />



*Shows the orange Real-Life Task reminder window that appears when a task with the type
`Real-Life Task` reaches its reminder time. It has an orange header, the task name in
capital letters on a highlighted background, and the three buttons in a row.*

---

## Testing

The system was tested manually by running the application and checking each major feature.

| **#** | **Feature** | **Test** | **Expected Result** | **Actual Result** | **Status** |
| ----- | ----------- | -------- | ------------------- | ----------------- | ---------- |
| 1 | Task Management | Add a task with a name, description, reminder time, and task type | Task appears in the table with `Pending` status | Task was added with the correct information and `Pending` status | Pass |
| 2 | Task Management | Read and display saved tasks | Saved tasks appear in the task table | Saved tasks were loaded and displayed in the table | Pass |
| 3 | Task Management | Complete a selected task | Status changes to `Completed` and the countdown stops | Selected task changed to `Completed` and its countdown stopped | Pass |
| 4 | Task Management | Delete a selected task and confirm | Task is removed from the table and database | Task disappeared from the table after confirmation and was removed from the database | Pass |
| 5 | Validation | Enter an invalid reminder time such as `3:3:3` | Task is rejected with a warning message | Warning showed `Reminder time must be written as HH:MM:SS (00:05:30).` | Pass |
| 6 | Validation | Leave the task name empty | Task is rejected with a warning message | Warning showed `Please input a task name.` | Pass |
| 7 | Timer | Add a task with a short reminder time | Countdown starts and decreases every second | Countdown showed `00:00:03`, then `00:00:02` as time decreased | Pass |
| 8 | Timer | Allow the countdown to reach zero | Countdown stops and the reminder is triggered | Countdown reached zero and opened the reminder window | Pass |
| 9 | Notifications | Trigger a Digital Task reminder | Digital Task notification window appears | `RemindMe - Digital Task` notification window appeared | Pass |
| 10 | Notifications | Trigger a Real-Life Task reminder | Real-Life Task notification window appears | `RemindMe - Real-Life Task` notification window appeared | Pass |
| 11 | Notifications | Click Snooze | Reminder closes and a new 5-minute countdown starts | Reminder closed and the task countdown restarted at 5 minutes | Pass |
| 12 | Notifications | Click Complete Task from a reminder | Task becomes `Completed`, countdown stops, and notification closes | Task changed to `Completed`, countdown stopped, and notification closed | Pass |
| 13 | Notifications | Click Dismiss | Reminder closes while the task remains `Pending` | Reminder closed and the task remained `Pending` | Pass |
| 14 | Notifications | Trigger the same task again while its notification is already open | Only one notification window should remain open | Duplicate notification was prevented and only one reminder window remained open | Pass |
| 15 | Database | Restart the application after saving tasks | Saved task records should still exist | Previously saved tasks remained in the SQLite database after restarting | Pass |
| 16 | Exit Behavior | Close the application and confirm the exit dialog | Pending tasks become `Completed` | Confirming the exit marked all remaining `Pending` tasks as `Completed` | Pass |

---

## Known Issues / Limitations

These are the real limitations of the current implementation.

1. **No dedicated task search.** There is no search box and no SQL search feature. Tasks are listed in id order and can only be selected row by row.

2. **Countdowns are not stored in SQLite.** `TimerRepository` keeps them in memory, so restarting the program reloads the tasks but does **not** resume their countdowns; the Timer column then shows the original reminder time again.

3. **Notification state is temporary.** Open reminder windows exist only while the program is running and are cleared when it closes.

4. **The database is local.** It is a single SQLite file on the same computer; there is no shared or remote database, and no user accounts or login.

5. **No automated test suite.** The project has no test files or test framework; testing was done manually.

6. **Editing is not possible in the table.** The table is read-only by design; changing a task means deleting it and adding it again.

7. **A reminder time must be at least one second.** `00:00:00` is rejected with `Reminder time must be more than 00:00:00.`, and the upper limit is `23:59:59`.

8. **No repeat or recurring reminders.** Each task triggers exactly once.

9. **Closing the program completes every pending task.** When the user confirms the exit dialog, all remaining `Pending` tasks are marked as `Completed`.

---

## Author

**Name:** Rondel Jay M. Gerasmio

**Section:** CS26L (3581)

