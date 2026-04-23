from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import post_save

from blog.models import Blog
from user.models import Follow
from notification.models import Notification
from interaction.models import Comment, Like


@receiver(post_save, sender=Follow, dispatch_uid="follow_notifications")
@receiver(post_save, sender=Like, dispatch_uid="like_notifications")
@receiver(post_save, sender=Blog, dispatch_uid="blog_notifications")
@receiver(post_save, sender=Comment, dispatch_uid="comment_notifications")
def send_notification(sender, instance, created, **kwargs):
    if created:
        if sender is Follow:
            values = {
                "notification_type": "follow",
                "sender": instance.follower,
                "receiver": instance.following,
            }
            Notification.objects.get_or_create(**values)
        elif sender is Blog:
            user = instance.user
            followers = user.followers.all()
            notifications = [
                Notification(
                    notification_type="blog_post",
                    sender=user,
                    receiver=follower,
                    blog=instance,
                )
                for follower in followers
            ]
            Notification.objects.bulk_create(notifications)
        elif sender is Like:
            values = {
                "sender": instance.user,
                "blog": instance.blog,
                "comment": instance.comment,
            }
            if instance.blog:
                values["receiver"] = instance.blog.user
                values["notification_type"] = "blog_like"
            else:
                values["receiver"] = instance.comment.user
                values["notification_type"] = "comment_like"
            if values["receiver"] == values["sender"]:
                return
            Notification.objects.get_or_create(**values)
        elif sender is Comment:
            values = {
                "sender": instance.user,
                "blog": instance.blog,
                "comment": instance,
            }
            if instance.depth == 1:
                values["receiver"] = instance.blog.user
                values["notification_type"] = "comment_add"
            else:
                values["receiver"] = instance.get_parent().user
                values["notification_type"] = "comment_reply"
            if values["receiver"] == values["sender"]:
                return
            Notification.objects.get_or_create(**values)
