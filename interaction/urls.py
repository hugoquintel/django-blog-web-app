from django.urls import path
from interaction.views import like_view, save_view, comment_view

app_name = "interaction"
urlpatterns = [
    path("like/<int:blog_id>", like_view, name="like"),
    path("save/<int:blog_id>", save_view, name="save"),
    path("comment/<int:blog_id>", comment_view, name="add-comment"),
    path("comment/<int:blog_id>/<int:comment_id>", comment_view, name="reply-comment"),
]
