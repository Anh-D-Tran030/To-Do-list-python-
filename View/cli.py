import tkinter as tk
from tkinter import ttk
from Model.Task import Task, Priority

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Todo List App")
        self.root.geometry("500x400")
        
        # Task list (will connect to Controller later)
        self.tasks = [
            Task("Buy milk", "2024-06-10", Priority.LOW),
            Task("Finish project", "2024-06-05", Priority.HIGH)
        ]
        
        self._setup_ui()

    def _setup_ui(self):
        """Build the GUI components."""
        # Task entry frame
        entry_frame = ttk.Frame(self.root)
        entry_frame.pack(pady=10, padx=10, fill="x")
        
        self.task_entry = ttk.Entry(entry_frame, width=40)
        self.task_entry.pack(side="left", expand=True)
        
        ttk.Button(entry_frame, text="Add", command=self._add_task).pack(side="left", padx=5)
        
        # Task list treeview
        self.tree = ttk.Treeview(
            self.root, 
            columns=("Priority", "Due Date", "Status"), 
            show="headings"
        )
        self.tree.heading("#0", text="Task")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.heading("Status", text="Status")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Delete button
        ttk.Button(self.root, text="Delete Selected", command=self._delete_task).pack(pady=10)
        
        self._refresh_task_list()

    def _refresh_task_list(self):
        """Update the Treeview with current tasks."""
        self.tree.delete(*self.tree.get_children())
        for task in self.tasks:
            status = "✓" if task.completed else " "
            self.tree.insert(
                "", "end", 
                text=task.title,
                values=(task.priority.name, task.due_date, status)
            )

    def _add_task(self):
        """Add a new task from the entry field."""
        title = self.task_entry.get()
        if title:
            self.tasks.append(Task(title))  # Simple add (will enhance later)
            self.task_entry.delete(0, "end")
            self._refresh_task_list()

    def _delete_task(self):
        """Remove selected task."""
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            del self.tasks[index]
            self._refresh_task_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()