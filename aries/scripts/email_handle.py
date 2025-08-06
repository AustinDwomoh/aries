import os, smtplib, logging
from email.message import EmailMessage
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)

def send_email_with_attachment(subject, body, to_email, file_path=None, from_email=None,html_content=None):
    from_email = f"Aries Project <{settings.DEFAULT_FROM_EMAIL}>"
    fallback_path = os.path.join(settings.LOG_BASE_DIR, "logs", "notify_failures.txt")

    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_email
        if isinstance(to_email, (list, tuple)):
            msg['To'] = ", ".join(to_email)
        else:
            msg['To'] = to_email
        msg.set_content(body)
        if html_content:
            msg.add_alternative(html_content, subtype='html')
        if file_path and os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(file_path)
                msg.add_attachment(
                    file_data,
                    maintype='text',
                    subtype='plain',
                    filename=file_name
                )

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(settings.GMAIL_USER, settings.GMAIL_PASSWORD)
            smtp.send_message(msg)

    except Exception as e:
        try:
            os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
            with open(fallback_path, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()} - Failed to notify admin: {str(e)}\n")
        except Exception as fallback_err:
            logger.critical(f"Failed to write fallback notify log: {fallback_err}")
