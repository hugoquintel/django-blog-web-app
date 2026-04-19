from django.urls import path
from notification.views import seen_and_redirect_view, update_seen_view, delete_view

app_name = "notification"
urlpatterns = [
    path(
        "seen-redirect/<int:noti_id>/",
        seen_and_redirect_view,
        name="seen-redirect",
    ),
    path("update/<int:noti_id>/", update_seen_view, name="update"),
    path("delete/<int:noti_id>/", delete_view, name="delete"),
]
