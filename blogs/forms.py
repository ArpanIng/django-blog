from django import forms

from .models import Post, Comment


class PostModelForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "thumbnail", "content", "reading_time_minutes")


class CommentModelForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("comment",)

    def __init__(self, *args, **kwargs):
        super(CommentModelForm, self).__init__(*args, **kwargs)
        self.fields["comment"].widget.attrs.update(
            (
                {
                    "class": "form-control",
                    "rows": "3",
                    "placeholder": "Join the discussion and leave a comment!",
                }
            )
        )
