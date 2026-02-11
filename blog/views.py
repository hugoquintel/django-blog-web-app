from django.urls import reverse
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from blog.models import Blog
from interaction.models import Comment
from interaction.forms import CommentForm
from blog.forms import CreateBlogForm, BlogSectionFormSet


def index_view(request):
    blogs = Blog.objects.all()
    context = {"blogs": blogs}
    return render(request, "blog/index.html", context)


def detail_view(request, blog_id, partial="None"):
    template = "blog/detail.html"
    blog = get_object_or_404(Blog, id=blog_id)
    root_comments = Comment.objects.filter(blog=blog, depth=1)
    form = CommentForm()
    context = {"blog": blog, "root_comments": root_comments, "form": form}
    if request.htmx and partial != "partial":
        template = f"{template}#{partial}"
    return render(request, template, context)


@login_required
def create_edit_view(request, partial="None", blog_id=None):
    context, del_ids = {"blog_id": blog_id}, set()
    template = "blog/create-edit.html"
    blog = get_object_or_404(Blog, id=blog_id) if blog_id else None
    if request.method == "POST":
        form_blog = CreateBlogForm(request.POST, instance=blog)
        formset_blog_sections = BlogSectionFormSet(
            request.POST, request.FILES, instance=blog
        )
        del_ids = {
            int(del_id) for del_id in request.POST.getlist("delete_ids") if del_id
        }
        if form_blog.is_valid() and formset_blog_sections.is_valid():
            if blog_id:
                for formset_blog_section in formset_blog_sections:
                    if formset_blog_section.cleaned_data.get("picture_delete"):
                        formset_blog_section.instance.picture = None
                        formset_blog_section.instance.picture_title = None
                        formset_blog_section.instance.save()
                blog = form_blog.save()
                blog_sections = formset_blog_sections.save()
            else:
                blog = form_blog.save(commit=False)
                blog.user = request.user
                blog.save()
                formset_blog_sections.instance = blog
                blog_sections = formset_blog_sections.save()

            for blog_section in blog_sections:
                if blog_section.picture:
                    blog.picture = blog_section.picture
                    blog.save()
                    break
            else:
                blog.picture = None
                blog.save()

            headers = {
                "HX-Location": reverse("blog:detail", kwargs={"blog_id": blog.id})
            }
            return HttpResponse(headers=headers)
    else:
        form_blog = CreateBlogForm(instance=blog)
        formset_blog_sections = BlogSectionFormSet(instance=blog)

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
    blog = get_object_or_404(Blog, id=blog_id)
    if request.user != blog.user:
        raise PermissionDenied()
    blog.delete()
    return redirect("blog:index")
