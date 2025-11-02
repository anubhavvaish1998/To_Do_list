from datetime import datetime
from typing import List, Optional
import traceback

from tasks.db_utils import TaskDatabase
from tasks.task_dto import TaskDTO
from tasks.logger import logger

class TaskManager:
    """Manager class for handling all task-related operations"""

    def __init__(self):
        """Initialize TaskManager with a database connection"""
        self._db = TaskDatabase()

    def create_task(self, title: str, description: Optional[str] = None, 
                   due_date: Optional[datetime] = None, status: str = "pending") -> int:
        """
        Create a new task
        Args:
            title: Title of the task
            description: Optional description of the task
            due_date: Optional due date for the task
            status: Status of the task (default: pending)
        Returns:
            int: ID of the newly created task
        Raises:
            ValueError: If title is empty or status is invalid
        """
        logger.debug(f"Creating task with title: {title}")
        try:
            if not title.strip():
                logger.error("Attempted to create task with empty title")
                raise ValueError("Task title cannot be empty")

            task = TaskDTO(
                title=title,
                description=description,
                due_date=due_date,
                status=status.lower()
            )
            task_id = self._db.create_task(task)
            logger.info(f"Created task {task_id}: {title}")
            return task_id
        except ValueError as e:
            # Re-raise ValueError as it's an expected validation error
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating task: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise

    def get_all_tasks(self) -> List[TaskDTO]:
        """
        Retrieve all tasks
        Returns:
            List[TaskDTO]: List of all tasks
        """
        logger.debug("Retrieving all tasks")
        try:
            tasks = self._db.get_all_tasks()
            logger.info(f"Retrieved {len(tasks)} tasks")
            return tasks
        except Exception as e:
            logger.error(f"Error retrieving tasks: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise

    def get_task(self, task_id: int) -> Optional[TaskDTO]:
        """
        Retrieve a specific task by ID
        Args:
            task_id: ID of the task to retrieve
        Returns:
            Optional[TaskDTO]: Task if found, None otherwise
        Raises:
            ValueError: If task_id is less than 1
        """
        logger.debug(f"Retrieving task {task_id}")
        try:
            if task_id < 1:
                logger.error(f"Invalid task ID: {task_id}")
                raise ValueError("Task ID must be a positive integer")
            
            task = self._db.get_task(task_id)
            if task:
                logger.info(f"Retrieved task {task_id}: {task.title}")
            else:
                logger.info(f"Task {task_id} not found")
            return task
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving task {task_id}: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise

    def update_task(self, task_id: int, title: Optional[str] = None,
                   description: Optional[str] = None, due_date: Optional[datetime] = None,
                   status: Optional[str] = None) -> bool:
        """
        Update an existing task
        Args:
            task_id: ID of the task to update
            title: New title of the task (if None, keeps existing)
            description: New description of the task (if None, keeps existing)
            due_date: New due date for the task (if None, keeps existing)
            status: New status of the task (if None, keeps existing)
        Returns:
            bool: True if update successful, False if task not found
        Raises:
            ValueError: If task_id is less than 1 or if title is empty when provided
        """
        logger.debug(f"Updating task {task_id}")
        try:
            if task_id < 1:
                logger.error(f"Invalid task ID for update: {task_id}")
                raise ValueError("Task ID must be a positive integer")

            # Get existing task
            existing_task = self._db.get_task(task_id)
            if not existing_task:
                logger.warning(f"Task {task_id} not found for update")
                return False

            # Update task fields if new values are provided
            logger.debug(f"Current task state: {existing_task}")
            if title is not None:
                if not title.strip():
                    logger.error("Attempted to update task with empty title")
                    raise ValueError("Task title cannot be empty")
                existing_task.title = title
            if description is not None:
                existing_task.description = description
            if due_date is not None:
                existing_task.due_date = due_date
            if status is not None:
                existing_task.status = status.lower()
            
            logger.debug(f"Updated task state: {existing_task}")
            success = self._db.update_task(existing_task)
            if success:
                logger.info(f"Successfully updated task {task_id}")
            return success
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task
        Args:
            task_id: ID of the task to delete
        Returns:
            bool: True if deletion successful, False if task not found
        Raises:
            ValueError: If task_id is less than 1
        """
        logger.debug(f"Deleting task {task_id}")
        try:
            if task_id < 1:
                logger.error(f"Invalid task ID for deletion: {task_id}")
                raise ValueError("Task ID must be a positive integer")

            success = self._db.delete_task(task_id)
            if success:
                logger.info(f"Successfully deleted task {task_id}")
            else:
                logger.warning(f"Task {task_id} not found for deletion")
            return success
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise

    def mark_completed(self, task_id: int) -> bool:
        """
        Mark a task as completed
        Args:
            task_id: ID of the task to mark as completed
        Returns:
            bool: True if update successful, False if task not found
        Raises:
            ValueError: If task_id is less than 1
        """
        logger.debug(f"Marking task {task_id} as completed")
        try:
            success = self.update_task(task_id, status="completed")
            if success:
                logger.info(f"Successfully marked task {task_id} as completed")
            return success
        except Exception as e:
            logger.error(f"Error marking task {task_id} as completed: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise

    def mark_pending(self, task_id: int) -> bool:
        """
        Mark a task as pending
        Args:
            task_id: ID of the task to mark as pending
        Returns:
            bool: True if update successful, False if task not found
        Raises:
            ValueError: If task_id is less than 1
        """
        logger.debug(f"Marking task {task_id} as pending")
        try:
            success = self.update_task(task_id, status="pending")
            if success:
                logger.info(f"Successfully marked task {task_id} as pending")
            return success
        except Exception as e:
            logger.error(f"Error marking task {task_id} as pending: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise
