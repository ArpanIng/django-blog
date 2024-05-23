from django.contrib import admin
from django.db import models
from tinymce.widgets import TinyMCE

from .models import Comment, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "author", "tag_list", "publish", "status"]
    list_filter = ["status", "publish", "author"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ["author"]
    date_hierarchy = "publish"
    ordering = ["status", "-publish"]
    readonly_fields = ("publish", "updated")

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("tags")

    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())

    formfield_overrides = {
        models.TextField: {"widget": TinyMCE()},
    }


class CustomTinyMCE(TinyMCE):
    def __init__(self, *args, **kwargs):
        # Check if mce_attrs exist in kwargs
        if "mce_attrs" not in kwargs:
            kwargs["mce_attrs"] = {}
        kwargs["mce_attrs"]["toolbar"] = "bold italic"
        kwargs["mce_attrs"]["width"] = "620"
        kwargs["mce_attrs"]["height"] = "260"
        kwargs["mce_attrs"]["menubar"] = False
        super().__init__(*args, **kwargs)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["author", "post", "created", "active"]
    list_filter = ["active", "created", "updated"]
    search_fields = ["name", "email"]
    readonly_fields = ("created", "updated")

    formfield_overrides = {
        models.TextField: {"widget": CustomTinyMCE()},
    }
