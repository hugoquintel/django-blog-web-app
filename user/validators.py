from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, EmailValidator, MinLengthValidator


# Sign in validators
def UserNotExist(value):
    if not User.objects.filter(username__iexact=value).exists():
        raise ValidationError("There is no user with this username.")


signin_validators = {"username": [UserNotExist]}


# Sign up validators


# username
def ValidCharacters(value):
    if not value.isalnum():
        raise ValidationError("Only alphanumeric characters are allowed.")


def ForbiddenUsers(value):
    forbidden_users = [
        "admin",
        "css",
        "js",
        "auth",
        "authenticate",
        "login",
        "logout",
        "administrator",
        "root",
        "email",
        "user",
        "join",
        "sql",
        "static",
        "python",
        "delete",
    ]
    if value.lower() in forbidden_users:
        raise ValidationError("Invalid name for user, this is a reserverd word.")


def UsernameLengthValidator(value):
    if len(value) < 4 or len(value) > 30:
        raise ValidationError("Length of username must be between 4 and 30 characters.")


def UniqueUser(value):
    if User.objects.filter(username__iexact=value).exists():
        raise ValidationError("A user with this username already exists.")


# email
ValidEmail = EmailValidator(
    message="That's not a valid email format, please correct it."
)


def UniqueEmail(value):
    if User.objects.filter(email__iexact=value).exists():
        raise ValidationError("A user with this email already exists.")


# password

ValidPassword = RegexValidator(
    r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z\d]).+$",
    message="Password must contain numbers, uppercase and lowercase letters and special characters.",
    code="invalid_password",
)

PasswordLengthValidator = MinLengthValidator(
    8, message="Password must be at least 8 characters long."
)

signup_validators = {
    "username": [ValidCharacters, ForbiddenUsers, UsernameLengthValidator, UniqueUser],
    "email": [ValidEmail, UniqueEmail],
    "password": [ValidPassword, PasswordLengthValidator],
}
