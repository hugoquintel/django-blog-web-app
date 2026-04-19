from django.db import models
from django.urls import reverse
from django.db.models import UniqueConstraint
from django.db.models import Exists, OuterRef
from django.contrib.auth.models import AbstractUser, UserManager

from config.manager import QuerySetMixin


def user_profile_picture_path(instance, filename):
    return f"{instance.username}/profile_picture/{filename}"


class UserQuerySet(QuerySetMixin, models.QuerySet):
    def with_is_followed(self, user, filter_conditions=None):
        is_followed_subquery = Follow.objects.filter(
            follower=user, following=OuterRef("pk")
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
        "self",
        through="Follow",
        related_name="followers",
        symmetrical=False,
        blank=True,
    )
    blog_count = models.PositiveBigIntegerField(default=0)
    following_count = models.PositiveBigIntegerField(default=0)
    follower_count = models.PositiveBigIntegerField(default=0)
    # custom manager
    objects = CustomUserManager()

    def get_absolute_url(self):
        return reverse("user:profile", kwargs={"user_id": self.id, "partial": None})


class Follow(models.Model):
    # The person who is following
    follower = models.ForeignKey(
        User, related_name="following_set", on_delete=models.CASCADE
    )
    # The person being followed
    following = models.ForeignKey(
        User, related_name="follower_set", on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["follower", "following"],
                name="unique_follow",
            )
        ]
