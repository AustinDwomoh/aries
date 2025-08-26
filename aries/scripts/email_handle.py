import os,base64,logging,resend
from datetime import datetime
from django.conf import settings
import asyncio
import time
import resend
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
executor = ThreadPoolExecutor(max_workers=2)  # process 2 at a time
logger = logging.getLogger(__name__)


resend.api_key = settings.RESEND_API_KEY
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
    fallback_path = os.path.join(settings.LOG_BASE_DIR, "email_logs", "notify_failures.txt")
  # Ensure the Resend API key is set

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


def notify_tournament_players(model,request, tournament, action):
    messages = []
    if model == 'clan':
        participants = tournament.teams.all()
    else:
        participants = tournament.players.all()
    for team in participants:
        html_content = render_to_string("tournaments/notify.html", {
            "tour": tournament,
            "tour_link": request.build_absolute_uri(
                reverse("cvc_details", kwargs={"tour_id": tournament.id})
            ),
            "action": action,
            "recipient": team.clan_name if model == 'clan' else team.user.username,
        })

        messages.append({
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [team.email if model == 'clan' else team.user.email],
            "subject": f"Tournament {tournament.name} - {action}",
            "html": html_content,
        })

        # Notify each member
        if model == 'clan':
            for member in team.members.all():
                html_content = render_to_string("tournaments/notify.html", {
                    "tour": tournament,
                    "tour_link": request.build_absolute_uri(
                        reverse("cvc_details", kwargs={"tour_id": tournament.id})
                    ),
                    "action": action,
                    "recipient": member.user.username,
                })

                messages.append({
                    "from": settings.DEFAULT_FROM_EMAIL,
                    "to": [member.user.email],
                    "subject": f"Tournament {tournament.name} - {action}",
                    "html": html_content,
                })

    asyncio.run(send_with_rate_limit_async(messages))


def send_email_sync(msg):
    return resend.Emails.send(msg)

async def send_with_rate_limit_async(messages, per_second=2):
    batch_size = per_second
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i+batch_size]
        tasks = [asyncio.get_event_loop().run_in_executor(executor, send_email_sync, msg) for msg in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for msg, res in zip(batch, results):
            if isinstance(res, Exception):
                print("❌ Failed for:", msg["to"], "| Error:", res)
            else:
                print("✅ Sent:", res)

        await asyncio.sleep(1) 