from django.shortcuts import render, redirect
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

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        action = self.request.POST.get("action")
        if action == "assign":
            obj.assignees.add(self.request.user)
        else:
            obj.assignees.remove(self.request.user)
        return redirect("task:task-detail", pk=obj.id)

class TaskCreateView(generic.CreateView):
    model = Task
    fields = "__all__"
    success_url = reverse_lazy("task:task-list")
