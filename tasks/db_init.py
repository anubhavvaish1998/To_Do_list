# tasks/db_init.py
from django.db import connection

def initialize_database_functions():
    """Initialize all PostgreSQL functions required for the task management system"""
    with connection.cursor() as cursor:
        # Function to ensure tasks table exists
        cursor.execute("""
            CREATE OR REPLACE FUNCTION ensure_tasks_table()
            RETURNS void AS $$
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'tasks') THEN
                    CREATE TABLE tasks (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        description TEXT,
                        due_date TIMESTAMP WITH TIME ZONE NULL,
                        status VARCHAR(50) NOT NULL DEFAULT 'pending',
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata'),
                        update_task TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')
                    );

                    CREATE INDEX idx_tasks_status ON tasks(status);
                    CREATE INDEX idx_tasks_due_date ON tasks(due_date);
                END IF;
            END;
            $$ LANGUAGE plpgsql;
        """)

        # Function to create a new task
        cursor.execute("""
            CREATE OR REPLACE FUNCTION create_new_task(
                p_title VARCHAR(255),
                p_description TEXT,
                p_due_date TIMESTAMP WITH TIME ZONE,
                p_status VARCHAR(50)
            )
            RETURNS INTEGER AS $$
            DECLARE
                new_task_id INTEGER;
            BEGIN
                IF p_title IS NULL OR trim(p_title) = '' THEN
                    RAISE EXCEPTION 'Title cannot be empty';
                END IF;

                IF p_status IS NULL OR trim(p_status) = '' THEN
                    p_status := 'pending';
                END IF;

                INSERT INTO tasks (title, description, due_date, status)
                VALUES (
                    trim(p_title),
                    CASE WHEN p_description IS NULL OR trim(p_description) = '' THEN NULL ELSE trim(p_description) END,
                    p_due_date,
                    lower(trim(p_status))
                )
                RETURNING id INTO new_task_id;

                RETURN new_task_id;
            END;
            $$ LANGUAGE plpgsql;
        """)

        # ✅ Fixed Function: get_all_tasks
        cursor.execute("""
            CREATE OR REPLACE FUNCTION get_all_tasks()
            RETURNS TABLE (
                id INTEGER,
                title VARCHAR(255),
                description TEXT,
                due_date TIMESTAMP WITH TIME ZONE,
                status VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE,
                update_task TIMESTAMP WITH TIME ZONE
            ) AS $$
            BEGIN
                RETURN QUERY 
                SELECT 
                    t.id,
                    t.title,
                    t.description,
                    t.due_date,
                    t.status,
                    (t.created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') AS created_at,
                    (t.update_task AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') AS update_task
                FROM tasks t 
                ORDER BY 
                    CASE WHEN t.due_date IS NOT NULL THEN 0 ELSE 1 END,
                    t.due_date ASC,
                    t.created_at DESC;
            END;
            $$ LANGUAGE plpgsql;
        """)

        # Function to get a task by ID
        cursor.execute("""
            CREATE OR REPLACE FUNCTION get_task_by_id(p_id INTEGER)
            RETURNS TABLE (
                id INTEGER,
                title VARCHAR(255),
                description TEXT,
                due_date TIMESTAMP WITH TIME ZONE,
                status VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE,
                update_task TIMESTAMP WITH TIME ZONE
            ) AS $$
            BEGIN
                IF p_id IS NULL OR p_id < 1 THEN
                    RAISE EXCEPTION 'Invalid task ID';
                END IF;

                RETURN QUERY 
                SELECT 
                    t.id,
                    t.title,
                    t.description,
                    t.due_date,
                    t.status,
                    (t.created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') AS created_at,
                    (t.update_task AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') AS update_task
                FROM tasks t 
                WHERE t.id = p_id;
            END;
            $$ LANGUAGE plpgsql;
        """)

        # Function to update a task
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_task_by_id(
                p_id INTEGER,
                p_title VARCHAR(255),
                p_description TEXT,
                p_due_date TIMESTAMP WITH TIME ZONE,
                p_status VARCHAR(50)
            )
            RETURNS BOOLEAN AS $$
            BEGIN
                IF p_id IS NULL OR p_id < 1 THEN
                    RAISE EXCEPTION 'Invalid task ID';
                END IF;

                IF p_title IS NOT NULL AND trim(p_title) = '' THEN
                    RAISE EXCEPTION 'Title cannot be empty if provided';
                END IF;

                UPDATE tasks
                SET title = COALESCE(trim(p_title), title),
                    description = CASE 
                        WHEN p_description IS NULL THEN description
                        WHEN trim(p_description) = '' THEN NULL
                        ELSE trim(p_description)
                    END,
                    due_date = COALESCE(p_due_date, due_date),
                    status = COALESCE(lower(trim(p_status)), status),
                    update_task = (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Kolkata')
                WHERE id = p_id;

                RETURN FOUND;
            END;
            $$ LANGUAGE plpgsql;
        """)

        # Function to delete a task
        cursor.execute("""
            CREATE OR REPLACE FUNCTION delete_task_by_id(p_id INTEGER)
            RETURNS BOOLEAN AS $$
            BEGIN
                IF p_id IS NULL OR p_id < 1 THEN
                    RAISE EXCEPTION 'Invalid task ID';
                END IF;

                DELETE FROM tasks WHERE id = p_id;
                RETURN FOUND;
            END;
            $$ LANGUAGE plpgsql;
        """)


def setup_database():
    """Setup the database by creating the table and all required functions"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM pg_tables 
                WHERE tablename = 'tasks'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            initialize_database_functions()
            cursor.execute("SELECT ensure_tasks_table();")
