from django import forms
from interaction.models import Comment


# Form for signing up
class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 1,
                "placeholder": "Add a comment...",
                "class": "resize-none px-2 py-1.5 focus:outline-none",
            }
        )
    )

    class Meta:
        model = Comment
        fields = ("content",)