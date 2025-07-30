from django.core.cache import cache
from smtplib import SMTPException
from django.core.mail import EmailMultiAlternatives, BadHeaderError
from django.template.loader import render_to_string
import random
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from aries.settings import SITE_DOMAIN,SITE_PROTOCOL,DEFAULT_FROM_EMAIL,ErrorHandler

error_handler = ErrorHandler()
# Set up logging to a txt file

UserModel = get_user_model()

class MultiFieldAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserModel.objects.filter(
                Q(username=username) | Q(email=username) | Q(profile__phone=username)
            ).first()
        
            if user and user.check_password(password):
                if not user.profile.is_verified:
                    return None, 'unverified'
                user.backend = 'users.verify.MultiFieldAuthBackend'
                return user, None
        except Exception as e:
            error_handler.handle(e, context="Error Authenticate process")
        return None, 'invalid'
 

    
def generate_otp():
    return str(random.randint(100000, 999999))


def send_sms(to_number, message):
    #logic for sms but gave up
    print(f"Sending SMS to {to_number}: {message}")
    
def send_verification(user,type='email'):
    """generate verification 

    Args:
        user (_type_): _description_
    """
    otp = str(generate_otp())
    cache.set(f"phone_otp_{user.pk}", otp, timeout=300)
    
    if type == 'email':
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        email_link = f"{SITE_PROTOCOL}://{SITE_DOMAIN}/verify/{uid}/{token}/"
        html_content = render_to_string("users/verify_email.html", {
            "user": user,
            "email_link": email_link,
            "otp":otp
        })

        # Fallback plain text version
        text_content = f"Hi {user.username},\n\nYour code is {otp} \n\nClick the link to verify your email: {email_link}"

        email = EmailMultiAlternatives(
            subject="Verify your email",
            body=text_content,
            from_email=DEFAULT_FROM_EMAIL,
            to=[user.email],
        )

        email.attach_alternative(html_content, "text/html")
        try:
            email.send(fail_silently=False)
        except (BadHeaderError, SMTPException, Exception) as e:
            error_handler.handle(e, context="Error Sending Verification process")
    """ else:
        if user.profile.phone:
              # 5 minutes
            send_sms(user.profile.phone, f"Your verification code is: {otp}") """
    