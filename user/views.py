from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect, get_object_or_404

from user.forms import SigninForm, SignupForm, EditProfileForm
from config.utils import User, sign_in_url, paginate_and_get_page


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


def signout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("user:sign-in", partial="None")


@login_required(login_url=sign_in_url)
def edit_profile_view(request, partial=None):
    template = "user/edit-profile.html"
    context = {}
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.birthday = user.birthday or None
            context["message"] = "Profile updated!"
            user.save()
    else:
        form = EditProfileForm(instance=request.user)
    context["form"] = form
    if request.htmx and partial != "None":
        template = f"{template}#{partial}"
    return render(request, template, context)


def search_view(request):
    query = request.GET.get("query").strip()
    result = (
        User.objects.filter(username__icontains=query) if query else User.objects.none()
    ).order_by("id")
    result = paginate_and_get_page(result, request.GET.get("page", 1))
    context = {"query": query, "result": result}
    return render(request, "user/user-search.html", context)


def profile_view(request, user_id, partial="None"):
    current_tab = request.GET.get("tab")
    user = get_object_or_404(User, id=user_id)
    tabs = (
        ("posts", "saved", "people", "settings")
        if request.user == user
        else ("posts", "people")
    )

    context = {"user": user, "tabs": tabs, "current_tab": current_tab}
    context["is_followed"] = True if request.user in user.followers.all() else False
    blogs = None

    match current_tab:
        case "saved":
            template = "profile/profile-posts.html"
            blogs = user.saved_blogs
        case "people":
            template = "profile/profile-people.html"
            followings, followers = (
                user.followings.with_is_followed(user=request.user).order_by("id"),
                user.followers.with_is_followed(user=request.user).order_by("id"),
            )
            followings, followers = (
                paginate_and_get_page(followings, request.GET.get("page", 1)),
                paginate_and_get_page(followers, request.GET.get("page", 1)),
            )
            context["followings"], context["followers"] = followings, followers
        case "settings":
            template = "profile/profile-settings.html"
        case _:
            template = "profile/profile-posts.html"
            blogs = user.blogs

    if blogs:
        blogs = blogs.with_is_liked_and_saved(user=user).order_by("-created_at")
        blogs = paginate_and_get_page(blogs, request.GET.get("page", 1))
        context["blogs"] = blogs

    if request.htmx and partial != "None":
        template = f"{template}#{partial}"
    return render(request, template, context)
