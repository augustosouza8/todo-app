# db.py
"""
This module provides functions for connecting to the SQLite database,
closing the connection, and initializing the database schema.
"""

import sqlite3
from flask import current_app, g

def get_db():
    """
    Returns a database connection for the current application context.
    The connection is stored in Flask's 'g' object so that it can be reused
    during a single request.
    """
    if 'db' not in g:
        # Connect to the SQLite database specified in the app configuration.
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES  # Enable type detection
        )
        # Use a Row factory to access columns by name.
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """
    Closes the database connection at the end of the request.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """
    Initializes the database by creating the required tables if they do not exist.
    This includes tables for users, categories, and tasks.
    """
    db = get_db()
    with db:
        # Create the 'users' table
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        ''')
        # Create the 'categories' table
        db.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        ''')
        # Create the 'tasks' table
        db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed INTEGER DEFAULT 0,
                user_id INTEGER NOT NULL,
                category_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            );
        ''')

def init_app(app):
    """
    Registers the function to close the database connection after each request.
    """
    app.teardown_appcontext(close_db)
