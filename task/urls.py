from django.urls import path

from .views import (
    HomeView, HowItWorksView,
    TaskListView, TaskDetailView,
    TaskCreateView, TaskUpdateView, TaskDeleteView,
    WorkerListView, WorkerDetailView, 
    WorkerCreateView, WorkerUpdateView,
    TeamListView, TeamDetailView,
    TeamCreateView, TeamUpdateView, TeamDeleteView,
    ProjectListView, ProjectDetailView,
    ProjectCreateView, ProjectUpdateView, ProjectDeleteView
)

app_name = 'task'

urlpatterns = [
    # Home page
    path('', HomeView.as_view(), name='index'),
    path('how-it-works/', HowItWorksView.as_view(), name='how-it-works'),
    # Registration for workers
    path('registration/', WorkerCreateView.as_view(), name="worker-create"),
    # Tasks
    path('tasks/', TaskListView.as_view(), name="task-list"),
    path('tasks/create/', TaskCreateView.as_view(), name="task-create"),
    path('tasks/update/<slug:slug>/', TaskUpdateView.as_view(), name="task-update"),
    path('tasks/delete/<slug:slug>/', TaskDeleteView.as_view(), name="task-delete"),
    path('tasks/<slug:slug>/', TaskDetailView.as_view(), name="task-detail"),
    # Workers
    path('workers/', WorkerListView.as_view(), name="worker-list"),
    path('workers/update/<slug:slug>/', WorkerUpdateView.as_view(), name="worker-update"),
    path('workers/<slug:slug>/', WorkerDetailView.as_view(), name="worker-detail"),
    # Teams
    path('teams/', TeamListView.as_view(), name="team-list"),
    path('teams/create/', TeamCreateView.as_view(), name="team-create"),
    path('teams/update/<slug:slug>/', TeamUpdateView.as_view(), name="team-update"),
    path('teams/delete/<slug:slug>/', TeamDeleteView.as_view(), name="team-delete"),
    path('teams/<slug:slug>/', TeamDetailView.as_view(), name="team-detail"),
    # Projects
    path('projects/', ProjectListView.as_view(), name="project-list"),
    path('projects/create/', ProjectCreateView.as_view(), name="project-create"),
    path('projects/update/<slug:slug>/', ProjectUpdateView.as_view(), name="project-update"),
    path('projects/delete/<slug:slug>/', ProjectDeleteView.as_view(), name="project-delete"),
    path('projects/<slug:slug>/', ProjectDetailView.as_view(), name="project-detail"),
]
