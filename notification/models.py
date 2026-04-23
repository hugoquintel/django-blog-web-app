from django.db import models
from django.conf import settings
from django.db.models import UniqueConstraint

from blog.models import Blog
from interaction.models import Comment
from config.manager import QuerySetMixin


class NotificationQuerySet(QuerySetMixin, models.QuerySet):
    pass


# Create your models here.
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("follow", "Follow"),
        ("blog_post", "Post Blog"),
        ("blog_like", "Like Blog"),
        ("comment_like", "Like Comment"),
        ("comment_add", "Add Comment"),
        ("comment_reply", "Reply Comment"),
    ]
    notification_type = models.CharField(choices=NOTIFICATION_TYPES)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_notifications",
    )
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    objects = NotificationQuerySet.as_manager()

    def __str__(self):
        return self.notification_type

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["notification_type", "sender", "receiver", "blog", "comment"],
                name="unique_notification",
                nulls_distinct=False,
            )
        ]
