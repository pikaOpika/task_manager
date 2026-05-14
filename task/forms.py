from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import Position

class WorkerForm(UserCreationForm):
    position = forms.ModelChoiceField(queryset=Position.objects.all())
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ("position", "image")

class WorkerUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "position", "image"]

class WorkerSearchForm(forms.Form):
    username = forms.CharField(required=False, max_length=100, label="")
