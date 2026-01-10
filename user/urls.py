from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from user.views import signin_view, signup_view, index_view

app_name = "user"
urlpatterns = [
    path("sign-in/", signin_view, name="sign-in"),
    path("sign-in/<str:render_type>", signin_view, name="sign-in"),
    path("sign-up/", signup_view, name="sign-up"),
    path("sign-up/<str:render_type>", signup_view, name="sign-up"),
    path(
        "sign-out/",
        auth_views.LogoutView.as_view(
            next_page=reverse_lazy("user:sign-in", kwargs={"render_type": "full"})
        ),
        name="sign-out",
    ),
    path("index/", index_view, name="index"),
]
