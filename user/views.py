from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash

from config.utils import User, sign_in_url, paginate_and_get_page, get_snapshot
from user.forms import SigninForm, SignupForm, EditProfileForm, ChangePasswordForm


# Create your views here.
def signin_view(request, partial=None):
    if request.user.is_authenticated:
        return redirect("blog:index", partial=None)

    template = "user/sign-in.html"
    if request.method == "POST":
        form = SigninForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data.get("username"),
                password=form.cleaned_data.get("password"),
            )
            first_login = user.last_login is None
            login(request, user)
            headers = {
                "HX-Location": reverse(
                    "user:edit-profile" if first_login else "blog:index",
                    kwargs={"partial": None},
                )
            }
            return HttpResponse(headers=headers)
    else:
        form = SigninForm()
    context = {"form": form}
    if request.htmx and partial != "None":
        template = f"{template}#{partial}"
    return render(request, template, context)


def signup_view(request, partial=None):
    if request.user.is_authenticated:
        return redirect("blog:index", partial=None)

    template = "user/sign-up.html"
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data.get("username"),
                email=form.cleaned_data.get("email"),
                password=form.cleaned_data.get("password"),
            )

            messages.success(request, "Account created successfully!")
            return redirect("user:sign-in", partial=partial)
    else:
        form = SignupForm()
    context = {"form": form}
    if request.htmx and partial != "None":
        template = f"{template}#{partial}"
    return render(request, template, context)


@require_POST
def signout_view(request):
    logout(request)
    return redirect("user:sign-in", partial=None)


@login_required(login_url=sign_in_url)
def edit_profile_view(request, partial=None):
    template = "user/edit-profile.html"
    context = {}
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            context["message"] = "Profile updated!"
    else:
        form = EditProfileForm(instance=request.user)
    context["form"] = form
    if request.htmx and partial != "None":
        template = f"{template}#{partial}"
    return render(request, template, context)


def search_view(request):
    query = request.GET.get("query").strip()
    snapshot = get_snapshot(request.GET)
    if query:
        result = User.objects.filter(
            username__icontains=query, date_joined__lt=snapshot
        )
    else:
        result = User.objects.none()
    result = result.order_by("id")
    context = {
        "result": paginate_and_get_page(result, request.GET.get("page", 1)),
        "snapshot": snapshot,
    }
    return render(request, "user/user-search.html", context)


def profile_view(request, user_id, partial="None"):
    current_tab = request.GET.get("tab")
    user = get_object_or_404(User, id=user_id)
    page = request.GET.get("page", 1)
    tabs = (
        ("posts", "saved", "people", "settings")
        if request.user == user
        else ("posts", "people")
    )

    context = {"user": user, "tabs": tabs, "current_tab": current_tab}
    context["is_followed"] = True if request.user in user.followers.all() else False
    blogs = None

    title = f"{user} profile"
    if current_tab == "saved":
        if user != request.user:
            raise PermissionDenied()
        template = "profile/profile-posts.html"
        blogs = user.saved_blogs
        context["title"] = f"{title} - saved blogs"
    elif current_tab == "people":
        template = "profile/profile-people.html"
        followings, followers = (
            user.followings.with_is_followed(user=request.user).order_by("id"),
            user.followers.with_is_followed(user=request.user).order_by("id"),
        )
        context["followings"], context["followers"] = (
            paginate_and_get_page(followings, page),
            paginate_and_get_page(followers, page),
        )
        context["title"] = f"{title} - people"
    elif current_tab == "settings":
        if user != request.user:
            raise PermissionDenied()
        template = "profile/profile-settings.html"
        if request.method == "POST":
            partial = "change_password_form"
            form = ChangePasswordForm(request.POST, user=request.user)
            if form.is_valid():
                new_password = form.cleaned_data.get("new_password")
                user.set_password(new_password)
                user.save(update_fields=["password"])
                update_session_auth_hash(request, user)
        else:
            form = ChangePasswordForm(user=request.user)
        context["form"] = form
    else:
        template = "profile/profile-posts.html"
        blogs = user.blogs
        context["title"] = f"{title} - blogs"

    if blogs:
        blogs = blogs.with_is_liked_and_saved(user=user).order_by("-created_at", "-id")
        context["blogs"] = paginate_and_get_page(blogs, page)

    if request.htmx and partial != "None":
        template = f"{template}#{partial}"
    return render(request, template, context)
