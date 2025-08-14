from scripts import email_handle
from threading import Thread
from datetime import datetime
import traceback,os
from django.conf import settings

class ErrorHandler:
    """
    Handles exceptions by logging error details to timestamped daily files. sends asynchronous email notifications to an admin with the log attached.

    Attributes:
        NOTIFY_EMAIL (str): Email address to receive error notifications.
        notify (bool): Whether to send email notifications on errors.

    Methods:
        handle(error, context=""): Logs error info and triggers notification if enabled.
        notify_admin(file_path): Sends an email with the error log attachment asynchronously.
    """
    NOTIFY_EMAIL = 'dwomohaustin14@gmail.com'

    def __init__(self, notify=True):
        
        self.notify = notify
        os.makedirs(settings.LOG_BASE_DIR, exist_ok=True)  

    def handle(self, error, context=""):
        """
        Handles exceptions by logging error details to a timestamped file 
        and optionally notifying the admin via email.

        Args:
            error (Exception): The caught exception.
            context (str): Optional context string describing where the error occurred.
        """
        now = datetime.now()
        day_folder = now.strftime("%Y-%m-%d")
        time_stamp = now.strftime("%H-%M-%S")

        folder_path = os.path.join(settings.LOG_BASE_DIR, day_folder)
        os.makedirs(folder_path, exist_ok=True)  
        file_path = os.path.join(folder_path, f"error_{time_stamp}.txt")

        error_message = (
            f"Timestamp: {now}\n"
            f"Context: {context}\n"
            f"Exception: {str(error)}\n\n"
            f"Traceback:\n{traceback.format_exc()}\n"
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(error_message)

        if self.notify:
            self.notify_admin(file_path)

    def notify_admin(self, file_path):
        """
        Sends an email to the admin with the error log attached.
        Runs asynchronously in a separate thread.

        Args:
            file_path (str): Path to the error log file to attach.
        """
        subject = '[ALERT] Server Error Notification'
        body = 'An error occurred. Please see the attached log file.'
        
        to_email = self.NOTIFY_EMAIL

        Thread(target=email_handle.send_email_with_attachment, kwargs={"subject": subject,"body": body,"to_email": to_email,"file_path": file_path,}).start()
        