from View.gui import TodoApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()