import json
from pathlib import Path
from datetime import datetime
from Model.Task import Task, Priority

class TaskManager:
    def __init__(self, data_file: str = "tasks.json"):
        self.data_file = Path(data_file)
        self.tasks = self._load_tasks()
    
    def _load_tasks(self) -> list[Task]:
        """Load tasks from JSON file with enhanced error handling"""
        try:
            if not self.data_file.exists():
                return []
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tasks = []
                for task_data in data:
                    try:
                        task = Task(
                            title=task_data.get('title', ''),
                            due_date=task_data.get('due_date'),
                            priority=Priority[task_data.get('priority', 'MEDIUM')]
                        )
                        if task_data.get('completed', False):
                            task.mark_completed()
                        tasks.append(task)
                    except (KeyError, ValueError) as e:
                        print(f"Skipping invalid task: {e}")
                return tasks
        except Exception as e:
            print(f"Error loading tasks: {e}")
            return []

    def _save_tasks(self):
        """Save tasks to JSON file with atomic write"""
        try:
            temp_file = self.data_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump([{
                    'title': task.title,
                    'due_date': task.due_date.strftime("%Y-%m-%d") if task.due_date else None,
                    'priority': task.priority.name,
                    'completed': task.completed
                } for task in self.tasks], f, indent=2)
            
            # Atomic replace
            temp_file.replace(self.data_file)
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def add_task(self, title: str, due_date: str = None, priority: Priority = Priority.MEDIUM) -> Task:
        """Add a new task with validation"""
        if not title.strip():
            raise ValueError("Task title cannot be empty")
            
        try:
            parsed_date = datetime.strptime(due_date, "%Y-%m-%d") if due_date else None
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
        
        task = Task(title=title, due_date=due_date, priority=priority)
        self.tasks.append(task)
        self._save_tasks()
        return task

    def delete_task(self, index: int) -> bool:
        """Delete task by index, returns success status"""
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self._save_tasks()
            return True
        return False

    def get_tasks(self, filter_completed: bool = None, search_query: str = None) -> list[Task]:
        """Get tasks with optional filtering"""
        tasks = self.tasks
        
        if filter_completed is not None:
            tasks = [t for t in tasks if t.completed == filter_completed]
            
        if search_query:
            query = search_query.lower()
            tasks = [
                t for t in tasks
                if (query in t.title.lower() or
                    query in t.priority.name.lower() or
                    (t.due_date and query in t.due_date.strftime("%Y-%m-%d")))
            ]
            
        return tasks

    def update_task(self, index: int, **kwargs) -> bool:
        """Update task attributes"""
        if not 0 <= index < len(self.tasks):
            return False
            
        task = self.tasks[index]
        
        if 'title' in kwargs:
            if not kwargs['title'].strip():
                raise ValueError("Title cannot be empty")
            task.title = kwargs['title']
            
        if 'priority' in kwargs:
            try:
                task.priority = Priority[kwargs['priority'].upper()]
            except KeyError:
                raise ValueError("Invalid priority value")
                
        if 'due_date' in kwargs:
            try:
                task.due_date = (datetime.strptime(kwargs['due_date'], "%Y-%m-%d") 
                                if kwargs['due_date'] else None)
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
                
        if 'completed' in kwargs:
            if kwargs['completed']:
                task.mark_completed()
            else:
                task.completed = False
                
        self._save_tasks()
        return True

    def clear_completed(self) -> int:
        """Remove all completed tasks, returns count removed"""
        initial_count = len(self.tasks)
        self.tasks = [t for t in self.tasks if not t.completed]
        removed = initial_count - len(self.tasks)
        if removed > 0:
            self._save_tasks()
        return removed