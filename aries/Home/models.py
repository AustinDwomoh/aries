from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

class Follow(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('blocked', 'Blocked'),
    ]

    follower_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='follower_type')
    follower_object_id = models.PositiveIntegerField()
    follower = GenericForeignKey('follower_content_type', 'follower_object_id')

    followed_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='followed_type')
    followed_object_id = models.PositiveIntegerField()
    followed = GenericForeignKey('followed_content_type', 'followed_object_id')

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='accepted')
    is_mutual = models.BooleanField(default=False)
    notified = models.BooleanField(default=False)  # for notifications
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            ('follower_content_type', 'follower_object_id', 'followed_content_type', 'followed_object_id'),
        )

    def __str__(self):
        return f"{self.follower} follows {self.followed} [{self.status}]"
