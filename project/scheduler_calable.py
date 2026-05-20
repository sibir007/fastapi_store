from datetime import datetime


def tick(task_id: str, optional_mes: str | None):
    
    mess = f', optional mesage: {optional_mes},' if optional_mes else ""

    print(f"Hello, task id: {task_id}{mess} the time is", datetime.now())
