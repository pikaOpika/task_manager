from django.urls import path

from .views import (
    index, 
    TaskListView, TaskDetailView,
    TaskUpdateView, TaskCreateView, TaskDeleteView,
    WorkerListView, WorkerDetailView, WorkerCreateView
)

app_name = 'task'

urlpatterns = [
    path('', index, name='index'),
    path('registration/', WorkerCreateView.as_view(), name="worker-create"),
    path('tasks/', TaskListView.as_view(), name="task-list"),
    path('tasks/create/', TaskCreateView.as_view(), name="task-create"),
    path('tasks/update/<int:pk>/', TaskUpdateView.as_view(), name="task-update"),
    path('tasks/delete/<int:pk>/', TaskDeleteView.as_view(), name="task-delete"),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name="task-detail"),
    path('workers/', WorkerListView.as_view(), name="worker-list"),
    path('workers/<int:pk>', WorkerDetailView.as_view(), name="worker-detail")
]
