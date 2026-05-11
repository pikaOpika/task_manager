from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model

from .models import Task
from .forms import WorkerForm

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

class TaskUpdateView(generic.UpdateView):
    model = Task
    fields = "__all__"

    def get_success_url(self):
        task = self.get_object()
        return reverse_lazy("task:task-detail", args=[task.id,])

class TaskDeleteView(generic.DeleteView):
    model = Task
    success_url = reverse_lazy("task:task-list")

class WorkerListView(generic.ListView):
    model = get_user_model()

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("tasks").select_related("position")
        return queryset


class WorkerDetailView(generic.DetailView):
    model = get_user_model()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["completed"] = self.object.tasks.filter(is_completed=True)
        context["in_progress"] = self.object.tasks.filter(is_completed=False)
        return context


class WorkerCreateView(generic.CreateView):
    model = get_user_model()
    form_class = WorkerForm
    success_url = reverse_lazy("task:index")
