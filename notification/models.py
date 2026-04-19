from django.db import models
from django.urls import reverse
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

    def get_absolute_url(self):
        if self.notification_type == "follow":
            url = reverse(
                "user:profile", kwargs={"user_id": self.sender.id, "partial": None}
            )
        elif self.notification_type == "blog_post":
            url = reverse(
                "blog:detail",
                kwargs={
                    "root_depth": 1,
                    "blog_id": self.blog.id,
                    "comment_id": 0,
                    "partial": None,
                },
            )
        elif self.notification_type == "blog_like":
            url = reverse(
                "blog:detail",
                kwargs={
                    "root_depth": 1,
                    "blog_id": self.blog.id,
                    "comment_id": 0,
                    "partial": None,
                },
            )
        elif self.notification_type == "comment_like":
            url = f'{reverse(
                "blog:detail",
                kwargs={
                    "root_depth": self.comment.depth,
                    "blog_id": self.comment.blog.id,
                    "comment_id": self.comment.id,
                    "partial": None,
                }
            )}#comment-{self.comment.id}'
        elif self.notification_type in ("comment_add", "comment_reply"):
            url = reverse(
                "blog:detail",
                kwargs={
                    "root_depth": self.comment.depth if self.comment else 1,
                    "blog_id": self.blog.id,
                    "comment_id": self.comment.id if self.comment else 0,
                    "partial": None,
                },
            )
        return url

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["notification_type", "sender", "receiver", "blog", "comment"],
                name="unique_notification",
                nulls_distinct=False,
            )
        ]
