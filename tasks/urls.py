from django.urls import path
from tasks.views import (
    TaskListView, 
    TaskCreateView, 
    TaskRetrieveView,
    TaskUpdateView, 
    TaskDeleteView,
    TaskWebView
)

urlpatterns = [
    # List all tasks
    path('tasks/', TaskListView.as_view(), name='task-list'),
    
    # Create a new task
    path('tasks/create/', TaskCreateView.as_view(), name='task-create'),
    
    # Retrieve a specific task
    path('tasks/<int:task_id>/', TaskRetrieveView.as_view(), name='task-retrieve'),
    
    # Update a specific task
    path('tasks/<int:task_id>/update/', TaskUpdateView.as_view(), name='task-update'),
    
    # Delete a specific task
    path('tasks/<int:task_id>/delete/', TaskDeleteView.as_view(), name='task-delete'),
]