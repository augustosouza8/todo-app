# app.py
"""
Main application file for the To-Do List web application.
This version includes routes for user authentication (login, logout, register)
and full CRUD functionality for tasks and categories.
Database interactions use raw SQL, and user sessions are managed with Flask-Login.
"""

import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from db import get_db, init_db, init_app

import logging

logging.basicConfig(
    level=logging.DEBUG,  # Use DEBUG level for detailed logs during development
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# Initialize the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with a secure secret for production!
app.config['DATABASE'] = 'todo.db'  # SQLite database file

# Initialize database helper functions (registers teardown for closing DB)
init_app(app)

# Initialize Flask-Login for user authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if not authenticated

# -----------------------------------------------------------------------------
# User Authentication Helpers and Routes
# -----------------------------------------------------------------------------

# Define a User class for Flask-Login. Inherits from UserMixin.
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

def get_user_by_id(user_id):
    """
    Retrieve a user by ID.
    Returns a User object or None if not found.
    """
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if user is None:
        return None
    return User(user['id'], user['username'], user['password'])

def get_user_by_username(username):
    """
    Retrieve a user by username.
    Returns a User object or None if not found.
    """
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    if user is None:
        return None
    return User(user['id'], user['username'], user['password'])

# Flask-Login user loader callback.
@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

# Route: Home Page
@app.route('/')
def index():
    """
    Home page: If the user is authenticated, display a welcome message.
    Otherwise, redirect to the login page.
    """
    if current_user.is_authenticated:
        return render_template('index.html', user=current_user)
    else:
        return redirect(url_for('login'))

# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route:
      - GET: Display the login form.
      - POST: Process login credentials.
    NOTE: For demonstration purposes, password checking is in plain text.
    In production, always hash passwords.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and user.password == password:
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

# Route: Logout
@app.route('/logout')
@login_required
def logout():
    """
    Logout route: Ends the user session.
    """
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

# Route: Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration route:
      - GET: Display the registration form.
      - POST: Process registration and create a new user.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if get_user_by_username(username) is not None:
            flash('Username already exists.', 'error')
        else:
            db = get_db()
            try:
                db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                db.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except sqlite3.Error as e:
                flash(f'Error: {e}', 'error')
    return render_template('register.html')

# -----------------------------------------------------------------------------
# Task Routes
# -----------------------------------------------------------------------------

@app.route('/tasks')
@login_required
def list_tasks():
    """
    List all tasks for the logged-in user, including the category name.
    """
    db = get_db()
    # LEFT JOIN to retrieve category name (if any)
    tasks = db.execute('''
        SELECT tasks.*, categories.name AS category_name
        FROM tasks
        LEFT JOIN categories ON tasks.category_id = categories.id
        WHERE tasks.user_id = ?
    ''', (current_user.id,)).fetchall()
    return render_template('tasks.html', tasks=tasks)

from flask import jsonify  # Add this at the top if not already imported

@app.route('/tasks/<int:task_id>/update_completed', methods=['POST'])
@login_required
def update_completed(task_id):
    """
    Update the completed status of a task.
    Expects JSON payload with the key 'completed' (value "Yes" or "No").
    """
    db = get_db()
    data = request.get_json()
    if not data or 'completed' not in data:
        logging.error("Invalid request payload for updating task %s", task_id)
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

    new_status = 1 if data['completed'] == "Yes" else 0

    try:
        db.execute(
            'UPDATE tasks SET completed = ? WHERE id = ? AND user_id = ?',
            (new_status, task_id, current_user.id)
        )
        db.commit()
        logging.info("Updated task %s completed status to %s", task_id, new_status)
        return jsonify({'status': 'success', 'message': 'Task updated'})
    except sqlite3.Error as e:
        logging.error("Error updating task %s: %s", task_id, e)
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/tasks/add', methods=['GET', 'POST'])
@login_required
def add_task():
    """
    Add a new task.
    GET: Display the form for creating a new task.
    POST: Process the submitted form and insert the task into the database.
    """
    db = get_db()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        category_id = request.form.get('category_id') or None  # Optional category
        try:
            db.execute(
                'INSERT INTO tasks (title, description, user_id, category_id) VALUES (?, ?, ?, ?)',
                (title, description, current_user.id, category_id)
            )
            db.commit()
            flash('Task added successfully!', 'success')
            return redirect(url_for('list_tasks'))
        except sqlite3.Error as e:
            flash('Error adding task: ' + str(e), 'error')
    # Retrieve categories for the dropdown list
    categories = db.execute('SELECT * FROM categories WHERE user_id = ?', (current_user.id,)).fetchall()
    return render_template('add_task.html', categories=categories)

@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """
    Edit an existing task.
    GET: Display the form pre-filled with the task's current data.
    POST: Update the task in the database.
    """
    db = get_db()
    task = db.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, current_user.id)).fetchone()
    if not task:
        flash('Task not found.', 'error')
        return redirect(url_for('list_tasks'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        category_id = request.form.get('category_id') or None
        # Checkbox for completed returns 'on' when checked
        completed = 1 if request.form.get('completed') == 'on' else 0
        try:
            db.execute(
                'UPDATE tasks SET title = ?, description = ?, category_id = ?, completed = ? '
                'WHERE id = ? AND user_id = ?',
                (title, description, category_id, completed, task_id, current_user.id)
            )
            db.commit()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('list_tasks'))
        except sqlite3.Error as e:
            flash('Error updating task: ' + str(e), 'error')
    # Retrieve categories for the dropdown list
    categories = db.execute('SELECT * FROM categories WHERE user_id = ?', (current_user.id,)).fetchall()
    return render_template('edit_task.html', task=task, categories=categories)

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """
    Delete a task.
    """
    db = get_db()
    try:
        db.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, current_user.id))
        db.commit()
        flash('Task deleted successfully!', 'success')
    except sqlite3.Error as e:
        flash('Error deleting task: ' + str(e), 'error')
    return redirect(url_for('list_tasks'))

