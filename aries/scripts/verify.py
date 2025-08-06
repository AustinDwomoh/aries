from django.core.cache import cache
from django.template.loader import render_to_string
import random,threading
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from aries.settings import SITE_DOMAIN,SITE_PROTOCOL,ErrorHandler
from django.contrib.auth.backends import BaseBackend
from clans.models import Clans
from . import email_handle

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
    


def send_verification(user, method='email'):
    try:
        otp = str(generate_otp())
        cache.set(f"phone_otp_{user.pk}", otp, timeout=300)

        if method == 'email':
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            email_link = f"{SITE_PROTOCOL}://{SITE_DOMAIN}/verify/{uid}/{token}/"
            name = user.username if isinstance(user, UserModel) else user.clan_name
            html_content = render_to_string("users/verify_email.html", {
                "name":name,
                "email_link": email_link,
                "otp": otp
            })
            plain_text = f"Hi {name},\n\nYour code is {otp}\n\nClick the link to verify your email: {email_link}"

           
            threading.Thread(target=email_handle.send_email_with_attachment,kwargs={
                "subject": "Verify Email",
                "body": plain_text,
                "to_email": user.email,
                "file_path": None,
                "from_email": None,
                "html_content": html_content}).start()
    except Exception as e:
        ErrorHandler().handle(e,context='Coundltn send verification')
