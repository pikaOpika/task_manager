from django.urls import path

from .views import index

app_name = 'task'

urlpatterns = [
    path('', index, name='index'),
]
