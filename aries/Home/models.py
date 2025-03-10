from django.db import models
from django.contrib.auth.models import User
from clubs.models import Clans
# Create your models here.
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")  # User who follows
    following_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="followers")  # Followed user
    following_club = models.ForeignKey(Clans, on_delete=models.CASCADE, null=True, blank=True, related_name="followers")  # Followed club
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following_user')  # Prevent duplicate follows
        unique_together = ('follower', 'following_club')

    def __str__(self):
        if self.following_user:
            return f"{self.follower.username} follows {self.following_user.username}"
        if self.following_club:
            return f"{self.follower.username} follows {self.following_club.name}"