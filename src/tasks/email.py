from src.tasks.main import celery_app
from src.utils.mailer import send_email


# define task here
@celery_app.task(name="send_email_task")
def send_email_task(recipient: str, subject: str, content: str):
    send_email(recipient=recipient, subject=subject, content=content)

    status = "sent"
    return status
