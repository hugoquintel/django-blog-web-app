from django.urls import path
from blog.views import index_view, detail_view, create_edit_view

app_name = "blog"
urlpatterns = [
    path("index/", index_view, name="index"),
    path("<int:blog_id>/", detail_view, name="detail"),
    path("<int:blog_id>/<str:render_type>", detail_view, name="detail"),
    path("create/", create_edit_view, name="create"),
    path("edit/<int:blog_id>/", create_edit_view, name="edit"),
]
