from django.urls import path

from .views import index, TaskListView, TaskCreateView

app_name = 'task'

urlpatterns = [
    path('', index, name='index'),
    path('tasks/', TaskListView.as_view(), name="task-list"),
    path('tasks/create/', TaskCreateView.as_view(), name="task-create"),
]
