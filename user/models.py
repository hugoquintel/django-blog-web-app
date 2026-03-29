from django.db import models
from django.db.models import Exists, OuterRef
from django.contrib.auth.models import AbstractUser, UserManager

from config.manager import QuerySetMixin


def user_profile_picture_path(instance, filename):
    return f"{instance.username}/profile_picture/{filename}"


class UserQuerySet(QuerySetMixin, models.QuerySet):
    def with_is_followed(self, user, filter_conditions=None):
        is_followed_subquery = User.followings.through.objects.filter(
            from_user=user, to_user=OuterRef("pk")
        )
        users = (
            self.filter_with_dict(filter_conditions) if filter_conditions else self
        ).annotate(is_followed=Exists(is_followed_subquery))
        return users


class CustomUserManager(UserManager.from_queryset(UserQuerySet)):
    def get_queryset(self):
        return self._queryset_class(self.model, using=self._db)


class User(AbstractUser):
    is_private = models.BooleanField(default=False)
    birthday = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=100, blank=True)
    work = models.CharField(max_length=100, blank=True)
    link = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=200, blank=True)
    picture = models.ImageField(upload_to=user_profile_picture_path, blank=True)
    followings = models.ManyToManyField(
        "self", related_name="followers", symmetrical=False, blank=True
    )
    blog_count = models.PositiveBigIntegerField(default=0)
    following_count = models.PositiveBigIntegerField(default=0)
    follower_count = models.PositiveBigIntegerField(default=0)
    # custom manager
    objects = CustomUserManager()
