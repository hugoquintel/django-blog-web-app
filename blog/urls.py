from django.urls import path
from blog.views import index_view, detail_view, create_edit_view, delete_view

app_name = "blog"
urlpatterns = [
    path("index/", index_view, name="index"),
    path("<int:blog_id>/<str:partial>/", detail_view, name="detail"),
    path("create/<str:partial>/", create_edit_view, name="create"),
    path("edit/<str:partial>/<int:blog_id>/", create_edit_view, name="edit"),
    path("delete/<int:blog_id>/", delete_view, name="delete"),
]
