from pathlib import Path
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse
from django.db.models import F, Value
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from blog.models import Blog
from interaction.models import Comment
from interaction.forms import CommentForm
from blog.forms import CreateBlogForm, BlogSectionFormSet, SearchForm
from config.utils import (
    User,
    tailwind_comment_spaces,
    sign_in_url,
    paginate_and_get_page,
    get_snapshot,
)


@login_required(login_url=sign_in_url)
def index_view(request, partial=None):
    template = "blog/index.html"
    user = request.user
    snapshot = get_snapshot(request.GET)

    current_filter, current_sort = (
        request.GET.get("filter", "following"),
        request.GET.get("sort", "popularity"),
    )

    filter_conditions = {"created_at__lt": snapshot}
    if current_filter == "following":
        filter_conditions["user__in"] = user.followings.all()

    blogs = (
        Blog.objects.with_is_liked_and_saved(
            user=user, filter_conditions=filter_conditions
        )
        .order_by(
            "-like_count" if current_sort == "popularity" else "-created_at", "-id"
        )
        .select_related("user")
    )

    context = {
        "blogs": paginate_and_get_page(blogs, request.GET.get("page", 1)),
        "filter_types": ("following", "all"),
        "sort_types": ("popularity", "date"),
        "current_filter": current_filter,
        "current_sort": current_sort,
        "snapshot": snapshot,
    }
    if request.htmx and partial != "None":
        template = f"{template}#{partial}"
    return render(request, template, context)


def detail_view(request, root_depth, blog_id, comment_id=None, partial=None):
    template = "blog/detail.html"
    user = request.user
    blog = get_object_or_404(Blog, id=blog_id)
    snapshot = get_snapshot(request.GET)

    extra_annotations = {
        "level": F("depth") - 1 if root_depth == 1 else F("depth") % root_depth,
        "is_added": Value(False),
    }
    filter_conditions = {
        "created_at__lt": snapshot,
        "blog": blog,
        "depth__lte": root_depth + settings.MAX_SUBCOMMENTS,
    }

    comments = (
        Comment.get_tree(parent=get_object_or_404(Comment, id=comment_id))
        if comment_id
        else Comment.objects.all()
    ).with_is_liked(
        user=user,
        extra_annotations=extra_annotations,
        filter_conditions=filter_conditions,
    )
    context = {
        "blog": blog,
        "is_liked": user in blog.liked_by.all(),
        "is_followed": user in blog.user.followers.all(),
        "comments": paginate_and_get_page(comments, request.GET.get("page", 1)),
        "form": CommentForm(),
        "root_depth": root_depth,
        "max_subcomments": settings.MAX_SUBCOMMENTS,
        "tailwind_comment_spaces": tailwind_comment_spaces,
        "snapshot": snapshot,
    }
    if comment_id:
        context["is_detailed"] = True
        context["thread_depth"] = root_depth // settings.MAX_SUBCOMMENTS

    if request.htmx and partial != "None":
        template = f"{template}#{partial}"
    return render(request, template, context)


@login_required(login_url=sign_in_url)
def create_edit_view(request, blog_id=None, partial=None):
    context, del_ids = {"blog_id": blog_id}, set()
    template = "blog/create-edit.html"
    blog = get_object_or_404(Blog, id=blog_id) if blog_id else None
    if request.method == "POST":
        form_blog, formset_blog_sections = (
            CreateBlogForm(request.POST, instance=blog),
            BlogSectionFormSet(request.POST, request.FILES, instance=blog),
        )
        del_ids_list = request.POST.getlist("delete_ids")
        del_ids = {int(del_id) for del_id in del_ids_list if del_id}

        if form_blog.is_valid() and formset_blog_sections.is_valid():
            user = request.user
            blog, created = Blog.objects.update_or_create(
                id=blog_id,
                defaults={**form_blog.cleaned_data},
                create_defaults={"user": user, **form_blog.cleaned_data},
            )
            if created:
                user.blog_count = user.blogs.count()
                user.save(update_fields=["blog_count"])
                formset_blog_sections.instance = blog
            formset_blog_sections.save()
            section_with_picture = blog.sections.exclude(picture__exact="").first()
            blog.picture = section_with_picture.picture if section_with_picture else ""
            blog.save(update_fields=["picture"])
            headers = {
                "HX-Location": reverse(
                    "blog:detail",
                    kwargs={
                        "root_depth": 1,
                        "blog_id": blog.id,
                        "comment_id": 0,
                        "partial": None,
                    },
                )
            }
            return HttpResponse(headers=headers)
    else:
        form_blog, formset_blog_sections = (
            CreateBlogForm(instance=blog),
            BlogSectionFormSet(instance=blog),
        )

    context["form_blog"] = form_blog
    context["formset_blog_sections"] = formset_blog_sections
    context["management_form"] = formset_blog_sections.management_form
    context["empty_form"] = formset_blog_sections.empty_form
    context["delete_ids"] = del_ids

    if request.htmx and partial != "None":
        template = f"{template}#{partial}"
    return render(request, template, context)


