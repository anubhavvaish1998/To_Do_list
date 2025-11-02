# To-Do List API Documentation

A RESTful API for managing tasks with support for CRUD operations, due dates, and task status management.

## Project Structure
```
To-Do-list/
├── app/                      # Main application directory
├── tasks/                    # Tasks application
│   ├── migrations/          # Database migrations
│   ├── templates/           # HTML templates
│   │   └── tasks/          
│   │       └── task_list.html  # Main task interface
│   ├── admin.py            # Admin configuration
│   ├── apps.py            # App configuration
│   ├── db_init.py         # Database initialization
│   ├── db_utils.py        # Database utilities
│   ├── logger.py          # Logging configuration
│   ├── models.py          # Database models
│   ├── task_dto.py        # Data transfer objects
│   ├── tasks.py           # Task business logic
│   ├── tests.py           # Unit tests
│   ├── urls.py            # URL routing
│   └── views.py           # View controllers
├── To_Do_List/             # Project configuration
│   ├── settings.py        # Project settings
│   ├── urls.py           # Main URL routing
│   ├── asgi.py          # ASGI configuration
│   └── wsgi.py          # WSGI configuration
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── .env                  # Environment variables

## Database Schema

### Task Table
| Column      | Type           | Description                                    |
|-------------|---------------|------------------------------------------------|
| id          | Integer       | Primary key                                    |
| title       | String        | Task title (required)                          |
| description | Text          | Task description (optional)                    |
| due_date    | DateTime      | Task due date with timezone (optional)        |
| status      | String        | Task status (pending/in_progress/completed)    |
| created_at  | DateTime      | Creation timestamp with timezone              |
| update_task | DateTime      | Last update timestamp with timezone           |

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 13 or higher
- pip (Python package installer)

### Environment Setup

Create a `.env` file in the root directory with the following configurations:

```env
# Database Configuration
POSTGRES_DB=TODODB
POSTGRES_USER=postgres
POSTGRES_PASSWORD=123456
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Django Configuration
DJANGO_SECRET_KEY=django-insecure-change-this-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*

# Other Configs
PYTHONUNBUFFERED=1  
PYTHONDONTWRITEBYTECODE=1
```

### Environment Variables Description
| Variable | Description | Default Value |
|----------|-------------|---------------|
| POSTGRES_DB | PostgreSQL database name | TODODB |
| POSTGRES_USER | Database user | postgres |
| POSTGRES_PASSWORD | Database password | 123456 |
| POSTGRES_HOST | Database host | localhost |
| POSTGRES_PORT | Database port | 5432 |
| DJANGO_SECRET_KEY | Django secret key | django-insecure-change-this-key |
| DJANGO_DEBUG | Debug mode (True/False) | True |
| DJANGO_ALLOWED_HOSTS | Allowed hosts | * |
| PYTHONUNBUFFERED | Python output buffering | 1 |
| PYTHONDONTWRITEBYTECODE | Prevent Python from writing bytecode | 1 |

### Installation Steps
1. Clone the repository
   ```bash
   git clone https://github.com/anubhavvaish1998/To-Do-list.git
   cd To-Do-list
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Unix or MacOS
   source venv/bin/activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file with above configurations

5. Create PostgreSQL database
   ```bash
   psql -U postgres
   CREATE DATABASE tododb;
   ```

6. Start development server
   ```bash
   python manage.py runserver
   ```
   
The application will be available at `http://localhost:8000`

## Base URL

```
http://localhost:8000/api
```

## API Endpoints

### 1. List All Tasks

Retrieves a list of all tasks, ordered by due date.

- **URL**: `/tasks/`
- **Method**: `GET`
- **Success Response**:
  - **Code**: 200 OK
  ```json
  [
    {
      "id": 1,
      "title": "Complete Project",
      "description": "Finish the documentation",
      "due_date": "2025-12-31T23:59:59Z",
      "status": "pending",
      "created_at": "2025-11-01T15:30:00+05:30",
      "update_task": "2025-11-01T15:30:00+05:30"
    }
  ]
  ```

### 2. Create Task

Creates a new task.

- **URL**: `/tasks/create/`
- **Method**: `POST`
- **Data Params**:
  ```json
  {
    "title": "Complete Project",
    "description": "Finish the documentation",
    "due_date": "2025-12-31T23:59:59Z",
    "status": "pending"
  }
  ```
  - `title` (required): String
  - `description` (optional): String
  - `due_date` (optional): ISO 8601 datetime string
  - `status` (optional): One of ["pending", "in_progress", "completed"]

- **Success Response**:
  - **Code**: 201 Created
  ```json
  {
    "id": 1,
    "title": "Complete Project",
    "description": "Finish the documentation",
    "due_date": "2025-12-31T23:59:59Z",
    "status": "pending",
    "created_at": "2025-11-01T15:30:00+05:30",
    "update_task": "2025-11-01T15:30:00+05:30"
  }
  ```

- **Error Responses**:
  - **Code**: 400 Bad Request
  ```json
  {
    "error": "Title cannot be empty"
  }
  ```

