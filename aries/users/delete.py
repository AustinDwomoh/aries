from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from .models import Profile  


class Command(BaseCommand):
    help = 'Delete users who have not verified their email or phone within 24 hours'

    def handle(self, *args, **kwargs):
        threshold = timezone.now() - timedelta(hours=24)
        profiles = Profile.objects.filter(verified=False, verification_sent_at__lt=threshold)

        total = profiles.count()

        for profile in profiles:
            username = profile.user.username
            profile.user.delete()
            self.stdout.write(self.style.WARNING(f"Deleted unverified user: {username}"))

        self.stdout.write(self.style.SUCCESS(f"Deleted {total} unverified user(s)."))
