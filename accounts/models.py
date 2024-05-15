from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from PIL import Image


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    headline = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Enter a brief headline that describes you or your role",
    )
    about = models.TextField(max_length=1000, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse("users:profile", kwargs={"username": self.username})

    def get_full_name(self):
        """
        Return the first_name and the last_name, with a space in between
        else return the username.
        """
        if self.first_name and self.last_login:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.username


class Profile(models.Model):
    """Model to represent user profile"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    image = models.ImageField(
        default="default_profile.jpg", upload_to="Profile Pictures/"
    )
    follows = models.ManyToManyField(
        "self",
        related_name="followers",
        symmetrical=False,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.user.email} Profile"

    # def clean(self):  error
    #     super().clean()
    #     if self.follows.filter(pk=self.pk).exists():
    #         raise ValidationError("User cannot follow themselves.")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 50)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def get_followers(self):
        """Retrieve all followers"""
        return self.followers.all()

    def get_followings(self):
        """Retrieve all followings"""
        return self.follows.all()

    def get_followers_count(self):
        return self.followers.count()

    def get_followings_count(self):
        return self.follows.count()
