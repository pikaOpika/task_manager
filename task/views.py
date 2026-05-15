from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q

from .models import Task, Position
from .forms import WorkerForm, WorkerUpdateForm, WorkerSearchForm

# Create your views here.
def index(request):
    context = {
        "stats": [
            ("12k+", "Active users"),
            ("340k", "Tasks completed"),
            ("98%", "Satisfaction"),
        ]
    }
    return render(request, "task/index.html", context=context)

class TaskListView(generic.ListView):
    model = Task
    paginate_by = 5

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

class TaskDetailView(LoginRequiredMixin, generic.DetailView):
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
    
    

class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    fields = ["name", "description", "deadline", "priority", "task_type", "assignees"]
    exclude = ["slug"]
    success_url = reverse_lazy("task:task-list")

class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    fields = ["name", "description", "deadline", "is_completed", "priority", "task_type", "assignees"]
    exclude = ["slug"]
    slug_url_kwarg = "slug"
    slug_field = "slug"

    def get_success_url(self):
        return reverse_lazy("task:task-detail", kwargs={"slug": self.object.slug})

class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    success_url = reverse_lazy("task:task-list")
    slug_url_kwarg = "slug"
    slug_field = "slug"

class WorkerListView(generic.ListView):
    model = get_user_model()
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("tasks").select_related("position")\
        .annotate(completed_count=Count("tasks", filter=Q(tasks__is_completed=True)))
        req = self.request.GET
        username = req.get("username")
        position = req.get("position")
        if username:
            queryset = queryset.filter(username__icontains=username)
        if position:
            queryset = queryset.filter(position__name__icontains=position)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = WorkerSearchForm(self.request.GET)
        context["position_list"] = Position.objects.all()
        return context


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
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
    

class WorkerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = get_user_model()
    form_class = WorkerUpdateForm

    def get_object(self, queryset = None):
        obj = super().get_object(queryset)
        if obj != self.request.user:
            raise PermissionDenied
        return obj
    
    def get_success_url(self):
        return reverse_lazy("task:worker-detail", kwargs={"slug": self.object.slug})
