from src.tasks.main import celery_app


# define task here
@celery_app.task(name="add_task")
def add_task(x: int, y: int):
    return x + y
