from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.urls import reverse

from PIL import Image


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


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
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse("users:profile", kwargs={"username": self.username})


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpg", upload_to="Profile Pictures/")

    def __str__(self) -> str:
        return f"{self.user.email} Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 50)
            img.thumbnail(output_size)
            img.save(self.image.path)


class Follow(models.Model):
    """Model to represent following relationships"""

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following"
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followers"
    )
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("follower", "following")

    def __str__(self):
        return f"User {self.follower} follows {self.following}"

    def save(self, *args, **kwargs):
        # ensure users cannot follow themselves
        if self.follower == self.following:
            raise ValidationError("User cannot follow themselves.")
        super().save(*args, **kwargs)
