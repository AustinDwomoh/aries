from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Follow(models.Model):
    """
    Represents a polymorphic follow relationship between any two entities in the system.

    This model uses Django's generic relations to allow any model instance
    to follow any other model instance. It tracks the status of the follow
    (e.g., pending, accepted, blocked), whether the follow is mutual,
    and whether the follower has been notified.

    Attributes:
        follower (GenericForeignKey): The entity initiating the follow.
        followed (GenericForeignKey): The entity being followed.
        status (str): Current status of the follow relationship.
        is_mutual (bool): Whether the follow is reciprocated.
        notified (bool): Whether a notification has been sent.
        created_at (datetime): Timestamp of when the follow was created.

    Constraints:
        Ensures uniqueness of each follower-followed pair.
    """
    STATUS_CHOICES = [('pending', 'Pending'),('accepted', 'Accepted'),('blocked', 'Blocked'),]
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
