import json
from datetime import datetime
from pathlib import Path

TASK_FILE = Path("data/tasks.json")


def load_tasks():
    """Load tasks from JSON file."""
    if not TASK_FILE.exists():
        TASK_FILE.parent.mkdir(parents=True, exist_ok=True)
        return []

    try:
        return json.loads(TASK_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_tasks(tasks):
    """Save tasks to JSON file."""
    TASK_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def add_task(title, description, priority):
    """Add a new task."""
    tasks = load_tasks()
    new_task = {
        "id": len(tasks) + 1,
        "title": title,
        "description": description,
        "priority": priority,
        "completed": False,
        "created_at": datetime.now().isoformat(),
    }
    tasks.append(new_task)
    save_tasks(tasks)


def get_tasks():
    """Get all tasks."""
    return load_tasks()


def update_task_status(task_id, completed):
    """Update task completion status."""
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = completed
            break
    save_tasks(tasks)


def delete_task(task_id):
    """Delete a task by ID."""
    tasks = load_tasks()
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
