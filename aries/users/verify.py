from django.utils import timezone
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.conf import settings
import random
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from aries.settings import SITE_DOMAIN,SITE_PROTOCOL
UserModel = get_user_model()

class MultiFieldAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = UserModel.objects.filter(
            Q(username=username) | Q(email=username) | Q(profile__phone=username)
        ).first()

        if user and user.check_password(password):
            if not user.profile.is_verified:
                return None
            return user
        return None
 

    
def generate_otp():
    return str(random.randint(100000, 999999))


def send_sms(to_number, message):
    # ⚠️ Placeholder — integrate Twilio or something later
    print(f"Sending SMS to {to_number}: {message}")
    
def send_verification(user,type='email'):
    """generate verification 

    Args:
        user (_type_): _description_
    """
    user.profile.verification_sent_at = timezone.now()
    if type == 'email':
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        email_link = f"{SITE_PROTOCOL}://{SITE_DOMAIN}/verify/{uid}/{token}/"
    

        # This can be a separate template file: "emails/verify_email.html"
        html_content = render_to_string("users/verify_email.html", {
            "user": user,
            "email_link": email_link,
        })

        # Fallback plain text version
        text_content = f"Hi {user.username},\n\nClick the link to verify your email: {email_link}"

        email = EmailMultiAlternatives(
            subject="Verify your email",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )

        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)


    else:
        if user.profile.phone_number:
            otp = generate_otp()
            cache.set(f"phone_otp_{user.pk}", otp, timeout=300)  # 5 minutes
            send_sms(user.profile.phone_number, f"Your verification code is: {otp}")
    user.profile.save() 