import json
import logging
from datetime import datetime
from pathlib import Path

TASK_FILE = Path("data/tasks.json")


def load_tasks() -> list[dict]:
    """Load tasks from JSON file."""
    if not TASK_FILE.exists():
        TASK_FILE.parent.mkdir(parents=True, exist_ok=True)
        return []
    try:
        return json.loads(TASK_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logging.exception("tasks.json is corrupt — terugvallen op lege lijst")
        return []


def save_tasks(tasks: list[dict]) -> None:
    """Save tasks to JSON file."""
    TASK_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def add_task(title: str, description: str, priority: str) -> None:
    """Add a new task."""
    tasks = load_tasks()
    tasks.append(
        {
            "id": len(tasks) + 1,
            "title": title,
            "description": description,
            "priority": priority,
            "completed": False,
            "created_at": datetime.now().isoformat(),
        }
    )
    save_tasks(tasks)


def get_tasks() -> list[dict]:
    """Get all tasks."""
    return load_tasks()


def update_task_status(task_id: int, completed: bool) -> None:
    """Update task completion status."""
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = completed
            break
    save_tasks(tasks)


def delete_task(task_id: int) -> None:
    """Delete a task by ID."""
    tasks = [t for t in load_tasks() if t["id"] != task_id]
    save_tasks(tasks)
