from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import datetime, timezone

class TaskAPITestCase(APITestCase):
    def setUp(self):
        """Setup initial test data"""
        # Create a sample task
        self.task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'due_date': '2025-12-31T23:59:59Z',
            'status': 'pending'
        }
        
        # Create initial task for testing retrieval, update, and delete
        response = self.client.post(reverse('task-create'), self.task_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.initial_task_id = response.data['id']

    def test_create_task(self):
        """Test task creation"""
        # Test successful creation
        response = self.client.post(reverse('task-create'), {
            'title': 'Another Task',
            'description': 'Another Description',
            'status': 'pending'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Another Task')
        self.assertIn('id', response.data)

        # Test creation with missing title
        response = self.client.post(reverse('task-create'), {
            'description': 'No Title'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test creation with empty title
        response = self.client.post(reverse('task-create'), {
            'title': '',
            'description': 'Empty Title'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_tasks(self):
        """Test retrieving task list"""
        # Create another task
        self.client.post(reverse('task-create'), {
            'title': 'Second Task',
            'description': 'Second Description'
        })

        # Test getting all tasks
        response = self.client.get(reverse('task-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)  # Should have at least 2 tasks

    def test_retrieve_task(self):
        """Test retrieving a single task"""
        # Test successful retrieval
        response = self.client.get(
            reverse('task-retrieve', kwargs={'task_id': self.initial_task_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Task')

        # Test retrieval of non-existent task
        response = self.client.get(
            reverse('task-retrieve', kwargs={'task_id': 99999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_task(self):
        """Test updating a task"""
        update_data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'status': 'completed'
        }

        # Test successful update
        response = self.client.put(
            reverse('task-update', kwargs={'task_id': self.initial_task_id}),
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Task')
        self.assertEqual(response.data['status'], 'completed')

        # Test update of non-existent task
        response = self.client.put(
            reverse('task-update', kwargs={'task_id': 99999}),
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test partial update
        response = self.client.put(
            reverse('task-update', kwargs={'task_id': self.initial_task_id}),
            {'status': 'pending'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'pending')

    def test_delete_task(self):
        """Test deleting a task"""
        # Test successful deletion
        response = self.client.delete(
            reverse('task-delete', kwargs={'task_id': self.initial_task_id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify task is deleted
        response = self.client.get(
            reverse('task-retrieve', kwargs={'task_id': self.initial_task_id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test deletion of non-existent task
        response = self.client.delete(
            reverse('task-delete', kwargs={'task_id': 99999})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_task_due_date(self):
        """Test task creation and update with due dates"""
        # Test creation with due date
        task_with_due_date = {
            'title': 'Task with Due Date',
            'description': 'Test due date handling',
            'due_date': '2025-12-31T23:59:59Z'
        }
        response = self.client.post(reverse('task-create'), task_with_due_date)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['due_date'])

        # Test update with new due date
        task_id = response.data['id']
        update_data = {
            'due_date': '2026-01-01T00:00:00Z'
        }
        response = self.client.put(
            reverse('task-update', kwargs={'task_id': task_id}),
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('2026-01-01', response.data['due_date'])

    def test_invalid_data_handling(self):
        """Test handling of invalid data"""
        # Test invalid date format
        response = self.client.post(reverse('task-create'), {
            'title': 'Invalid Date',
            'due_date': 'not-a-date'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid status
        response = self.client.post(reverse('task-create'), {
            'title': 'Invalid Status',
            'status': 'invalid-status'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test each valid status
        valid_statuses = ['pending', 'in_progress', 'completed']
        for valid_status in valid_statuses:
            response = self.client.post(reverse('task-create'), {
                'title': f'Task with {valid_status} status',
                'status': valid_status
            })
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['status'], valid_status)

    def test_task_list_ordering(self):
        """Test that tasks are returned in the correct order"""
        # Create tasks with different due dates
        self.client.post(reverse('task-create'), {
            'title': 'Future Task',
            'due_date': '2026-01-01T00:00:00Z'
        })
        self.client.post(reverse('task-create'), {
            'title': 'Past Task',
            'due_date': '2025-01-01T00:00:00Z'
        })

        # Get all tasks
        response = self.client.get(reverse('task-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if tasks with due dates come first and are ordered by due date
        tasks_with_due_dates = [
            task for task in response.data 
            if task['due_date'] is not None
        ]
        if len(tasks_with_due_dates) >= 2:
            for i in range(len(tasks_with_due_dates) - 1):
                current_due_date = datetime.fromisoformat(
                    tasks_with_due_dates[i]['due_date'].replace('Z', '+00:00')
                )
                next_due_date = datetime.fromisoformat(
                    tasks_with_due_dates[i + 1]['due_date'].replace('Z', '+00:00')
                )
                self.assertLessEqual(current_due_date, next_due_date)
