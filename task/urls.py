from django.urls import path

from .views import (
    index, 
    TaskListView, TaskDetailView,
    TaskUpdateView, TaskCreateView, TaskDeleteView,
    WorkerListView, WorkerDetailView, WorkerCreateView,
    WorkerUpdateView
)

app_name = 'task'

urlpatterns = [
    path('', index, name='index'),
    path('registration/', WorkerCreateView.as_view(), name="worker-create"),
    path('tasks/', TaskListView.as_view(), name="task-list"),
    path('tasks/create/', TaskCreateView.as_view(), name="task-create"),
    path('tasks/update/<slug:slug>/', TaskUpdateView.as_view(), name="task-update"),
    path('tasks/delete/<slug:slug>/', TaskDeleteView.as_view(), name="task-delete"),
    path('tasks/<slug:slug>/', TaskDetailView.as_view(), name="task-detail"),
    path('workers/', WorkerListView.as_view(), name="worker-list"),
    path('workers/<slug:slug>/', WorkerDetailView.as_view(), name="worker-detail"),
    path('workers/update/<slug:slug>/', WorkerUpdateView.as_view(), name="worker-update"),
]
