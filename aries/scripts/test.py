import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aries.settings')  # adjust 'aries.settings' to your project’s settings module
django.setup()

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from Home.models import Follow

for user_id in range(1, 6):
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        print(f"User with id {user_id} does not exist.")
        continue

    followers = Follow.objects.filter(
        followed_content_type=ContentType.objects.get_for_model(target_user),
        followed_object_id=target_user.id,
        status='accepted'
    )

    print(f"User ID {user_id} has {followers.count()} followers:")
    for f in followers:
        print(f"  Follower: {f.follower} (ID: {f.follower.id})")
