from django.shortcuts import render
from django.views import generic
from django.urls import reverse, reverse_lazy

from .models import Task

# Create your views here.
def index(request):
    return render(request, "task/index.html")

class TaskListView(generic.ListView):
    model = Task

    def get_queryset(self):
        queryset = Task.objects.all()
        req = self.request.GET
        completed = req.get("completed")
        if completed is not None:
            queryset = queryset.filter(is_completed=completed == "true")
        if req.get("my"):
            user = self.request.user
            queryset = queryset.filter(assignees=user)
        return queryset

class TaskDetailView(generic.DetailView):
    model = Task

class TaskCreateView(generic.CreateView):
    model = Task
    fields = ["name", "description", "deadline", "priority",
              "task_type", "assignees"]
    success_url = reverse_lazy("task:task-list")
