from django.db import models
from django.conf import settings
from django.db.models import Exists, OuterRef

from interaction.models import Like
from config.manager import QuerySetMixin


def user_blog_section_picture_path(instance, filename):
    return f"{instance.blog.user}/blog_{instance.blog.id}/{filename}"


class BlogQuerySet(QuerySetMixin, models.QuerySet):
    def with_is_liked(self, user, filter_conditions=None):
        is_liked_subquery = Like.objects.filter(blog=OuterRef("pk"), user=user)
        blogs = (
            self.filter_with_dict(filter_conditions)
            if filter_conditions
            else self.all()
        ).annotate(is_liked=Exists(is_liked_subquery))
        return blogs

    def with_is_saved(self, user, filter_conditions=None):
        is_saved_subquery = Blog.saved_by.through.objects.filter(
            blog=OuterRef("pk"), user=user
        )
        blogs = (
            self.filter_with_dict(filter_conditions)
            if filter_conditions
            else self.all()
        ).annotate(is_saved=Exists(is_saved_subquery))
        return blogs

    def with_is_liked_and_saved(self, user, filter_conditions=None):
        is_liked_subquery, is_saved_subquery = (
            Like.objects.filter(blog=OuterRef("pk"), user=user),
            Blog.saved_by.through.objects.filter(blog=OuterRef("pk"), user=user),
        )
        blogs = (
            self.filter_with_dict(filter_conditions)
            if filter_conditions
            else self.all()
        ).annotate(
            is_liked=Exists(is_liked_subquery), is_saved=Exists(is_saved_subquery)
        )
        return blogs


class Blog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blogs"
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    picture = models.ImageField(blank=True)
    saved_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="saved_blogs", blank=True
    )
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="interaction.Like",
        through_fields=("blog", "user"),
        related_name="liked_blogs",
        blank=True,
    )
    like_count = models.PositiveBigIntegerField(default=0)
    comment_count = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BlogQuerySet.as_manager()

    def __str__(self):
        return self.title


class BlogSection(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=100)
    content = models.TextField()
    picture = models.ImageField(upload_to=user_blog_section_picture_path, blank=True)
    picture_title = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.title} | blog: {self.blog.title} "