### 3. Get Task

Retrieves a specific task by ID.

- **URL**: `/tasks/{task_id}/`
- **Method**: `GET`
- **URL Params**: 
  - `task_id`: Integer

- **Success Response**:
  - **Code**: 200 OK
  ```json
  {
    "id": 1,
    "title": "Complete Project",
    "description": "Finish the documentation",
    "due_date": "2025-12-31T23:59:59Z",
    "status": "pending",
    "created_at": "2025-11-01T15:30:00+05:30",
    "update_task": "2025-11-01T15:30:00+05:30"
  }
  ```

- **Error Response**:
  - **Code**: 404 Not Found
  ```json
  {
    "error": "Task not found"
  }
  ```

### 4. Update Task

Updates an existing task.

- **URL**: `/tasks/{task_id}/update/`
- **Method**: `PUT`
- **URL Params**: 
  - `task_id`: Integer
- **Data Params**:
  ```json
  {
    "title": "Updated Project",
    "description": "Updated description",
    "due_date": "2026-01-01T00:00:00Z",
    "status": "completed"
  }
  ```
  All fields are optional. Only provided fields will be updated.

- **Success Response**:
  - **Code**: 200 OK
  ```json
  {
    "id": 1,
    "title": "Updated Project",
    "description": "Updated description",
    "due_date": "2026-01-01T00:00:00Z",
    "status": "completed",
    "created_at": "2025-11-01T15:30:00+05:30",
    "update_task": "2025-11-01T15:40:00+05:30"
  }
  ```

- **Error Responses**:
  - **Code**: 404 Not Found
  ```json
  {
    "error": "Task not found"
  }
  ```
  - **Code**: 400 Bad Request
  ```json
  {
    "error": "Title cannot be empty if provided"
  }
  ```

### 5. Delete Task

Deletes a specific task.

- **URL**: `/tasks/{task_id}/delete/`
- **Method**: `DELETE`
- **URL Params**: 
  - `task_id`: Integer

- **Success Response**:
  - **Code**: 204 No Content

- **Error Response**:
  - **Code**: 404 Not Found
  ```json
  {
    "error": "Task not found"
  }
  ```

## Status Values

Tasks can have one of the following status values:
- `pending`: Task is yet to be started
- `in_progress`: Task is currently being worked on
- `completed`: Task is finished

## Date Formats

- All dates should be provided in ISO 8601 format
- Timezone information is preserved
- Example: `2025-12-31T23:59:59Z` or `2025-12-31T23:59:59+05:30`

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `200`: Success
- `201`: Successfully created
- `204`: Successfully deleted
- `400`: Bad request (invalid input)
- `404`: Resource not found
- `500`: Internal server error

Error responses include a message explaining the error:
```json
{
  "error": "Description of what went wrong"
}
```

## Automated Functions

### Task Management Functions
| Function Name | Description | Location |
|--------------|-------------|-----------|
| `createNewTask()` | Creates a new task with title, description, and due date | `task_list.html` |
| `updateTaskStatus()` | Updates the status of a task | `task_list.html` |
| `deleteTask()` | Deletes a task with confirmation | `task_list.html` |
| `makeEditable()` | Makes a task field editable on double-click | `task_list.html` |
| `saveChanges()` | Saves changes to task fields | `task_list.html` |
| `cancelEdit()` | Cancels editing of task fields | `task_list.html` |
| `formatDate()` | Formats dates for display | `task_list.html` |
| `showMessage()` | Shows success/error messages | `task_list.html` |

### Backend Functions
| Function Name | Description | Location |
|--------------|-------------|-----------|
| `get_task_list()` | Retrieves all tasks | `views.py` |
| `create_task()` | Creates a new task | `views.py` |
| `update_task()` | Updates task details | `views.py` |
| `delete_task()` | Deletes a task | `views.py` |
| `get_task_by_id()` | Retrieves a specific task | `db_utils.py` |
| `validate_task_data()` | Validates task input data | `task_dto.py` |

### Utility Functions
| Function Name | Description | Location |
|--------------|-------------|-----------|
| `setup_logger()` | Configures application logging | `logger.py` |
| `initialize_db()` | Initializes database with default data | `db_init.py` |
| `format_datetime()` | Formats datetime with timezone | `utils.py` |

## Example Usage

### Creating a Task

```bash
curl -X POST http://localhost:8000/api/tasks/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Important Meeting",
    "description": "Team sync-up",
    "due_date": "2025-12-31T15:00:00+05:30",
    "status": "pending"
  }'
```

### Updating a Task Status

```bash
curl -X PUT http://localhost:8000/api/tasks/1/update/ \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

### Retrieving All Tasks

```bash
curl http://localhost:8000/api/tasks/
```

### Deleting a Task

```bash
curl -X DELETE http://localhost:8000/api/tasks/1/delete/
```

## Technical Details

- All timestamps are stored in the database with timezone information
- Tasks are automatically ordered by due date (tasks with due dates come first)
- The API uses proper HTTP status codes and content negotiation
- All responses are in JSON format
- The API includes comprehensive error handling and validation