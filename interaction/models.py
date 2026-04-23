from django.db import models
from django.conf import settings
from treebeard.mp_tree import MP_Node, MP_NodeQuerySet, MP_NodeManager
from django.db.models import Q, F, CheckConstraint, UniqueConstraint, Exists, OuterRef

from config.manager import QuerySetMixin


# custom django-treebeard manager must inherit from specific tree's manager https://django-treebeard.readthedocs.io/en/latest/mp_tree.html#treebeard.mp_tree.MP_NodeQueryset
class CommentQuerySet(QuerySetMixin, MP_NodeQuerySet):
    def with_is_liked(self, user, extra_annotations=None, filter_conditions=None):
        is_liked_subquery = Like.objects.filter(comment=OuterRef("pk"), user=user)
        comments = (
            self.filter_with_dict(filter_conditions) if filter_conditions else self
        ).annotate(is_liked=Exists(is_liked_subquery), **extra_annotations)
        return comments


class CommentManager(MP_NodeManager.from_queryset(CommentQuerySet)):
    def get_queryset(self):
        return self._queryset_class(self.model, using=self._db).order_by("path")


class Comment(MP_Node):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    blog = models.ForeignKey(
        "blog.Blog", on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Like",
        through_fields=("comment", "user"),
        related_name="liked_comments",
        blank=True,
    )
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CommentManager()

    def __str__(self):
        return self.content


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    blog = models.ForeignKey(
        "blog.Blog", null=True, blank=True, on_delete=models.CASCADE
    )
    comment = models.ForeignKey(
        Comment, null=True, blank=True, on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            CheckConstraint(
                condition=(
                    Q(blog__isnull=False, comment__isnull=True)
                    | Q(blog__isnull=True, comment__isnull=False)
                ),
                name="only_one_instance",
            ),
            *[
                UniqueConstraint(fields=["user", field], name=f"unique_like_{field}")
                for field in ("blog", "comment")
            ],
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        instance = self.blog or self.comment
        instance.like_count = F("like_count") + 1
        instance.save(update_fields=["like_count"])

    def delete(self, *args, **kwargs):
        instance = self.blog or self.comment
        super().delete(*args, **kwargs)
        instance.like_count = F("like_count") - 1
        instance.save(update_fields=["like_count"])
