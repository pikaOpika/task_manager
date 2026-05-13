from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import Position

class WorkerForm(UserCreationForm):
    position = forms.ModelChoiceField(queryset=Position.objects.all())
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ("position", "image")