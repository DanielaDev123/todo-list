from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class UserProfile(AbstractUser):
    STATUS_CHOICES = [
        ("beginner", "beginner"),
        ("active", "active"),
        ("pro", "pro"),
    ]

    age = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(14), MaxValueValidator(70)],
        null=True, blank=True,
    )
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="beginner")
    date_register = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.username


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    category_img = models.ImageField(upload_to="categories/", null=True, blank=True)

    def __str__(self):
        return self.category_name


class Project(models.Model):
    project_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="projects")
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="projects")
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_name

    def get_tasks_count(self):
        return self.tasks.count()

    def get_completed_percent(self):
        total = self.tasks.count()
        if total == 0:
            return 0
        done = self.tasks.filter(completed=True).count()
        return round(done * 100 / total)


class Tag(models.Model):
    tag_name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.tag_name


class Task(models.Model):
    PRIORITY_CHOICES = [("low", "low"), ("medium", "medium"), ("high", "high")]

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    deadline = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    assignee = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="assigned_tasks",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="tasks")

    def __str__(self):
        return self.title

    def get_progress(self):
        total = self.subtasks.count()
        if total == 0:
            return 0
        done = self.subtasks.filter(completed=True).count()
        return round(done * 100 / total)

    def get_comments_count(self):
        return self.comments.count()

    def is_overdue(self):
        return bool(self.deadline) and self.deadline < timezone.now() and not self.completed


class Subtask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="subtasks")
    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class TaskFile(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to="task_files/")


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)


class Favorite(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="favorite")


class FavoriteItem(models.Model):
    favorite = models.ForeignKey(Favorite, on_delete=models.CASCADE, related_name="items")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="favorite_items")

    class Meta:
        unique_together = ("favorite", "task")


@receiver(post_save, sender=UserProfile)
def create_favorite(sender, instance, created, **kwargs):
    if created:
        Favorite.objects.get_or_create(user=instance)
