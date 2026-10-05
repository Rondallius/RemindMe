from dataclasses import dataclass

from features.management.model import Task


# Model: stores the data of one running countdown.
@dataclass
class Countdown:
    # The service only creates a countdown with at least one second.
    task: Task  # The task this countdown belongs to.
    seconds_left: int  # The time left in seconds.
    is_snooze: bool = False  # True when the countdown came from Snooze.