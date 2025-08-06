from django.core.cache import cache
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.template.loader import render_to_string
import random,threading
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from aries.settings import SITE_DOMAIN,SITE_PROTOCOL,DEFAULT_FROM_EMAIL,ErrorHandler,SENDGRID_API_KEY
from django.contrib.auth.backends import BaseBackend
from clans.models import Clans


UserModel = get_user_model()

class MultiFieldAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if request and request.path.startswith('/admin/login/'):
            return None, 'admin_login_blocked'
        try:
            user = UserModel.objects.filter(
                Q(username=username) | Q(email=username) | Q(profile__phone=username)
            ).first()
        
            if user and user.check_password(password):
                if not user.profile.is_verified:
                    return None, 'unverified'
                user.backend = 'scripts.verify.MultiFieldAuthBackend'
                return user, None
        except Exception as e:
            ErrorHandler().handle(e, context="Error Authenticate process")
        return None, 'invalid'
 
class ClanBackend(BaseBackend):
    """Testin

    Args:
        BaseBackend (_type_): _description_
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            clan = Clans.objects.filter(
                Q(clan_name=username) | Q(email=username) | Q(phone=username)
            ).first()
            if clan and clan.check_password(password):
                if not clan.is_verified:
                    return None, 'unverified'
                clan.backend = 'scripts.verify.ClanBackend'
                return clan, None
        except Exception as e:
            ErrorHandler().handle(e, context="Error during Clan authentication")

        return None, 'invalid'

    def get_user(self, user_id):
        try:
            return Clans.objects.get(pk=user_id)
        except Clans.DoesNotExist:
            return None
    
def generate_otp():
    return str(random.randint(100000, 999999))
      
def send_sms(to_number, message):
    #logic for sms but gave up
    print(f"Sending SMS to {to_number}: {message}")
    
def _send_sendgrid_email(message):
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        if response.status_code not in range(200, 300):
            ErrorHandler().handle(
                Exception(f"SendGrid responded with status {response.status_code}"),
                context="SendGrid Email Sending"
            )
    except Exception as e:
        ErrorHandler().handle(e, context="SendGrid Email Sending")

def send_verification(user, method='email'):
    try:
        otp = str(generate_otp())
        cache.set(f"phone_otp_{user.pk}", otp, timeout=300)

        if method == 'email':
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            email_link = f"{SITE_PROTOCOL}://{SITE_DOMAIN}/verify/{uid}/{token}/"

            html_content = render_to_string("users/verify_email.html", {
                "name": user.username if isinstance(user,UserModel) else user.clan_name,
                "email_link": email_link,
                "otp": otp
            })
            plain_text = f"Hi {user.username if isinstance(user,UserModel) else user.clan_name},\n\nYour code is {otp}\n\nClick the link to verify your email: {email_link}"

            message = Mail(
                from_email= f"Aries Project <{DEFAULT_FROM_EMAIL}>",
                to_emails=user.email,
                subject="Verify your email",
                plain_text_content=plain_text,
                html_content=html_content
            )

            # Send email asynchronously to avoid blocking request
            threading.Thread(target=_send_sendgrid_email, args=(message,)).start()
    except Exception as e:
        ErrorHandler().handle(e,context='Coundltn send verification')
