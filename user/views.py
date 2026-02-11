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
def signin_view(request, partial="None"):
    template = "user/sign-in.html"
    if request.method == "POST":
        form = SigninForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            first_login = user.last_login is None
            login(request, user)
            headers = {
                "HX-Location": reverse(
                    "user:edit-profile" if first_login else "blog:index"
                )
            }
            return HttpResponse(headers=headers)
    else:
        form = SigninForm()
    context = {"form": form}
    if request.htmx and partial != "None":
        template = f"{template}#{partial}"
    return render(request, template, context)


def signup_view(request, partial="None"):
    template = "user/sign-up.html"
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Account created successfully!")
            return redirect("user:sign-in", partial="auth-form")
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


@login_required(login_url=reverse_lazy("user:sign-in"))
def edit_profile_view(request):
    template = "user/edit-profile.html"
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
