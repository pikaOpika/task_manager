from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth import login

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
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        action = self.request.POST.get("action")
        if action == "assign":
            obj.assignees.add(self.request.user)
        else:
            obj.assignees.remove(self.request.user)
        return redirect("task:task-detail", slug=obj.slug)
    
    

class TaskCreateView(generic.CreateView):
    model = Task
    fields = ["name", "description", "deadline", "priority", "task_type", "assignees"]
    exclude = ["slug"]
    success_url = reverse_lazy("task:task-list")

class TaskUpdateView(generic.UpdateView):
    model = Task
    fields = ["name", "description", "deadline", "priority", "task_type", "assignees"]
    exclude = ["slug"]
    slug_url_kwarg = "slug"
    slug_field = "slug"

    def get_success_url(self):
        task = self.get_object()
        return reverse_lazy("task:task-detail", kwargs={"slug": task.slug})

class TaskDeleteView(generic.DeleteView):
    model = Task
    success_url = reverse_lazy("task:task-list")
    slug_url_kwarg = "slug"
    slug_field = "slug"

class WorkerListView(generic.ListView):
    model = get_user_model()

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("tasks").select_related("position")
        return queryset


class WorkerDetailView(generic.DetailView):
    model = get_user_model()
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["completed"] = self.object.tasks.filter(is_completed=True)
        context["in_progress"] = self.object.tasks.filter(is_completed=False)
        return context


class WorkerCreateView(generic.CreateView):
    model = get_user_model()
    form_class = WorkerForm
    success_url = reverse_lazy("task:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, form.instance)
        return response
    


