from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, RegisterForm, TaskForm
from .models import Comment, Favorite, FavoriteItem, Task


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("task_list")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def task_list(request):
    tasks = Task.objects.select_related("project", "assignee").prefetch_related("tags")
    return render(request, "tasks/task_list.html", {"tasks": tasks})


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    favorite, _ = Favorite.objects.get_or_create(user=request.user)
    return render(request, "tasks/task_detail.html", {
        "task": task,
        "comment_form": CommentForm(),
        "is_favorite": favorite.items.filter(task=task).exists(),
    })


@login_required
def task_create(request):
    form = TaskForm(request.POST or None)
    if form.is_valid():
        task = form.save()
        return redirect("task_detail", pk=task.pk)
    return render(request, "tasks/task_form.html", {"form": form, "title": "Новая задача"})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    form = TaskForm(request.POST or None, instance=task)
    if form.is_valid():
        form.save()
        return redirect("task_detail", pk=task.pk)
    return render(request, "tasks/task_form.html", {"form": form, "title": "Редактировать задачу"})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        task.delete()
        return redirect("task_list")
    return render(request, "tasks/confirm_delete.html", {"object": task})


@login_required
def comment_create(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
    return redirect("task_detail", pk=task.pk)


@login_required
def comment_update(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user != request.user:
        raise PermissionDenied
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect("task_detail", pk=comment.task.pk)
    return render(request, "tasks/task_form.html", {"form": form, "title": "Редактировать комментарий"})


@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user != request.user:
        raise PermissionDenied
    task_pk = comment.task.pk
    if request.method == "POST":
        comment.delete()
        return redirect("task_detail", pk=task_pk)
    return render(request, "tasks/confirm_delete.html", {"object": comment})


@login_required
def favorite_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        favorite, _ = Favorite.objects.get_or_create(user=request.user)
        item = FavoriteItem.objects.filter(favorite=favorite, task=task)
        if item.exists():
            item.delete()
        else:
            FavoriteItem.objects.create(favorite=favorite, task=task)
    return redirect("task_detail", pk=task.pk)
