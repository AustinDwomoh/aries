from django.utils import timezone
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import random
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from aries.settings import SITE_DOMAIN,SITE_PROTOCOL,DEFAULT_FROM_EMAIL
UserModel = get_user_model()

class MultiFieldAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = UserModel.objects.filter(
            Q(username=username) | Q(email=username) | Q(profile__phone=username)
        ).first()
      
        if user and user.check_password(password):
            if not user.profile.is_verified:
                return None, 'unverified'
            user.backend = 'users.verify.MultiFieldAuthBackend'
            return user, None
        return None, 'invalid'
 

    
def generate_otp():
    return str(random.randint(100000, 999999))


def send_sms(to_number, message):
    # ⚠️ Placeholder — integrate Twilio or something later
    print(f"Sending SMS to {to_number}: {message}")
    
def send_verification(user,type):
    """generate verification 

    Args:
        user (_type_): _description_
    """
    otp = str(generate_otp())
    cache.set(f"phone_otp_{user.pk}", otp, timeout=300)
    print(f"OTP generated for user: {user.pk} -> {otp}")
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
        email.send(fail_silently=False)
    else:
        if user.profile.phone:
              # 5 minutes
            send_sms(user.profile.phone, f"Your verification code is: {otp}")
    user.profile.save() 