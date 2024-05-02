from django import forms
from taggit.models import Tag
from taggit.forms import TagWidget

from .models import Post, Comment


# class PostModelForm(forms.ModelForm):
#     select_topic = forms.ModelMultipleChoiceField(
#         queryset=Tag.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=False,
#     )
#     add_topic = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "placeholder": "Enter new topic separated by commas",
#             }
#         ),
#         required=False,
#     )

#     class Meta:
#         model = Post
#         fields = (
#             "title",
#             "overview",
#             "thumbnail",
#             "content",
#             "select_topic",
#             "add_topic",
#             "reading_time_minutes",
#         )

#     def clean_add_topic(self):
#         add_topic = self.cleaned_data["add_topic"]
#         if add_topic:
#             # Split the input by comma and strip whitespace from each tag
#             tag_list = [tag.strip() for tag in add_topic.split(",")]
#             # Return the list of tags
#             return tag_list
#         else:
#             return []


class PostModelForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "title",
            "overview",
            "thumbnail",
            "content",
            "tags",
            "reading_time_minutes",
        )


class CommentModelForm(forms.ModelForm):
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

    class Meta:
        model = Comment
        fields = ("comment",)
