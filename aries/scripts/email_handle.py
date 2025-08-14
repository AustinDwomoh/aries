import os,base64,logging,resend
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)



def send_email_with_attachment(subject, body, to_email, file_path=None, from_email=None, html_content=None):
    """
    Sends an email using the Resend API, optionally with an attachment and HTML content.
    Falls back to logging errors in a local file if the email fails to send.

    Args:
        subject (str): Subject line of the email.
        body (str): Plain text body of the email.
        to_email (str or list): Recipient email address(es).
        file_path (str, optional): Path to a file to attach.
        from_email (str, optional): Sender's email address. Defaults to settings.DEFAULT_FROM_EMAIL.
        html_content (str, optional): HTML content of the email. If provided, overrides plain text body.
    """
    from_email = from_email or settings.DEFAULT_FROM_EMAIL
    fallback_path = os.path.join(settings.LOG_BASE_DIR, "logs", "notify_failures.txt")
    resend.api_key = settings.RESEND_API_KEY  # Ensure the Resend API key is set

    if not isinstance(to_email, (list, tuple)):
        to_email = [to_email]

    # Prepare attachments payload for Resend
    attachments = []
    if file_path and os.path.isfile(file_path):
        with open(file_path, "rb") as f:
            file_data = f.read()
            encoded_content = base64.b64encode(file_data).decode("ascii")
            attachments.append({
                "filename": os.path.basename(file_path),
                "content": encoded_content,
                "disposition": "attachment",
                
            })

    try:
        resend.Emails.send({
            "from": from_email,
            "to": to_email,
            "subject": subject,
            **({"html": html_content} if html_content else {}),
            **({"text": body} if not html_content else {}),
            **({"attachments": attachments} if attachments else {}),
        })
    except Exception as e:
        try:
            os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
            with open(fallback_path, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()} - Failed to notify admin: {str(e)}\n")
        except Exception as fallback_err:
            logger.critical(f"Failed to write fallback notify log: {fallback_err}")
