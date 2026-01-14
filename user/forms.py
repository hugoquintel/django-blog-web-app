from django import forms
from django.contrib.auth.models import User
from user.models import Profile
from user.validators import (
    signin_validators,
    signup_validators,
    edit_profile_validators,
)


# Form for signing in
class SigninForm(forms.Form):
    username = forms.CharField(
        validators=signin_validators["username"],
        widget=forms.TextInput(attrs={"class": "mb-6"}),
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "mb-2"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[f"{field}"].required = True
            self.fields[f"{field}"].widget.attrs["class"] += (
                " rounded-sm border px-2 py-1 focus:outline-0"
            )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        if User.objects.filter(username__iexact=username).exists():
            user = User.objects.get(username=username)
            if not user.check_password(password):
                self.add_error("password", "The password you entered is incorrect.")
        return cleaned_data


# Form for signing up
class SignupForm(forms.Form):
    username = forms.CharField(
        validators=signup_validators["username"],
        widget=forms.TextInput(attrs={"class": "mb-6"}),
    )
    email = forms.CharField(
        validators=signup_validators["email"],
        widget=forms.EmailInput(attrs={"class": "mb-6"}),
    )
    password = forms.CharField(
        validators=signup_validators["password"],
        widget=forms.PasswordInput(attrs={"class": "mb-6"}),
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "mb-2"}),
        label="Re-type password",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[f"{field}"].required = True
            self.fields[f"{field}"].widget.attrs["class"] += (
                " rounded-sm border px-2 py-1 focus:outline-0"
            )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data


class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        validators=edit_profile_validators["first_name"],
        widget=forms.TextInput(attrs={"class": ""}),
    )
    last_name = forms.CharField(
        max_length=50,
        validators=edit_profile_validators["last_name"],
        widget=forms.TextInput(attrs={"class": ""}),
    )
    birthday = forms.CharField(
        validators=edit_profile_validators["birthday"],
        widget=forms.TextInput(attrs={"class": "", "type": "date"}),
    )
    address = forms.CharField(
        max_length=100,
        validators=edit_profile_validators["address"],
        widget=forms.TextInput(attrs={"class": "w-full"}),
    )
    education = forms.CharField(
        max_length=100,
        validators=edit_profile_validators["education"],
        widget=forms.TextInput(attrs={"class": "w-full"}),
    )
    work = forms.CharField(
        max_length=100,
        validators=edit_profile_validators["work"],
        widget=forms.TextInput(attrs={"class": "w-full"}),
    )
    link = forms.CharField(
        max_length=100,
        validators=edit_profile_validators["link"],
        widget=forms.TextInput(attrs={"class": "w-full"}),
    )
    bio = forms.CharField(
        max_length=200,
        validators=edit_profile_validators["bio"],
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Describe yourself here... (max 200 words)",
                "class": "w-full resize-none",
            }
        ),
    )
    picture = forms.ImageField(
        widget=forms.FileInput(attrs={"class": "hidden"}), required=False
    )

    class Meta:
        model = Profile
        fields = (
            "first_name",
            "last_name",
            "birthday",
            "address",
            "education",
            "work",
            "link",
            "bio",
            "picture",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[f"{field}"].required = False
            self.fields[f"{field}"].widget.attrs["class"] += (
                " rounded-sm border px-2 py-1 focus:outline-0"
            )
