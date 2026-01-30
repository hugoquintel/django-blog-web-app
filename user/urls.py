from django.urls import path
from user.views import signin_view, signup_view, signout_view, edit_profile_view

app_name = "user"
urlpatterns = [
    path("sign-in/", signin_view, name="sign-in"),
    path("sign-in/<str:render_type>", signin_view, name="sign-in"),
    path("sign-up/", signup_view, name="sign-up"),
    path("sign-up/<str:render_type>", signup_view, name="sign-up"),
    path("sign-out/", signout_view, name="sign-out"),
    path("edit-profile/", edit_profile_view, name="edit-profile"),
]
