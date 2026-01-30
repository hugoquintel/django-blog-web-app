from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from profanity_check import predict


def ProfanityValidator(value):
    if predict([value]).all():
        raise ValidationError("Inappropriate words detected, try again.")


TitleLengthValidator = MaxLengthValidator(100, message="100 characters max")


blog_validators = {
    "title": [TitleLengthValidator, ProfanityValidator],
    "description": [ProfanityValidator],
}
blog_section_validators = {
    "title": [TitleLengthValidator, ProfanityValidator],
    "content": [ProfanityValidator],
}
