from django.urls import path
from user.views import (
    signin_view,
    signup_view,
    signout_view,
    edit_profile_view,
    search_view,
    profile_view,
)

app_name = "user"
urlpatterns = [
    path("sign-in/<str:partial>/", signin_view, name="sign-in"),
    path("sign-up/<str:partial>/", signup_view, name="sign-up"),
    path("edit-profile/<str:partial>/", edit_profile_view, name="edit-profile"),
    path("sign-out/", signout_view, name="sign-out"),
    path("search/", search_view, name="search"),
    path("<int:user_id>/<str:partial>/", profile_view, name="profile"),
]
