from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.http import Http404

from blog.models import Blog
from interaction.models import Comment
from interaction.forms import CommentForm


@login_required(login_url=reverse_lazy("user:sign-in"))
@require_POST
def like_view(request, blog_id=0, comment_id=0):
    user = request.user
    if blog_id:
        instance = get_object_or_404(Blog, id=blog_id)
    elif comment_id:
        instance = get_object_or_404(Comment, id=comment_id)
    else:
        return Http404("No instance founded")

    if instance.liked_by.filter(id=user.id).exists():
        instance.liked_by.remove(user)
    else:
        instance.liked_by.add(user)
    instance.save()
    return render(request, "interaction/like.html", {"instance": instance})


@login_required(login_url=reverse_lazy("user:sign-in"))
@require_POST
def save_view(request, blog_id):
    user, blog = request.user, get_object_or_404(Blog, id=blog_id)
    if blog.saved_by.filter(id=user.id).exists():
        blog.saved_by.remove(user)
    else:
        blog.saved_by.add(user)
    blog.save()
    return render(request, "interaction/save.html", {"blog": blog})


def comment_view(request, blog_id, comment_id=None):
    template = "blog/detail.html"
    partial = "comment-form"
    blog = get_object_or_404(Blog, id=blog_id)
    context = {"blog": blog}
    if comment_id:
        comment = get_object_or_404(Comment, id=comment_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.blog = blog
            new_comment.user = request.user
            if comment_id:
                comment.add_child(instance=new_comment)
            else:
                Comment.add_root(instance=new_comment)
            context["root_comments"] = Comment.objects.filter(blog=blog, depth=1)
            form = CommentForm()
            partial = "comment"
    else:
        form = CommentForm()

    context["form"] = form

    template = f"{template}#{partial}"
    response = render(request, template, context)
    if partial == "comment":
        response["HX-Retarget"] = "#comment"
    return response
