from django.core.cache import cache
import random, threading
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from scripts.error_handle import ErrorHandler
from django.contrib.auth.backends import BaseBackend
from clans.models import Clan
import resend

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
        print(f"[AUTH] Attempting authentication for username: {username}")
        
        if request and request.path.startswith('/admin/login/'):
            print("[AUTH] Admin login blocked - using custom backend")
            return None, 'admin_login_blocked'
        
        try:
            print(f"[AUTH] Searching for user with username/email/phone: {username}")
            user = UserModel.objects.filter(
                Q(username=username) | Q(email=username) | Q(profile__phone=username)
            ).first()
            
            if user:
                print(f"[AUTH] User found: {user.username} (ID: {user.id})")
                print(f"[AUTH] User is_active: {user.is_active}")
                
                if user.check_password(password):
                    print("[AUTH] Password check passed")
                    
                    # Check if user has profile and is verified
                    try:
                        profile = user.profile
                        print(f"[AUTH] Profile found - is_verified: {profile.is_verified}")
                        
                        if not profile.is_verified:
                            print("[AUTH] User not verified - blocking login")
                            return None, 'unverified'
                            
                        user.backend = 'scripts.verify.MultiFieldAuthBackend'
                        print("[AUTH] Authentication successful")
                        return user, None
                        
                    except Exception as profile_error:
                        print(f"[AUTH] Profile error: {profile_error}")
                        # Create profile if it doesn't exist
                        from users.models import Profile
                        profile = Profile.objects.create(user=user)
                        print("[AUTH] Profile created - user needs verification")
                        return None, 'unverified'
                else:
                    print("[AUTH] Password check failed")
            else:
                print("[AUTH] No user found with provided credentials")
                
        except Exception as e:
            print(f"[AUTH] Authentication error: {e}")
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
            clan = Clan.objects.filter(
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
            return Clan.objects.get(pk=user_id)
        except Clan.DoesNotExist:
            return None
    
def generate_otp():
    """Generates a 6-digit numeric OTP as a string."""
    return str(random.randint(100000, 999999))
      
def send_sms(to_number, message):
    """Stub for SMS sending functionality (not implemented)."""
    print(f"Sending SMS to {to_number}: {message}")


def send_verification(account, model_type, method='email'):
    """
    Sends verification OTP via email using Resend.
    Caches OTP for 5 minutes keyed by user ID.
    Sends email with verification link and OTP asynchronously.
    Handles both UserModel and Clan instances.
    """
    print(f"[VERIFY] Starting verification for {model_type} account: {account.pk}")
    
    try:
        otp = str(generate_otp())
        print(f"[VERIFY] Generated OTP: {otp}")
        
        cache_key = f"{model_type}_otp_{account.pk}"
        cache.set(cache_key, otp, timeout=300)
        print(f"[VERIFY] OTP cached with key: {cache_key}")
        
        if method == 'email':
            uid = urlsafe_base64_encode(force_bytes(account.pk))
            token = default_token_generator.make_token(account)
            name = getattr(account, "username", getattr(account, "clan_name", ""))
            email_link = f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/api/verify/{model_type}/{uid}/{token}/"
            email = getattr(account, "email", None)
            
            print(f"[VERIFY] Email verification for: {name} ({email})")
            print(f"[VERIFY] Verification link: {email_link}")

            # Create HTML email content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Verify Your Account</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #f8f9fa; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: white; padding: 30px; border: 1px solid #e9ecef; }}
                    .otp-code {{ font-size: 24px; font-weight: bold; color: #007bff; text-align: center; margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }}
                    .button {{ display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ background: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; font-size: 14px; color: #6c757d; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Verify Your Account</h1>
                    </div>
                    <div class="content">
                        <p>Hi {name},</p>
                        <p>Thank you for registering! Please verify your account using the code below:</p>
                        <div class="otp-code">{otp}</div>
                        <p>Or click the button below to verify your account:</p>
                        <a href="{email_link}" class="button">Verify Account</a>
                        <p>This verification code will expire in 5 minutes.</p>
                        <p>If you didn't create an account, please ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message, please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            plain_text = f"""Hi {name},

Thank you for registering! Please verify your account using the code below:

Verification Code: {otp}

Or click the link to verify your account: {email_link}

This verification code will expire in 5 minutes.

If you didn't create an account, please ignore this email.

This is an automated message, please do not reply."""

            # Send email using Resend
            print(f"[VERIFY] Starting email thread for: {email}")
            threading.Thread(
                target=send_resend_email,
                kwargs={
                    "subject": "Verify Your Account",
                    "html_content": html_content,
                    "text_content": plain_text,
                    "to_email": email,
                    "from_email": settings.DEFAULT_FROM_EMAIL
                }
            ).start()
            print(f"[VERIFY] Email thread started successfully")
    except Exception as e:
        print(f"[VERIFY] Error in send_verification: {e}")
        ErrorHandler().handle(e, context=f'Could not send verification for {model_type}')


def send_resend_email(subject, html_content, text_content, to_email, from_email):
    """
    Send email using Resend API.
    """
    print(f"[EMAIL] Attempting to send email to: {to_email}")
    print(f"[EMAIL] From: {from_email}")
    print(f"[EMAIL] Subject: {subject}")
    
    try:
        resend.api_key = settings.RESEND_API_KEY
        print(f"[EMAIL] Resend API key set: {bool(settings.RESEND_API_KEY)}")
        
        params = {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
            "text": text_content,
        }
        
        print(f"[EMAIL] Sending email with params: {list(params.keys())}")
        email = resend.Emails.send(params)
        print(f"[EMAIL] Email sent successfully: {email}")
        
    except Exception as e:
        print(f"[EMAIL] Error sending email: {e}")
        ErrorHandler().handle(e, context="Resend email sending")
