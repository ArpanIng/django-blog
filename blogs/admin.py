from django.contrib import admin

from .models import Post, Comment


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


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["author", "post", "created", "active"]
    list_filter = ["active", "created", "updated"]
    search_fields = ["name", "email"]
    readonly_fields = ("created", "updated")
