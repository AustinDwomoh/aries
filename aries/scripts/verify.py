from django.core.cache import cache
from django.template.loader import render_to_string
import random,threading
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from scripts.error_handle import ErrorHandler
from django.contrib.auth.backends import BaseBackend
from clans.models import Clans
from . import email_handle

UserModel = get_user_model()

class MultiFieldAuthBackend(ModelBackend):
    """
    Custom auth backend for UserModel allowing login by username, email, or phone.
    Blocks admin login via this backend.
    Verifies password and email verification status.
    Returns user or error code.
    """
    def custom_authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a User by username, email, or phone number.

        - Blocks authentication attempts from the Django admin login page.
        - Searches UserModel for a user matching the given username/email/phone.
        - Checks the provided password against the hashed password.
        - Returns the user object if authenticated and verified; otherwise returns None with an error code.
        """
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
    """
    Custom auth backend for Clan model.
    Allows login by clan_name, email, or phone.
    Checks password equality (plain text?).
    Verifies clan verification status.
    Returns clan or error code.
    """
    def custom_authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a Clan by clan_name, email,

        - Searches Clans model for a clan matching the given username/email/
        - Compares the provided password directly (no hashing) with clan.password — **insecure, should be hashed**.
        - Returns the clan object if authenticated and verified; otherwise returns None with an error code.
        """
        try:
            clan = Clans.objects.filter(
                Q(clan_name=username) | Q(email=username)
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
    """Generates a 6-digit numeric OTP as a string."""
    return str(random.randint(100000, 999999))
      
def send_sms(to_number, message):
    """Stub for SMS sending functionality (not implemented)."""
    print(f"Sending SMS to {to_number}: {message}")


def send_verification(account, model_type, method='email'):
    """
    Sends verification OTP via email.
    Caches OTP for 5 minutes keyed by user ID.
    Sends email with verification link and OTP asynchronously.
    Handles both UserModel and Clan instances.
    """
    try:
        otp = str(generate_otp())
        cache.set(f"{model_type}_otp_{account.pk}", otp, timeout=300)
        if method == 'email':
            uid = urlsafe_base64_encode(force_bytes(account.pk))
            token = default_token_generator.make_token(account)
            name = getattr(account, "username", getattr(account, "clan_name", ""))
            email_link = f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/verify/{model_type}/{uid}/{token}/"

           
            email = getattr(account, "email", None)

            html_content = render_to_string("users/verify_email.html", {
                "name": name,
                "email_link": email_link,
                "otp": otp
            })
            plain_text = f"Hi {name},\n\nYour code is {otp}\n\nClick the link to verify your account: {email_link}"

            threading.Thread(
                target=email_handle.send_email_with_attachment,
                kwargs={
                    "subject": "Verify Your Account",
                    "body": plain_text,
                    "to_email": email,
                    "file_path": None,
                    "from_email": None,
                    "html_content": html_content
                }
            ).start()
    except Exception as e:
        ErrorHandler().handle(e,context=f'Coundltn send verification for {model_type}')
