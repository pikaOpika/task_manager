from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q


from .models import Task, Position, Project, Team
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
        if req.get("my") and self.request.user != AnonymousUser():
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
    success_url = reverse_lazy("task:task-list")

class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    fields = ["name", "description", "deadline", "is_completed", "priority", "task_type", "assignees"]
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



class ProjectListView(generic.ListView):
    model = Project
    paginate_by = 5
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.prefetch_related("tasks").all()
    
class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project
    slug_field = "slug"
    slug_url_kwarg = "slug"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["teams"] = self.object.teams.all()
        context["tasks"] = self.object.tasks.all()
        return context


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    fields = ["name", "description"]
    success_url = reverse_lazy("task:project-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    

class PermissionCheckedMixin:
    def get_object(self, queryset = None):
        obj = super().get_object(queryset)
        if obj.created_by != self.request.user:
            raise PermissionDenied
        return obj



class ProjectUpdateView(LoginRequiredMixin, PermissionCheckedMixin, generic.UpdateView):
    model = Project
    fields = ["name", "description"]
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_success_url(self):
        return reverse_lazy("task:project-detail", kwargs={"slug": self.object.slug})
    

class ProjectDeleteView(LoginRequiredMixin, PermissionCheckedMixin, generic.DeleteView):
    model = Project
    slug_url_kwarg = "slug"
    slug_field = "slug"
    success_url = reverse_lazy("task:project-list")

    

class TeamListView(generic.ListView):
    model = Team
    paginate_by = 5
    context_object_name = "teams"

    def get_queryset(self):
        return super().get_queryset().select_related("project", "created_by").prefetch_related("workers").all()
    

class TeamDetailView(generic.DetailView):
    model = Team
    slug_field = "slug"
    slug_url_kwarg = "slug"
    context_object_name = "team"

    def get_queryset(self):
        return super().get_queryset().select_related("project", "created_by").prefetch_related("workers").all()

    

class TeamCreateView(LoginRequiredMixin, generic.CreateView):
    model = Team
    fields = ["name", "workers", "project"]
    success_url = reverse_lazy("task:team-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    

class TeamUpdateView(LoginRequiredMixin, PermissionCheckedMixin, generic.UpdateView):
    model = Team
    slug_field = "slug"
    slug_url_kwarg = "slug"
    fields = ["name", "workers", "project"]

    def get_success_url(self):
        return reverse_lazy("task:team-detail", kwargs={"slug":self.object.slug})

class TeamDeleteView(LoginRequiredMixin, PermissionCheckedMixin, generic.DeleteView):
    model = Team
    slug_url_kwarg = "slug"
    slug_field = "slug"
    success_url = reverse_lazy("task:team-list")
