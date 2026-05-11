from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Position

class WorkerForm(UserCreationForm):
    position = forms.ModelChoiceField(queryset=Position.objects.all())