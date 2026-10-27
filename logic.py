import database

def add_smart_task(title):
    clean_title = title.strip()
    if not clean_title:
        return {"success": False, "error": "Название задачи не может быть пустым!"}

    current_tasks = database.get_all_tasks()
    for task in current_tasks:
        if task[1].lower().strip() == clean_title.lower():
            return {"success": False, "error": "Такая задача уже существует!"}
            
    database.add_task(clean_title)
    return {"success": True, "error": None}

def get_dashboard_stats():
    tasks = database.get_all_tasks()
    total = len(tasks)
    completed = sum(1 for task in tasks if task[2] == 'done')
    not_completed = total - completed
    
    return {
        "total": total,
        "completed": completed,
        "not_completed": not_completed
    }

def change_task_status(task_id, new_status):
    if new_status in ["done", "new"]:
        return database.update_task_status(task_id, new_status)
    return False
