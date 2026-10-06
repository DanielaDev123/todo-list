from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Category, Comment, Favorite, FavoriteItem, Project,
    Subtask, Tag, Task, TaskFile, UserProfile,
)


@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    list_display = ("username", "age", "phone_number", "status")
    search_fields = ("username", "phone_number")
    list_filter = ("status",)
    fieldsets = UserAdmin.fieldsets + (
        ("Профиль", {"fields": ("age", "phone_number", "avatar", "status")}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("category_name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ("tag_name",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("project_name", "category", "owner")
    list_filter = ("category",)


class SubtaskInline(admin.TabularInline):
    model = Subtask
    extra = 1


class TaskFileInline(admin.TabularInline):
    model = TaskFile
    extra = 1


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "priority", "completed", "deadline")
    search_fields = ("title",)
    list_filter = ("priority", "completed", "project")
    inlines = [SubtaskInline, TaskFileInline, CommentInline]


class FavoriteItemInline(admin.TabularInline):
    model = FavoriteItem
    extra = 1


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    inlines = [FavoriteItemInline]
