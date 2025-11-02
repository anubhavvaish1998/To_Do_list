# tasks/db_utils.py
from django.db import connection
from datetime import datetime
from typing import List, Optional
import traceback

from tasks.task_dto import TaskDTO
from tasks.db_init import setup_database
from tasks.logger import logger

class TaskDatabase:
    """Database utility class for managing tasks using PostgreSQL functions"""

    def __init__(self):
        """Initialize the TaskDatabase class"""
        setup_database()

    def create_task(self, task: TaskDTO) -> int:
        """
        Create a new task in the database
        Args:
            task: TaskDTO object containing task details
        Returns:
            int: ID of the newly created task
        """
        logger.debug(f"Creating new task: {task}")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT create_new_task(%s, %s, %s, %s);",
                    [task.title, task.description, task.due_date, task.status]
                )
                task_id = cursor.fetchone()[0]
                logger.info(f"Successfully created task with ID: {task_id}")
                return task_id
        except Exception as e:
            logger.error(f"Failed to create task: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise

    def get_all_tasks(self) -> List[TaskDTO]:
        """
        Retrieve all tasks from the database
        Returns:
            List[TaskDTO]: List of all tasks
        """
        logger.debug("Retrieving all tasks")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM get_all_tasks();")
                tasks = [
                    TaskDTO(
                        id=row[0],
                        title=row[1],
                        description=row[2],
                        due_date=row[3],
                        status=row[4],
                        created_at=row[5],
                        update_task=row[6]
                    ) for row in cursor.fetchall()
                ]
                logger.info(f"Retrieved {len(tasks)} tasks")
                return tasks
        except Exception as e:
            logger.error(f"Failed to retrieve tasks: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise

    def get_task(self, task_id: int) -> Optional[TaskDTO]:
        """
        Retrieve a specific task by ID
        Args:
            task_id: ID of the task to retrieve
        Returns:
            Optional[TaskDTO]: Task if found, None otherwise
        """
        logger.debug(f"Retrieving task with ID: {task_id}")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM get_task_by_id(%s);", [task_id])
                row = cursor.fetchone()
                if row:
                    task = TaskDTO(
                        id=row[0],
                        title=row[1],
                        description=row[2],
                        due_date=row[3],
                        status=row[4],
                        created_at=row[5],
                        update_task=row[6]
                    )
                    logger.info(f"Retrieved task {task_id}: {task.title}")
                    return task
                logger.info(f"Task {task_id} not found")
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve task {task_id}: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise

    def update_task(self, task: TaskDTO) -> bool:
        """
        Update an existing task
        Args:
            task: TaskDTO object containing updated task details
        Returns:
            bool: True if update successful, False otherwise
        """
        logger.debug(f"Updating task {task.id}: {task}")
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT update_task_by_id(%s, %s, %s, %s, %s);",
                    [task.id, task.title, task.description, task.due_date, task.status]
                )
                success = cursor.fetchone()[0]
                if success:
                    logger.info(f"Successfully updated task {task.id}")
                else:
                    logger.warning(f"Task {task.id} not found for update")
                return success
        except Exception as e:
            logger.error(f"Failed to update task {task.id}: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID
        Args:
            task_id: ID of the task to delete
        Returns:
            bool: True if deletion successful, False otherwise
        """
        logger.debug(f"Deleting task {task_id}")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT delete_task_by_id(%s);", [task_id])
                success = cursor.fetchone()[0]
                if success:
                    logger.info(f"Successfully deleted task {task_id}")
                else:
                    logger.warning(f"Task {task_id} not found for deletion")
                return success
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {str(e)}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
            raise
