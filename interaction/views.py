from django.db.models import F
from django.http import Http404
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from blog.models import Blog
from user.models import Follow
from django.conf import settings
from interaction.forms import CommentForm
from interaction.models import Comment, Like
from config.utils import User, tailwind_comment_spaces

instance_dict = {"blog": Blog, "comment": Comment}


@login_required(login_url=reverse_lazy("user:sign-in", kwargs={"partial": None}))
@require_POST
def like_view(request, instance_model, instance_id):
    # change to try except
    user = request.user
    if instance_model not in ("blog", "comment"):
        return Http404("No instance founded")
    context = {}
    instance = get_object_or_404(instance_dict[instance_model], id=instance_id)
    params = {instance_model: instance, "user": user}
    try:
        Like.objects.get(**params).delete()
        context["is_liked"] = False
    except Like.DoesNotExist:
        Like.objects.create(**params)
        context["is_liked"] = True
    instance.refresh_from_db()
    context["instance"] = instance
    return render(request, "interaction/like.html#like", context)


@login_required(login_url=reverse_lazy("user:sign-in"))
@require_POST
def save_view(request, blog_id):
    user, blog = request.user, get_object_or_404(Blog, id=blog_id)
    context = {}
    if blog.saved_by.filter(id=user.id).exists():
        blog.saved_by.remove(user)
        context["is_saved"] = False
    else:
        blog.saved_by.add(user)
        context["is_saved"] = True
    return render(request, "interaction/save.html#save", context)


@login_required(login_url=reverse_lazy("user:sign-in"))
@require_POST
def follow_view(request, user_to_follow_id):
    current_user, user_to_follow = (
        request.user,
        get_object_or_404(User, id=user_to_follow_id),
    )
    if current_user == user_to_follow:
        raise PermissionDenied()
    context = {}
    try:
        Follow.objects.get(follower=current_user, following=user_to_follow).delete()
        context["is_followed"] = False
    except Follow.DoesNotExist:
        Follow.objects.create(follower=current_user, following=user_to_follow)
        context["is_followed"] = True
    return render(request, "interaction/follow.html#follow", context)


def comment_view(request, level, blog_id, comment_id=None):
    template, partial = "blog/detail.html", "comment_form"
    user, blog = request.user, get_object_or_404(Blog, id=blog_id)
    headers = {}
    context = {
        "blog_id": blog.id,
        "tailwind_comment_spaces": tailwind_comment_spaces,
    }
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.blog, new_comment.user = blog, user

            if comment_id:
                comment = get_object_or_404(Comment, id=comment_id)
                comment.add_child(instance=new_comment)
                if level >= settings.MAX_SUBCOMMENTS:
                    return redirect(
                        "blog:detail",
                        blog_id=blog_id,
                        root_depth=comment.depth,
                        comment_id=comment.id,
                        partial="comments",
                    )
                new_comment.level = level + 1
                new_comment.parent_id = comment_id
                headers["HX-Retarget"] = f"#comment-{comment_id}"
                headers["HX-Reswap"] = "afterend show:none"
            else:
                Comment.add_root(instance=new_comment)
                new_comment.level = 0
                headers["HX-Retarget"] = "#comments"
                headers["HX-Reswap"] = "afterbegin show:none"
                new_comment.parent_id = new_comment.id
            form.save_m2m()
            new_comment.is_added = True
            blog.comment_count = blog.comments.count()
            blog.save(update_fields=["comment_count"])

            context["comment"] = new_comment
            context["comment_count"] = blog.comment_count
            context["max_subcomments"] = settings.MAX_SUBCOMMENTS
            response = render(request, "interaction/comment.html", context)
            for key in headers:
                response[key] = headers[key]
            return response
    else:
        form = CommentForm()

    context["form"] = form
    template = f"{template}#{partial}"
    response = render(request, template, context)
    response["HX-Retarget"] = "#comment-form"
    return response
