from django import forms
from blog.models import Blog, BlogSection
from django.forms.models import inlineformset_factory

from blog.validators import blog_validators, blog_section_validators


class CreateBlogForm(forms.ModelForm):
    title = forms.CharField(
        max_length=100,
        validators=blog_validators["title"],
        widget=forms.TextInput(
            attrs={
                "placeholder": "Title",
                "class": "w-full text-3xl focus:outline-0",
            },
        ),
    )
    description = forms.CharField(
        validators=blog_validators["description"],
        widget=forms.Textarea(
            attrs={
                "placeholder": "A quick description (150 words)",
                "class": "border-gray-light text-gray-dark w-full resize-none border-b text-2xl focus:outline-0 overflow-visible",
            },
        ),
    )
    description.widget.attrs.pop("cols", None)
    description.widget.attrs.pop("rows", None)

    class Meta:
        model = Blog
        fields = ("title", "description")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[f"{field}"].required = True


class CreateBlogSectionForm(forms.ModelForm):
    title = forms.CharField(
        required=True,
        validators=blog_section_validators["title"],
        widget=forms.TextInput(
            attrs={
                "placeholder": "Section title",
                "class": "w-full text-xl focus:outline-0",
            }
        ),
    )
    content = forms.CharField(
        required=True,
        validators=blog_section_validators["content"],
        widget=forms.Textarea(
            attrs={
                "placeholder": "Section content",
                "class": "w-full resize-none text-gray-dark text-lg focus:outline-0",
            },
        ),
    )
    content.widget.attrs.pop("cols", None)
    content.widget.attrs.pop("rows", None)
    picture_delete = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"class": "hidden"})
    )
    picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"class": "hidden"}),
    )
    picture_title = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Your image title",
                "class": "border-gray-base w-4/10 rounded-sm border p-1",
            },
        ),
    )

    class Meta:
        model = BlogSection
        fields = ("title", "content", "picture", "picture_title")

    def clean(self):
        data = super().clean()
        if data.get("picture_delete"):
            data["picture"], data["picture_title"] = "", ""
        return data


BlogSectionFormSet = inlineformset_factory(
    Blog, BlogSection, form=CreateBlogSectionForm, can_delete=True, extra=0
)


class SearchForm(forms.Form):
    BASE_CHOICES = {
        "Filter": [
            ("none", "None", ""),
            ("all", "All", ""),
            ("following", "Following", ""),
        ],
        "Match": [
            ("contain", "Contain", ""),
            ("exact", "Exact", ""),
        ],
    }
    PEOPLE_CHOICES = {
        **BASE_CHOICES,
        "Search by": [
            ("username", "Name", ""),
            ("bio", "Bio", ""),
        ],
        "Order by": [
            ("popularity", "Popularity", ""),
            ("date", "Date", "Date joined"),
        ],
    }
    POSTS_CHOICES = {
        **BASE_CHOICES,
        "Search by": [
            ("title", "Title", ""),
            ("description", "Description", ""),
            ("content", "Content", ""),
        ],
        "Order by": [
            ("popularity", "Popularity", ""),
            ("date", "Date", "Date posted"),
        ],
    }

    people = forms.ChoiceField(
        choices=PEOPLE_CHOICES, required=False, widget=forms.Select()
    )
    posts = forms.ChoiceField(
        choices=POSTS_CHOICES, required=False, widget=forms.Select()
    )

    search_input = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search",
                "class": "grow px-4 py-1 focus:outline-none",
            },
        ),
    )

    # break it down into multiple stuffs
