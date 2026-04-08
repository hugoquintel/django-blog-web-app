from django.urls import path
from blog.views import (
    index_view,
    detail_view,
    create_edit_view,
    delete_view,
    search_view,
)

app_name = "blog"
urlpatterns = [
    path("index/<str:partial>/", index_view, name="index"),
    path(
        "<int:root_depth>/<int:blog_id>/<int:comment_id>/<str:partial>/",
        detail_view,
        name="detail",
    ),
    path("create/<str:partial>/", create_edit_view, name="create"),
    path("edit/<int:blog_id>/<str:partial>/", create_edit_view, name="edit"),
    path("delete/<int:blog_id>/", delete_view, name="delete"),
    path("search/<str:partial>/", search_view, name="search"),
]
