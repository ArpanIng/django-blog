from html import unescape

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.html import strip_tags
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    """
    Custom Manager
    Returns: Post with 'PUBLISHED' status
    """

    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"

    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    overview = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Enter a brief overview or summary of the post here.",
    )
    content = models.TextField()
    thumbnail = models.ImageField(
        upload_to="post_images/",
        null=True,
        blank=True,
        help_text="Upload an image to accompany this post.",
    )
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.DRAFT
    )
    tags = TaggableManager(blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_posts",
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="post_likes",
    )
    publish = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()  # default Manager
    published = PublishedManager()  # custom Manager

    class Meta:
        ordering = ["-publish"]
        indexes = [
            models.Index(fields=["-publish"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "blogs:post_detail",
            kwargs={"username": self.author.username, "post_slug": self.slug},
        )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def get_read_time(self):
        """Calculate the estimated read time for the content of the object."""

        # calculates the read time based on the total word count of the title, and content
        string = self.title + unescape(strip_tags(self.content))
        total_words = len(string.split())
        # 200 = assumed average reading speed of words per minute
        read_time = round(total_words / 200)
        return max(read_time, 1)

    def get_comments(self):
        return self.comments.filter(active=True).select_related(
            "author", "author__profile"
        )

    def get_total_comments(self):
        """
        Returns the total number of active comments associated with a post.
        """
        return self.comments.filter(active=True).count()

    def get_likes(self):
        return self.likes.all()

    def get_likes_count(self):
        return self.likes.count()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    edited = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["created"]),
        ]

    def __str__(self) -> str:
        return f"Commented by {self.author.email} on post {self.post}"

    def get_absolute_url(self):
        return reverse(
            "blogs:post_detail",
            kwargs={"username": self.author.username, "post_slug": self.post.slug},
        )
