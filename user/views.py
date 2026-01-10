from django.shortcuts import render, redirect
from user.forms import SigninForm, SignupForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse


# Create your views here.
def signin_view(request, render_type="partial"):
    context = {}
    template = "user/sign-in.html"
    partial = "form"
    if request.method == "POST":
        form = SigninForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect("user:index")
    else:
        form = SigninForm()
    context = {"form": form}

    if render_type == "partial":
        template = f"{template}#{partial}" if request.htmx else template
    return render(request, template, context)


def signup_view(request, render_type="partial"):
    context = {}
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
    return render(request, template, context)


def index_view(request):
    return render(request, "user/index.html")
