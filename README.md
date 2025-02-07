# To-do App 🗓️

A simple Flask-based web application for managing tasks and categories with secure user authentication.

![MIT License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-lightgrey)
![Tests](https://img.shields.io/badge/Tests-Pytest-red)

## ✨ Features

- **User Authentication System**
  - Secure registration and login flows
  - Session management and logout functionality
  - Password security measures

- **Task Management**
  - Create, read, update, and delete (CRUD) operations
  - Mark tasks as complete/incomplete
  - Rich text descriptions
  - Due date tracking

- **Category System**
  - Organize tasks with custom categories
  - Category-based filtering
  - Bulk category operations

- **Search & Filter**
  - Real-time search functionality
  - Multiple filter options
  - Sort by various criteria

- **Modern Interface**
  - Responsive design for all devices
  - Intuitive user experience
  - Clean, minimalist aesthetics

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/augustosouza8/augustosouza8-todo-app.git
   cd augustosouza8-todo-app
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv venv
   
   # Linux/MacOS
   source venv/bin/activate
   
   # Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   python -c "from db import init_db; init_db()"
   ```

5. **Launch application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5001` 🎉

## 💡 Usage Guide

### User Management
1. Register a new account or login with existing credentials
2. Secure password recovery flow available
3. Profile customization options

### Task Operations
1. Create new tasks with:
   - Title and description
   - Due date
   - Priority level
   - Category assignment
2. Manage existing tasks:
   - Edit task details
   - Toggle completion status
   - Delete tasks
   - Bulk actions available

### Category Management
1. Create custom categories
2. Edit category details
3. Delete unused categories
4. Assign/remove tasks from categories

### Search & Filter
1. Search tasks by title/description
2. Filter by:
   - Status (complete/incomplete)
   - Due date
   - Priority
   - Category

## 🧪 Testing

Run the test suite using pytest:

```bash
pytest tests/
```

For coverage report:
```bash
pytest --cov=app tests/
```

## 📁 Project Structure

```
.
├── app.py              # Application core
├── db.py              # Database configuration
├── requirements.txt    # Dependencies
├── static/            # Static assets
│   ├── css/          # Stylesheets
│   ├── js/           # JavaScript files
│   └── img/          # Images
├── templates/         # HTML templates
└── tests/            # Test suite
    ├── conftest.py   # Test configuration
    ├── test_app.py   # App tests
    └── test_db.py    # Database tests
```

## 🚨 Production Deployment

Before deploying to production, implement these critical security measures:

1. Security Configuration:
   - Set strong `SECRET_KEY` in `app.py`
   - Implement robust password hashing
   - Configure HTTPS
   - Set up proper session handling

2. Server Setup:
   - Use production-grade WSGI server (Gunicorn/uWSGI)
   - Set up reverse proxy (Nginx/Apache)
   - Configure proper database security
   - Implement rate limiting

3. Monitoring:
   - Set up error logging
   - Implement performance monitoring
   - Configure backup systems

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Made with ❤️ by [Augusto Souza](https://github.com/augustosouza8) and with assistance from ChatGPT ([click here to access the main used chat](https://chatgpt.com/share/67a69751-0650-8013-a443-c8e5c9c506e9)) 