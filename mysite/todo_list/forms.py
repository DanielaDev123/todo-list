from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, Task, UserProfile


class RegisterForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ("username", "age", "phone_number", "avatar")


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title", "description", "priority", "deadline",
            "project", "assignee", "tags", "completed",
        ]
        widgets = {
            "deadline": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["deadline"].input_formats = ["%Y-%m-%dT%H:%M"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {"text": forms.Textarea(attrs={"rows": 3})}