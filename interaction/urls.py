from django.urls import path
from interaction.views import like_view, save_view, comment_view, follow_view

app_name = "interaction"
urlpatterns = [
    path("save/<int:blog_id>/", save_view, name="save"),
    path("like/<str:instance_model>/<int:instance_id>/", like_view, name="like"),
    path("comment/<int:level>/<int:blog_id>/", comment_view, name="add-comment"),
    path(
        "comment/<int:level>/<int:blog_id>/<int:comment_id>/",
        comment_view,
        name="reply-comment",
    ),
    path("follow/<str:user_to_follow_id>", follow_view, name="follow"),
]
