from django.contrib.auth.models import User
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Follow(models.Model):
    follower_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="following_type")
    follower_id = models.PositiveIntegerField()
    follower = GenericForeignKey('follower_type', 'follower_id')  

    followed_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="followed_type")
    followed_id = models.PositiveIntegerField()
    followed = GenericForeignKey('followed_type', 'followed_id')  

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower_type', 'follower_id', 'followed_type', 'followed_id')  
        indexes = [
            models.Index(fields=['follower_type', 'follower_id']),
            models.Index(fields=['followed_type', 'followed_id']),
        ]