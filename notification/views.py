from django.db.models import F
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404

from notification.models import Notification


@require_POST
def seen_and_redirect_view(request, noti_id):
    if noti_id:
        notification = get_object_or_404(Notification, id=noti_id)
        notification.is_seen = True
        notification.save(update_fields=["is_seen"])
        if notification.notification_type == "follow":
            url = reverse(
                "user:profile",
                kwargs={"user_id": notification.sender.id, "partial": None},
            )
        elif notification.notification_type in ("blog_post", "blog_like"):
            url = notification.blog.get_absolute_url()
        elif notification.notification_type == "comment_like":
            url = reverse(
                "blog:detail",
                kwargs={
                    "root_depth": notification.comment.depth,
                    "blog_id": notification.comment.blog.id,
                    "comment_id": notification.comment.id,
                    "partial": None,
                },
            )
        elif notification.notification_type == "comment_add":
            url = reverse(
                "blog:detail",
                kwargs={
                    "root_depth": 1,
                    "blog_id": notification.blog.id,
                    "comment_id": notification.comment.id,
                    "partial": None,
                },
            )
        elif notification.notification_type == "comment_reply":
            parent_comment = notification.comment.get_parent()
            url = reverse(
                "blog:detail",
                kwargs={
                    "root_depth": parent_comment.depth,
                    "blog_id": notification.blog.id,
                    "comment_id": parent_comment.id,
                    "partial": None,
                },
            )
        return redirect(url)
    else:
        notifications = request.user.received_notifications.all()
        for notification in notifications:
            notification.is_seen = True
        Notification.objects.bulk_update(notifications, fields=["is_seen"])
        return render(
            request,
            "components/header.html#notifications",
            {"notifications": notifications},
        )


@require_POST
def update_seen_view(request, noti_id):
    notification = get_object_or_404(Notification, id=noti_id)
    notification.is_seen = ~F("is_seen")
    notification.save(update_fields=["is_seen"])

    return render(
        request,
        "notification/notification.html",
        {"notification": notification},
    )


@require_POST
def delete_view(request, noti_id):
    if noti_id:
        notification = get_object_or_404(Notification, id=noti_id)
        notification.delete()
        return HttpResponse()
    else:
        request.user.received_notifications.all().delete()
        notifications = Notification.objects.none()
        return render(
            request,
            "components/header.html#notifications",
            {"notifications": notifications},
        )
