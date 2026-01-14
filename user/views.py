from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from user.models import Profile
from user.forms import SigninForm, SignupForm, EditProfileForm


# Create your views here.
def signin_view(request, render_type="partial"):
    template = "user/sign-in.html"
    partial = "form"
    if request.method == "POST":
        form = SigninForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            first_login = user.last_login is None

            login(request, user)
            response = HttpResponse()
            if first_login:
                response["HX-Location"] = reverse("user:edit-profile")
            else:
                response["HX-Location"] = reverse("user:index")
            return response
    else:
        form = SigninForm()
    context = {"form": form}
    if render_type == "partial":
        template = f"{template}#{partial}" if request.htmx else template
    response = render(request, template, context)
    if render_type == "full":
        response["HX-Retarget"] = "body"
    return response


def signup_view(request, render_type="partial"):
    template = "user/sign-up.html"
    partial = "form"
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Account created successfully!")
            return redirect("user:sign-in")
    else:
        form = SignupForm()
    context = {"form": form}

    if render_type == "partial":
        template = f"{template}#{partial}" if request.htmx else template
    response = render(request, template, context)
    if render_type == "full":
        response["HX-Retarget"] = "body"
    return response


def signout_view(request):
    if request.method == "POST":
        logout(request)
        response = HttpResponse()
        response["HX-Location"] = reverse(
            "user:sign-in", kwargs={"render_type": "full"}
        )
        return response


@login_required(login_url=reverse_lazy("user:sign-in"))
def edit_profile_view(request):
    template = "user/profile-edit.html"
    profile = get_object_or_404(Profile, user=request.user)
    context = {"profile": profile}

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            if not profile.birthday:
                profile.birthday = None
            context["message"] = "Profile updated!"

            profile.save()
    else:
        form = EditProfileForm(instance=profile)
    context["form"] = form
    return render(request, template, context)


def index_view(request):
    return render(request, "user/index.html")
