from datetime import datetime
from enum import Enum


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Task:
    def __init__(self, title: str, due_date: str = None, priority: Priority = Priority.MEDIUM):
        self.title = title
        self.due_date = self.validate_date(due_date) if due_date else None
        self.priority = priority if isinstance(priority, Priority) else Priority(priority)
        self.completed = False 

    def validate_date(self, date_str : str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")
    def mark_completed(self):
        self.completed = True
    def __repr__(self):
        return f"Task('{self.title}', priority={self.priority.name}, due={self.due_date}, done={self.completed})"

    # New: Enable sorting by priority
    def __lt__(self, other):
        return self.priority.value < other.priority.value
        
    
    
