# tests/test_app.py

import os
import tempfile
import pytest
from app import app  # Import your Flask app
from db import init_db


@pytest.fixture
def client():
    """
    Set up a temporary database and test client for each test.
    """
    # Create a temporary file to serve as our test database
    db_fd, temp_db = tempfile.mkstemp()
    app.config['DATABASE'] = temp_db
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            # Initialize the database schema in the temporary database
            init_db()
        yield client

    # Clean up: close and remove the temporary file
    os.close(db_fd)
    os.unlink(temp_db)


def test_register_and_login(client):
    """
    Test the user registration and login process.
    """
    # Register a new user
    rv = client.post('/register', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    assert b'Registration successful' in rv.data or b'Please log in' in rv.data

    # Log in with the new user credentials
    rv = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    assert b'Welcome, testuser!' in rv.data


def test_add_task(client):
    """
    Test adding a new task after logging in.
    """
    # Register and log in first
    client.post('/register', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)

    # Add a new task
    rv = client.post('/tasks/add', data={
        'title': 'Test Task',
        'description': 'This is a test task',
        'category_id': ''
    }, follow_redirects=True)
    # Look for a success message or redirection
    assert b'Task added successfully' in rv.data

    # Verify that the task appears on the tasks page
    rv = client.get('/tasks')
    assert b'Test Task' in rv.data


def test_update_completed_status(client):
    """
    Test that the AJAX route for updating a task's completed status works.
    """
    # Register and log in
    client.post('/register', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)

    # Add a new task first
    client.post('/tasks/add', data={
        'title': 'Test Task',
        'description': 'This is a test task',
        'category_id': ''
    }, follow_redirects=True)

    # Get the tasks page and extract the task id from the page
    # For simplicity, assume that the first task in the database is the one we just added.
    # In a more robust test, you might query the database directly.
    import sqlite3
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    cur.execute("SELECT id FROM tasks LIMIT 1")
    row = cur.fetchone()
    task_id = row['id']

    # Now, simulate an AJAX POST to update the completed status to "Yes"
    rv = client.post(f'/tasks/{task_id}/update_completed', json={'completed': 'Yes'})
    json_data = rv.get_json()
    assert json_data['status'] == 'success'

    # Optionally, verify that the database was updated:
    cur.execute("SELECT completed FROM tasks WHERE id = ?", (task_id,))
    updated_status = cur.fetchone()['completed']
    assert updated_status == 1

    db.close()
