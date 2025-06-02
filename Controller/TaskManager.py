import json
from pathlib import Path
from Model.Task import Task, Priority

class TaskManager:
    def __init__(self, data_file: str = "tasks.json"):
        self.data_file = Path(data_file)
        self.tasks = self._load_tasks()
    
    def _load_tasks(self) -> list[Task]:
        """Load tasks from JSON file"""
        if not self.data_file.exists():
            return []
        
        with open(self.data_file, 'r') as f:
            data = json.load(f)
            return [Task(
                title=task['title'],
                due_date=task['due_date'],
                priority=Priority[task['priority']]
            ) for task in data]
    
    def _save_tasks(self):
        """Save tasks to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump([{
                'title': task.title,
                'due_date': str(task.due_date) if task.due_date else None,
                'priority': task.priority.name,
                'completed': task.completed
            } for task in self.tasks], f, indent=2)
    
    def add_task(self, title: str, due_date: str = None, priority: Priority = Priority.MEDIUM):
        """Add a new task"""
        self.tasks.append(Task(title, due_date, priority))
        self._save_tasks()
    
    def delete_task(self, index: int):
        """Delete task by index"""
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self._save_tasks()
    
    def get_tasks(self) -> list[Task]:
        """Get all tasks"""
        return self.tasks