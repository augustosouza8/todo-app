# app.py
"""
Main application file for the To-Do List web application.
This version uses PostgreSQL with SQLAlchemy as the ORM for database interactions.
User authentication is handled with Flask-Login.
"""

# ---------------------------
# Load Environment Variables
# ---------------------------
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# ---------------------------
# Import Required Modules and Initialize Flask
# ---------------------------
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Debug-level logging for development
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ---------------------------
# Initialize the Flask Application and Configure It
# ---------------------------
app = Flask(__name__)
# Use the SECRET_KEY and DATABASE_URL from the .env file
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ---------------------------
# Initialize Extensions
# ---------------------------
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to 'login' if user is not authenticated

# ---------------------------
# Define Database Models Using SQLAlchemy
# ---------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # Auto-increment primary key
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    # Relationships
    tasks = db.relationship('Task', backref='user', lazy=True)
    categories = db.relationship('Category', backref='user', lazy=True)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tasks = db.relationship('Task', backref='category', lazy=True)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)

# ---------------------------
# Create Database Tables if They Don't Exist
# ---------------------------
with app.app_context():
    db.create_all()

# ---------------------------
# User Loader for Flask-Login
# ---------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------------------
# Routes for User Authentication
# ---------------------------
@app.route('/')
def index():
    """Home page: display a welcome message if authenticated, else redirect to login."""
    if current_user.is_authenticated:
        return render_template('index.html', user=current_user)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route:
    - GET: Display login form.
    - POST: Validate credentials and log in the user.
    NOTE: Passwords are checked in plain text (for demonstration only).
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout route: ends the user session."""
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration route:
    - GET: Display the registration form.
    - POST: Create a new user.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
        else:
            new_user = User(username=username, password=password)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error: {e}', 'error')
    return render_template('register.html')

# ---------------------------
# Routes for Task Management
# ---------------------------
@app.route('/tasks')
@login_required
def list_tasks():
    """
    List all tasks for the logged-in user.
    For each task, if a category is associated, it can be accessed via task.category.name.
    """
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('tasks.html', tasks=tasks)

@app.route('/tasks/<int:task_id>/update_completed', methods=['POST'])
@login_required
def update_completed(task_id):
    """
    Update the completed status of a task via an AJAX request.
    Expects JSON payload with 'completed' (value "Yes" or "No").
    """
    data = request.get_json()
    if not data or 'completed' not in data:
        logging.error("Invalid request payload for updating task %s", task_id)
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

    new_status = True if data['completed'] == "Yes" else False
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'status': 'error', 'message': 'Task not found'}), 404
    try:
        task.completed = new_status
        db.session.commit()
        logging.info("Updated task %s completed status to %s", task_id, new_status)
        return jsonify({'status': 'success', 'message': 'Task updated'})
    except Exception as e:
        db.session.rollback()
        logging.error("Error updating task %s: %s", task_id, e)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/tasks/add', methods=['GET', 'POST'])
@login_required
def add_task():
    """
    Add a new task:
    - GET: Display the task creation form.
    - POST: Create the task in the database.
    """
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        category_id = request.form.get('category_id') or None
        new_task = Task(title=title, description=description, user_id=current_user.id, category_id=category_id)
        try:
            db.session.add(new_task)
            db.session.commit()
            flash('Task added successfully!', 'success')
            return redirect(url_for('list_tasks'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding task: ' + str(e), 'error')
    # Retrieve categories for the dropdown list
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('add_task.html', categories=categories)

@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """
    Edit an existing task:
    - GET: Display the form pre-filled with the task's data.
    - POST: Update the task in the database.
    """
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        flash('Task not found.', 'error')
        return redirect(url_for('list_tasks'))
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form.get('description', '')
        task.category_id = request.form.get('category_id') or None
        task.completed = True if request.form.get('completed') == 'on' else False
        try:
            db.session.commit()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('list_tasks'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating task: ' + str(e), 'error')
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('edit_task.html', task=task, categories=categories)

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """
    Delete a task.
    """
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        flash('Task not found.', 'error')
    else:
        try:
            db.session.delete(task)
            db.session.commit()
            flash('Task deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error deleting task: ' + str(e), 'error')
    return redirect(url_for('list_tasks'))

# ---------------------------
# Routes for Category Management
# ---------------------------
@app.route('/categories')
@login_required
def list_categories():
    """
    List all categories for the logged-in user.
    """
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('categories.html', categories=categories)

@app.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    """
    Add a new category:
    - GET: Display the category creation form.
    - POST: Create the category in the database.
    """
    if request.method == 'POST':
        name = request.form['name']
        new_category = Category(name=name, user_id=current_user.id)
        try:
            db.session.add(new_category)
            db.session.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('list_categories'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding category: ' + str(e), 'error')
    return render_template('add_category.html')

@app.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """
    Edit an existing category:
    - GET: Display the form pre-filled with the category's data.
    - POST: Update the category in the database.
    """
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('list_categories'))
    if request.method == 'POST':
        category.name = request.form['name']
        try:
            db.session.commit()
            flash('Category updated successfully!', 'success')
            return redirect(url_for('list_categories'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating category: ' + str(e), 'error')
    return render_template('edit_category.html', category=category)

@app.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    """
    Delete a category.
    """
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
    if not category:
        flash('Category not found.', 'error')
    else:
        try:
            db.session.delete(category)
            db.session.commit()
            flash('Category deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error deleting category: ' + str(e), 'error')
    return redirect(url_for('list_categories'))

# ---------------------------
# Application Entry Point
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5001)
