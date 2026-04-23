from django import forms

from config.utils import User
from user.validators import (
    signin_validators,
    signup_validators,
    edit_profile_validators,
)


# Form for signing in
class SigninForm(forms.Form):
    username = forms.CharField(
        validators=signin_validators["username"],
        widget=forms.TextInput(),
    )
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[f"{field}"].required = True
            self.fields[f"{field}"].widget.attrs[
                "class"
            ] = "rounded-sm border px-2 py-1 focus:outline-0"

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
        widget=forms.TextInput(),
    )
    email = forms.CharField(
        validators=signup_validators["email"],
        widget=forms.EmailInput(),
    )
    password = forms.CharField(
        validators=signup_validators["password"],
        widget=forms.PasswordInput(),
    )
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[f"{field}"].required = True
            self.fields[f"{field}"].widget.attrs[
                "class"
            ] = "rounded-sm border px-2 py-1 focus:outline-0"

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
        widget=forms.TextInput(),
    )
    last_name = forms.CharField(
        max_length=50,
        validators=edit_profile_validators["last_name"],
        widget=forms.TextInput(),
    )
    birthday = forms.CharField(
        validators=edit_profile_validators["birthday"],
        widget=forms.TextInput(attrs={"type": "date"}),
    )
    address = forms.CharField(
        max_length=100,
        validators=edit_profile_validators["address"],
        widget=forms.TextInput(),
    )
    education = forms.CharField(
        max_length=100,
        validators=edit_profile_validators["education"],
        widget=forms.TextInput(),
    )
    work = forms.CharField(
        max_length=100,
        validators=edit_profile_validators["work"],
        widget=forms.TextInput(),
    )
    link = forms.CharField(
        max_length=100,
        validators=edit_profile_validators["link"],
        widget=forms.TextInput(),
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
    picture = forms.ImageField(widget=forms.FileInput())

    class Meta:
        model = User
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
            self.fields[f"{field}"].widget.attrs[
                "class"
            ] = "rounded-sm border px-2 py-1 focus:outline-0"

    def clean_birthday(self):
        birthday = self.cleaned_data.get("birthday")
        return None if birthday == "" else birthday


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(
        validators=signup_validators["password"], widget=forms.PasswordInput()
    )
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[f"{field}"].required = True
            self.fields[f"{field}"].widget.attrs[
                "class"
            ] = "rounded-sm border px-2 py-1 focus:outline-0"

    def clean(self):
        cleaned_data = super().clean()
        user = self.user
        old_password = cleaned_data.get("old_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if not user.check_password(old_password):
            self.add_error("old_password", "The password you entered is incorrect.")
        if new_password != confirm_password:
            self.add_error("new_password", "The passwords you entered don't match.")
        return cleaned_data
