from datetime import datetime
import traceback
from django.http import Http404
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.serializers import Serializer, CharField, DateTimeField, IntegerField

from tasks.tasks import TaskManager
from tasks.task_dto import TaskDTO
from tasks.logger import logger

class TaskBaseSerializer(Serializer):
    """Base Serializer for Task DTOs with common fields"""
    VALID_STATUSES = ['pending', 'in_progress', 'completed']

    id = IntegerField(read_only=True)
    title = CharField(max_length=255, required=True)
    description = CharField(allow_null=True, required=False)
    due_date = DateTimeField(allow_null=True, required=False)
    status = CharField(default="pending")
    created_at = DateTimeField(read_only=True)
    update_task = DateTimeField(read_only=True)

    def validate_status(self, value):
        """Validate the status field"""
        if value and value.lower() not in self.VALID_STATUSES:
            raise serializers.ValidationError(
                f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}"
            )
        return value.lower() if value else 'pending'

class TaskCreateSerializer(TaskBaseSerializer):
    """Serializer for creating tasks"""
    def create(self, validated_data):
        pass

class TaskUpdateSerializer(TaskBaseSerializer):
    """Serializer for updating tasks"""
    title = CharField(max_length=255, required=False)
    
    def update(self, instance, validated_data):
        pass

class TaskListView(APIView):
    """API View for listing all tasks"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_manager = TaskManager()

    def get(self, request):
        """
        Get all tasks
        GET /api/tasks/
        """
        logger.debug("API request: GET /api/tasks/")
        try:
            tasks = self.task_manager.get_all_tasks()
            serializer = TaskBaseSerializer(tasks, many=True)
            logger.info(f"Successfully retrieved {len(tasks)} tasks")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving tasks: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TaskCreateView(APIView):
    """API View for creating new tasks"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_manager = TaskManager()

    def post(self, request):
        """
        Create a new task
        POST /api/tasks/create/
        """
        logger.debug(f"API request: POST /api/tasks/create/ with data: {request.data}")
        serializer = TaskCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            logger.warning(f"Invalid request data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Convert string date to datetime if provided
            due_date = None
            if serializer.validated_data.get('due_date'):
                due_date = datetime.fromisoformat(
                    str(serializer.validated_data['due_date']).replace('Z', '+00:00')
                )
                logger.debug(f"Parsed due_date: {due_date}")

            task_id = self.task_manager.create_task(
                title=serializer.validated_data['title'],
                description=serializer.validated_data.get('description'),
                due_date=due_date,
                status=serializer.validated_data.get('status', 'pending')
            )
            
            # Fetch the created task to return complete data
            created_task = self.task_manager.get_task(task_id)
            response_serializer = TaskCreateSerializer(created_task)
            logger.info(f"Successfully created task {task_id}")
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            logger.warning(f"Validation error creating task: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TaskRetrieveView(APIView):
    """API View for retrieving individual tasks"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_manager = TaskManager()

    def get_task(self, task_id: int) -> TaskDTO:
        """Helper method to get task or raise 404"""
        try:
            task = self.task_manager.get_task(task_id)
            if task is None:
                raise Http404("Task not found")
            return task
        except ValueError as e:
            raise Http404(str(e))

    def get(self, request, task_id):
        """
        Get a specific task
        GET /api/tasks/{task_id}/
        """
        logger.debug(f"API request: GET /api/tasks/{task_id}/")
        try:
            task = self.get_task(task_id)
            serializer = TaskBaseSerializer(task)
            logger.info(f"Successfully retrieved task {task_id}")
            return Response(serializer.data)
        except Http404 as e:
            logger.warning(f"Task not found: {task_id}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving task {task_id}: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TaskUpdateView(APIView):
    """API View for updating tasks"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_manager = TaskManager()

    def get_task(self, task_id: int) -> TaskDTO:
        """Helper method to get task or raise 404"""
        try:
            task = self.task_manager.get_task(task_id)
            if task is None:
                raise Http404("Task not found")
            return task
        except (ValueError, Exception) as e:
            raise Http404(str(e))

    def put(self, request, task_id):
        """
        Update a specific task
        PUT /api/tasks/{task_id}/update/
        """
        logger.debug(f"API request: PUT /api/tasks/{task_id}/update/ with data: {request.data}")
        try:
            # Check if task exists and get its data
            task = self.get_task(task_id)
            
            # Initialize serializer with the existing task data and update data
            serializer = TaskUpdateSerializer(task, data=request.data, partial=True)
            if not serializer.is_valid():
                logger.warning(f"Invalid request data: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Convert string date to datetime if provided
            due_date = None
            if serializer.validated_data.get('due_date'):
                due_date = datetime.fromisoformat(
                    str(serializer.validated_data['due_date']).replace('Z', '+00:00')
                )
                logger.debug(f"Parsed due_date: {due_date}")

            success = self.task_manager.update_task(
                task_id=task_id,
                title=serializer.validated_data.get('title'),
                description=serializer.validated_data.get('description'),
                due_date=due_date,
                status=serializer.validated_data.get('status')
            )
            
            if success:
                updated_task = self.task_manager.get_task(task_id)
                response_serializer = TaskUpdateSerializer(updated_task)
                logger.info(f"Successfully updated task {task_id}")
                return Response(response_serializer.data)
            
            logger.warning(f"Task not found during update: {task_id}")
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Http404 as e:
            logger.warning(f"Task not found: {task_id}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        except ValueError as e:
            logger.warning(f"Validation error updating task {task_id}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TaskWebView(TemplateView):
    """Frontend view for displaying tasks"""
    template_name = "tasks/task_list.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_manager = TaskManager()
        try:
            tasks = task_manager.get_all_tasks()
            context['tasks'] = tasks
        except Exception as e:
            logger.error(f"Error retrieving tasks for web view: {str(e)}")
            context['tasks'] = []
            context['error'] = "Error loading tasks. Please try again later."
        return context


class TaskDeleteView(APIView):
    """API View for deleting tasks"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_manager = TaskManager()

    def get_task(self, task_id: int) -> TaskDTO:
        """Helper method to get task or raise 404"""
        try:
            task = self.task_manager.get_task(task_id)
            if task is None:
                raise Http404("Task not found")
            return task
        except ValueError as e:
            raise Http404(str(e))

    def delete(self, request, task_id):
        """
        Delete a specific task
        DELETE /api/tasks/{task_id}/delete/
        """
        logger.debug(f"API request: DELETE /api/tasks/{task_id}/delete/")
        try:
            # Check if task exists
            self.get_task(task_id)
            
            success = self.task_manager.delete_task(task_id)
            if success:
                logger.info(f"Successfully deleted task {task_id}")
                return Response(status=status.HTTP_204_NO_CONTENT)
            
            logger.warning(f"Task not found during deletion: {task_id}")
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Http404 as e:
            logger.warning(f"Task not found: {task_id}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
