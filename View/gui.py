import tkinter as tk
from tkinter import ttk, messagebox
from Model.Task import Task, Priority
from Controller.TaskManager import TaskManager
from datetime import datetime

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Todo List App")
        self.root.geometry("700x500")

        # Initialize controller
        self.task_manager = TaskManager()

        self._setup_ui()
        self._refresh_task_list()

    def _setup_ui(self):
        """Build the GUI components"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Search and Add Task Frame
        search_add_frame = ttk.Frame(main_frame)
        search_add_frame.pack(fill="x", pady=5)

        # Search Entry
        ttk.Label(search_add_frame, text="Search/Filter:").pack(side="left", padx=2)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_add_frame, 
            textvariable=self.search_var,
            width=40
        )
        self.search_entry.pack(side="left", expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self._filter_tasks)

        # Priority selection
        self.priority_var = tk.StringVar(value="MEDIUM")
        priority_menu = ttk.OptionMenu(
            search_add_frame, self.priority_var,
            "MEDIUM", "LOW", "MEDIUM", "HIGH"
        )
        priority_menu.pack(side="left", padx=5)


        # Tag entry field
        ttk.Label(search_add_frame, text="Tag:").pack(side="left", padx=2)
        self.tag_var = tk.StringVar()
        self.tag_entry = ttk.Entry(search_add_frame, textvariable=self.tag_var, width=20)
        self.tag_entry.pack(side="left", padx=5)
        self.tag_entry.insert(0, "#work")  # default/example

        # Add Task Button
        ttk.Button(
            search_add_frame, 
            text="Add Task", 
            command=self._add_task
        ).pack(side="left", padx=5)

        # Task list treeview
        self.tree = ttk.Treeview(
            main_frame,
            columns=("Title", "Priority", "Due Date", "Status","Tags"),
            show="headings",
            selectmode="browse"
        )
        
        # Configure columns
        self.tree.heading("Title", text="Title")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Tags", text="Tags")

        self.tree.column("Title", width=250, anchor="w")
        self.tree.column("Priority", width=100, anchor="center")
        self.tree.column("Due Date", width=120, anchor="center")
        self.tree.column("Status", width=60, anchor="center")
        self.tree.column("Tags", width=100, anchor="center")
        
        self.tree.pack(fill="both", expand=True, pady=5)
        self.tree.bind("<Double-1>", self._on_double_click)  # Enable editing

        # Action buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=5)

        ttk.Button(
            button_frame, 
            text="Delete Selected", 
            command=self._delete_task
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame, 
            text="Mark Complete", 
            command=self._mark_complete
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame, 
            text="Uncheck", 
            command=self._uncheck_task
        ).pack(side="left", padx=5)

    def _refresh_task_list(self, tasks=None):
        """Update the Treeview with current tasks"""
        self.tree.delete(*self.tree.get_children())
        tasks = tasks or self.task_manager.get_tasks()

        for task in tasks:
            status = "✓" if task.completed else ""
            due_date = task.due_date.strftime("%Y-%m-%d") if task.due_date else ""
            tags_text = ", ".join(task.tags)
            
            self.tree.insert(
                "", "end",
                values=(task.title, task.priority.name, due_date, status, tags_text),
                tags=(task.priority.name,)
            )

        # Configure tag colors for priorities
        self.tree.tag_configure("HIGH", background="#ffdddd")
        self.tree.tag_configure("MEDIUM", background="#ffffdd")
        self.tree.tag_configure("LOW", background="#ddffdd")

    def _filter_tasks(self, event=None):
        """Filter tasks based on search query"""
        query = self.search_var.get().lower()
        all_tasks = self.task_manager.get_tasks()
        
        if not query:
            self._refresh_task_list(all_tasks)
            return
            
        filtered = [
            t for t in all_tasks 
            if query in t.title.lower() or 
                query in t.priority.name.lower() or
                (t.due_date and query in t.due_date.strftime("%Y-%m-%d")) or
                any(query in tag.lower() for tag in t.tags)
        ]
        self._refresh_task_list(filtered)

    def _on_double_click(self, event):
        """Handle cell editing on double-click"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column != "#4":  # Skip Status column
                self._edit_cell(event)

    def _edit_cell(self, event):
        """Edit a specific cell in the Treeview"""
        row_id = self.tree.focus()
        column = self.tree.identify_column(event.x)
        col_index = int(column[1:]) - 1
        
        # Get current value
        current_value = self.tree.item(row_id)['values'][col_index]

        
        
        # Create editable entry
        x, y, width, height = self.tree.bbox(row_id, column)
        entry = ttk.Entry(self.tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, current_value)
        entry.focus()
        
        def save_edit():
            """Save the edited value back to the model"""
            new_value = entry.get()
            self.tree.set(row_id, column, new_value)
            entry.destroy()
            
            # Update model
            task_index = self.tree.index(row_id)
            tasks = self.task_manager.get_tasks()
            
            if 0 <= task_index < len(tasks):
                task = tasks[task_index]
                
                if col_index == 0:  # Title
                    if not new_value.strip():
                        messagebox.showerror("Error", "Title cannot be empty")
                        return
                    task.title = new_value
                elif col_index == 1:  # Priority
                    try:
                        task.priority = Priority[new_value.upper()]
                    except KeyError:
                        messagebox.showerror("Error", "Invalid priority value")
                        return
                elif col_index == 2:  # Due Date
                    try:
                        if new_value:  # Only parse if not empty
                            task.due_date = datetime.strptime(new_value, "%Y-%m-%d")
                        else:
                            task.due_date = None
                    except ValueError:
                        messagebox.showerror("Error", "Date must be in YYYY-MM-DD format")
                        return
                
                self.task_manager._save_tasks()
                self._refresh_task_list()  # Refresh to update colors if priority changed
        
        entry.bind("<FocusOut>", lambda e: save_edit())
        entry.bind("<Return>", lambda e: save_edit())

    def _add_task(self):
        """Add a new task"""
        title = self.search_entry.get().strip()  # Using search entry for new tasks
        if not title:
            messagebox.showerror("Error", "Task title cannot be empty")
            return
            
        try:
            priority = Priority[self.priority_var.get()]
            tags = self.tag_var.get().strip()
            tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
            self.task_manager.add_task(title, priority=priority, tags=tag_list)

            self.search_entry.delete(0, "end")
            self.tag_entry.delete(0, "end")
            self._refresh_task_list()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _delete_task(self):
        """Delete selected task"""
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

    def _uncheck_task(self):
        """Uncheck selected task"""
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            tasks = self.task_manager.get_tasks()
            if 0 <= index < len(tasks):
                tasks[index].completed = False
                self.task_manager._save_tasks()
                self._refresh_task_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()