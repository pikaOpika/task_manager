from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q


from .models import Task, Position, Project, Team, JoinRequest
from .forms import (
    WorkerForm, WorkerUpdateForm, WorkerSearchForm,
    TaskSearchForm, TaskForm, TaskUpdateForm
)

class HomeView(generic.TemplateView):
    template_name = "task/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stats"] = (
            (get_user_model().objects.count(), "Active users"),
            (Task.objects.filter(is_completed=True).count(), "Task completed"),
            (Project.objects.count(), "Projects"),
        )
        return context


class HowItWorksView(generic.TemplateView):
    template_name = "task/how_it_works.html"

class OnboardingView(generic.TemplateView):
    template_name = "registration/onboarding.html"


class TaskListView(generic.ListView):
    model = Task
    paginate_by = 5

    def get_queryset(self):
        queryset = Task.objects.prefetch_related("assignees").all()
        req = self.request.GET
        completed = req.get("completed")
        project = req.get("project")
        if completed is not None:
            queryset = queryset.filter(is_completed=completed == "true")
        if req.get("my") and self.request.user != AnonymousUser():
            user = self.request.user
            queryset = queryset.filter(assignees=user)
        if req.get("no_projects"):
            queryset = queryset.filter(project__isnull=True)
        if project is not None:
            queryset = queryset.filter(project__name__icontains=project)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = TaskSearchForm(self.request.GET)
        return context

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
    form_class = TaskForm
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        project = self.request.GET.get("project")
        if project:
            queryset = get_user_model().objects.filter(teams__project__slug=project)
            if queryset.exists():
                form.fields["assignees"].queryset = queryset
        return form
    
    def get_success_url(self):
        slug_project = self.request.GET.get("project")
        if slug_project:
            return reverse_lazy("task:project-detail", kwargs={"slug": slug_project})
        return reverse_lazy("task:task-detail", kwargs={"slug": self.object.slug}) 

    def form_valid(self, form):
        slug_project = self.request.GET.get("project")
        if slug_project:
            project = Project.objects.get(slug=slug_project)
            members = project.teams.filter(workers=self.request.user).exists()
            
            if project.created_by == self.request.user or members:
                form.instance.project = project
            else:
                raise PermissionDenied() 
        res = super().form_valid(form)
        form.instance.assignees.add(self.request.user.id)
        return res

class PermissionCheckedTaskMixin:
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user not in obj.assignees.all():
            raise PermissionDenied
        return obj


class TaskUpdateView(LoginRequiredMixin, PermissionCheckedTaskMixin, generic.UpdateView):
    model = Task
    form_class = TaskUpdateForm
    slug_url_kwarg = "slug"
    slug_field = "slug"

    def get_success_url(self):
        return reverse_lazy("task:task-detail", kwargs={"slug": self.object.slug})

class TaskDeleteView(LoginRequiredMixin, PermissionCheckedTaskMixin, generic.DeleteView):
    model = Task
    success_url = reverse_lazy("task:task-list")
    slug_url_kwarg = "slug"
    slug_field = "slug"

class WorkerListView(generic.ListView):
    model = get_user_model()
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("tasks").select_related("position")\
        .annotate(
            completed_count=Count("tasks", filter=Q(tasks__is_completed=True)),
            uncompleted_count=Count("tasks", filter=Q(tasks__is_completed=False))
        )
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
    success_url = reverse_lazy("task:onboarding")

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
        context["join_requests"] = self.object.requests.filter(status="P")
        context["user_in_project"] = self.object.teams.filter(workers=self.request.user).exists()
        context["user_already_requested"] = self.object.requests.filter(from_user=self.request.user, status="P").exists()
        return context


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    fields = ["name", "description"]
    

    def get_success_url(self):
        return reverse_lazy("task:project-detail", kwargs={"slug": self.object.slug})

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
    fields = ["name", "workers"] 
    
    def get_success_url(self):
        slug_project = self.request.GET.get("project")
        if slug_project:
            return reverse_lazy("task:project-detail", kwargs={"slug": slug_project})
        return reverse_lazy("task:team-detail", kwargs={"slug": self.object.slug})

    def form_valid(self, form):
        slug_project = self.request.GET.get("project")
        if slug_project:
            project = Project.objects.get(slug=slug_project)
            if project.created_by == self.request.user:
                form.instance.project = project
            else:
                raise PermissionDenied()
            
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


class JoinRequestCreateView(generic.View):
    def post(self, request, *args, **kwargs):
        slug_project=self.kwargs.get("slug")
        project = Project.objects.get(slug=slug_project)
        JoinRequest.objects.get_or_create(
            project=project, from_user=self.request.user
        )

        return redirect("task:project-detail", slug=slug_project)

class JoinRequestReviewView(generic.View):
    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        join_request = JoinRequest.objects.get(pk=pk)
        if self.request.user == join_request.project.created_by:
            action = request.POST.get("action")
            if action == "approve":
                join_request.status="A"
                join_request.save()
                team_id = request.POST.get("team_id")
                team = Team.objects.get(pk=team_id)
                team.workers.add(join_request.from_user)
                return redirect("task:project-detail", slug=join_request.project.slug)
            join_request.status="R"
            join_request.save()
            return redirect("task:project-detail", slug=join_request.project.slug)
        else:
            raise PermissionDenied()
        