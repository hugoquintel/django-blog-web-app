from django.db.models import F
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
        return redirect(notification.get_absolute_url())
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