# -----------------------------------------------------------------------------
# Category Routes
# -----------------------------------------------------------------------------

@app.route('/categories')
@login_required
def list_categories():
    """
    List all categories for the logged-in user.
    """
    db = get_db()
    categories = db.execute('SELECT * FROM categories WHERE user_id = ?', (current_user.id,)).fetchall()
    return render_template('categories.html', categories=categories)

@app.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    """
    Add a new category.
    GET: Display the form for adding a new category.
    POST: Process the submitted data and insert the category.
    """
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        try:
            db.execute('INSERT INTO categories (name, user_id) VALUES (?, ?)', (name, current_user.id))
            db.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('list_categories'))
        except sqlite3.Error as e:
            flash('Error adding category: ' + str(e), 'error')
    return render_template('add_category.html')

@app.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """
    Edit an existing category.
    GET: Display the form pre-filled with the category data.
    POST: Update the category.
    """
    db = get_db()
    category = db.execute('SELECT * FROM categories WHERE id = ? AND user_id = ?', (category_id, current_user.id)).fetchone()
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('list_categories'))
    if request.method == 'POST':
        name = request.form['name']
        try:
            db.execute('UPDATE categories SET name = ? WHERE id = ? AND user_id = ?', (name, category_id, current_user.id))
            db.commit()
            flash('Category updated successfully!', 'success')
            return redirect(url_for('list_categories'))
        except sqlite3.Error as e:
            flash('Error updating category: ' + str(e), 'error')
    return render_template('edit_category.html', category=category)

@app.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    """
    Delete a category.
    """
    db = get_db()
    try:
        db.execute('DELETE FROM categories WHERE id = ? AND user_id = ?', (category_id, current_user.id))
        db.commit()
        flash('Category deleted successfully!', 'success')
    except sqlite3.Error as e:
        flash('Error deleting category: ' + str(e), 'error')
    return redirect(url_for('list_categories'))

# -----------------------------------------------------------------------------
# Application Entry Point
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    # Since Flask 3.1.0 removed the before_first_request decorator,
    # we initialize the database explicitly within the app context.
    with app.app_context():
        init_db()
    app.run(debug=True, port=5001)
