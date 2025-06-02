import tkinter as tk
from tkinter import ttk
from Model.Task import Task, Priority
from Controller.TaskManager import TaskManager

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Todo List App")
        self.root.geometry("600x450")
        
        # Initialize controller
        self.task_manager = TaskManager()
        
        self._setup_ui()
        self._refresh_task_list()

    def _setup_ui(self):
        """Build the GUI components"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Task entry frame
        entry_frame = ttk.Frame(main_frame)
        entry_frame.pack(fill="x")
        
        self.task_entry = ttk.Entry(entry_frame, width=40)
        self.task_entry.pack(side="left", expand=True, padx=5)
        
        # Priority selection
        self.priority_var = tk.StringVar(value="MEDIUM")
        priority_menu = ttk.OptionMenu(
            entry_frame, self.priority_var,
            "MEDIUM", "LOW", "MEDIUM", "HIGH"
        )
        priority_menu.pack(side="left", padx=5)
        
        ttk.Button(entry_frame, text="Add", command=self._add_task).pack(side="left", padx=5)
        
        # Task list treeview
        self.tree = ttk.Treeview(
            main_frame, 
            columns=("Priority", "Due Date", "Status"), 
            show="headings",
            selectmode="browse"
        )
        self.tree.heading("#0", text="Task")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.heading("Status", text="Status")
        self.tree.column("#0", width=250)
        self.tree.column("Priority", width=100)
        self.tree.column("Due Date", width=100)
        self.tree.column("Status", width=50)
        self.tree.pack(fill="both", expand=True, pady=10)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Delete Selected", command=self._delete_task).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Mark Complete", command=self._mark_complete).pack(side="left", padx=5)

    def _refresh_task_list(self):
        """Update the Treeview with current tasks"""
        self.tree.delete(*self.tree.get_children())
        for task in self.task_manager.get_tasks():
            status = "✓" if task.completed else " "
            self.tree.insert(
                "", "end", 
                text=task.title,
                values=(task.priority.name, task.due_date, status),
                tags=(task.priority.name,)
            )
        
        # Configure tag colors for priorities
        self.tree.tag_configure("HIGH", background="#ffdddd")
        self.tree.tag_configure("MEDIUM", background="#ffffdd")
        self.tree.tag_configure("LOW", background="#ddffdd")

    def _add_task(self):
        """Add a new task from the entry field"""
        title = self.task_entry.get()
        if title:
            priority = Priority[self.priority_var.get()]
            self.task_manager.add_task(title, priority=priority)
            self.task_entry.delete(0, "end")
            self._refresh_task_list()

    def _delete_task(self):
        """Remove selected task"""
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            self.task_manager.delete_task(index)
            self._refresh_task_list()

    def _mark_complete(self):
        """Mark selected task as complete"""
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            tasks = self.task_manager.get_tasks()
            if 0 <= index < len(tasks):
                tasks[index].mark_completed()
                self.task_manager._save_tasks()
                self._refresh_task_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()