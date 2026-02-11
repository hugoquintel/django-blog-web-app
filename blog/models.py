from django.db import models
from django.contrib.auth.models import User


def user_blog_section_picture_path(instance, filename):
    return f"{instance.blog.user}/blog_{instance.blog.id}/{filename}"


# Create your models here.
class Blog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    picture = models.ImageField(null=True, blank=True)
    saved_by = models.ManyToManyField(User, related_name="saved_blogs", blank=True)
    liked_by = models.ManyToManyField(User, related_name="liked_blogs", blank=True)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class BlogSection(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    picture = models.ImageField(
        upload_to=user_blog_section_picture_path, null=True, blank=True
    )
    picture_title = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.title} | blog: {self.blog.title} "
