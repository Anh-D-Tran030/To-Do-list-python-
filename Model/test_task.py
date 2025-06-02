from Task import Task, Priority

# Create sample tasks
tasks = [
    Task("Buy groceries", "2024-06-10", Priority.LOW),
    Task("Finish project", "2024-06-05", Priority.HIGH),
    Task("Call mom", priority=Priority.MEDIUM)
]

# Test 1: Print all tasks
print("All tasks:")
for task in tasks:
    print(task)

# Test 2: Filter incomplete tasks
incomplete = [t for t in tasks if not t.completed]
print("\nIncomplete tasks:", incomplete)

# Test 3: Sort by priority (HIGH first)
sorted_tasks = sorted(tasks, reverse=True)
print("\nSorted by priority (High -> Low):")
for task in sorted_tasks:
    print(task)