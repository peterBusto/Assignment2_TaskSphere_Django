from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_task, name='create-task'),
    path('', views.list_tasks, name='list-tasks'),
    path('<int:task_id>/', views.task_detail, name='task-detail'),
    path('<int:task_id>/status/', views.update_task_status, name='update-task-status'),
]
