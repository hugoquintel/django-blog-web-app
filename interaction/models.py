from django.db import models
from django.contrib.auth.models import User

from blog.models import Blog
from treebeard.mp_tree import MP_Node


# Create your models here.
class Comment(MP_Node):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    content = models.TextField()
    liked_by = models.ManyToManyField(User, related_name="liked_comments", blank=True)
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content
