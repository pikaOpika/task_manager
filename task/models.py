import uuid

from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class Position(models.Model):
    name = models.CharField(
        max_length=200,
    )

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ["name"]

class TaskType(models.Model):
    name = models.CharField(
        max_length=200,
    )

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ["name"]
    
class Task(models.Model):
    class Choices(models.TextChoices):
        urgent = "U", "Urgent"
        high = "H", "High"
        low = "L", "Low"


    name = models.CharField(
        max_length=100,
    )
    description = models.TextField()
    deadline = models.DateField()
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=30,
        choices=Choices, default=Choices.low
    )
    task_type = models.ForeignKey(
        TaskType, on_delete=models.SET_NULL,
        related_name="tasks",
        null=True, blank=True
    )
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="tasks"
    )
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        slugify_name = slugify(f"task-{uuid.uuid4().hex[:8]}")
        if not self.slug:
            self.slug = slugify_name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Worker(AbstractUser):
    position = models.ForeignKey(
        Position, related_name="workers", on_delete=models.CASCADE,
        null=True, blank=True,
    )
    image = models.ImageField(upload_to="user_photo", null=True, blank=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        slugify_username = slugify(self.username)
        if not self.slug or self.slug != slugify_username:
            self.slug = slugify_username
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} {self.position}"
