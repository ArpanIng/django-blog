from django import forms
from taggit.models import Tag
from tinymce.widgets import TinyMCE

from .models import Comment, Post


class PostModelForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
    )

    def __init__(self, *args, **kwargs):
        super(PostModelForm, self).__init__(*args, **kwargs)
        self.fields["tags"].required = False

    class Meta:
        model = Post
        fields = (
            "title",
            "overview",
            "thumbnail",
            "content",
            "status",
            "tags",
        )
        widgets = {"content": TinyMCE()}


class CustomCommentTinyMCE(TinyMCE):
    def __init__(self, height="260px", placeholder="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs["placeholder"] = placeholder
        self.mce_attrs["height"] = height
        self.mce_attrs["toolbar"] = "bold italic"
        self.mce_attrs["menubar"] = False
        self.mce_attrs["statusbar"] = False


class CommentModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommentModelForm, self).__init__(*args, **kwargs)
        self.fields["comment"].widget.attrs.update(
            (
                {
                    "rows": "6",
                }
            )
        )

    class Meta:
        model = Comment
        fields = ("comment",)
        widgets = {
            "comment": CustomCommentTinyMCE(
                placeholder="Join the discussion and leave a comment!"
            )
        }
