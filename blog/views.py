from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from user.models import Profile
from blog.models import Blog
from blog.forms import CreateBlogForm, BlogSectionFormSet


def index_view(request):
    blogs = Blog.objects.all()
    context = {"blogs": blogs}
    return render(request, "blog/index.html", context)


def detail_view(request, blog_id, render_type="full"):
    template = "blog/detail.html"
    partial = "content"

    user = request.user
    profile = get_object_or_404(Profile, user=user)
    blog = get_object_or_404(Blog, id=blog_id)
    blog_sections = blog.blogsection_set.all()

    context = {
        "user": user,
        "profile": profile,
        "blog": blog,
        "blog_sections": blog_sections,
    }

    if request.htmx and render_type == "partial":
        template = f"{template}#{partial}"

    return render(request, template, context)


def delete_view(request):
    return HttpResponse("nothing yet")


@login_required
def create_edit_view(request, blog_id=None):
    context, del_ids = {"blog_id": blog_id}, set()
    template, partial = "blog/create-edit.html", "form"
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

    if request.htmx:
        template = f"{template}#{partial}"
    return render(request, template, context)