@require_POST
def delete_view(request, blog_id):
    user = request.user
    blog = get_object_or_404(Blog, id=blog_id)
    if user != blog.user:
        raise PermissionDenied()
    blog_folder = Path(settings.MEDIA_ROOT) / blog.user.username / f"blog_{blog.id}"
    blog.delete()
    try:
        blog_folder.rmdir()
    except (FileNotFoundError, OSError) as e:
        print(f"Error: {e}")

    user.blog_count = user.blogs.count()
    user.save(update_fields=["blog_count"])
    return redirect("blog:index", partial="content")


def search_view(request, partial=None):
    template = "blog/search-advanced.html"
    user = request.user
    snapshot = get_snapshot(request.GET)
    options = {"filter", "search_by", "match", "order_by"}
    form = SearchForm(request.GET)
    queries = form.data
    people_queries, posts_queries = (
        {option: queries.get(f"people_{option}") for option in options},
        {option: queries.get(f"posts_{option}") for option in options},
    )
    user_input = queries.get("search_input")

    # people
    people_conditions = {"date_joined__lt": snapshot}
    if people_queries["filter"] in (None, "none") or user_input == "":
        users = User.objects.none()
    else:
        if people_queries["filter"] == "following":
            people_conditions["followers"] = user
        search_by, match_case = (
            ("bio" if people_queries["search_by"] == "bio" else "username"),
            ("__iexact" if people_queries["match"] == "exact" else "__icontains"),
        )
        people_conditions[f"{search_by}{match_case}"] = user_input
        order_by = (
            "-follower_count"
            if people_queries["order_by"] == "popularity"
            else "-date_joined"
        )
        users = (
            User.objects.with_is_followed(
                user=user, filter_conditions=people_conditions
            )
            .exclude(username=user.username)
            .order_by(order_by)
        )

    # posts
    posts_conditions = {"created_at__lt": snapshot}
    if posts_queries["filter"] in (None, "none") or user_input == "":
        blogs = Blog.objects.none()
    else:
        if posts_queries["filter"] == "following":
            posts_conditions["user__followers"] = user

        match_case = "__iexact" if posts_queries["match"] == "exact" else "__icontains"

        if posts_queries["search_by"] == "description":
            search_by = "description"
        elif posts_queries["search_by"] == "title":
            search_by = "title"
        else:
            search_by = "sections__content"

        posts_conditions[f"{search_by}{match_case}"] = user_input
        order_by = (
            "-like_count"
            if posts_queries["order_by"] == "popularity"
            else "-created_at"
        )
        blogs = (
            Blog.objects.with_is_liked_and_saved(
                user=user, filter_conditions=posts_conditions
            )
            .order_by(order_by)
            .select_related("user")
        )

    context = {
        "form": form,
        "users": paginate_and_get_page(users, request.GET.get("page", 1)),
        "blogs": paginate_and_get_page(blogs, request.GET.get("page", 1)),
        "snapshot": snapshot,
    }
    if request.htmx and partial != "None":
        template = f"{template}#{partial}"
    return render(request, template, context)
