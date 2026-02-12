# FairChoices Assignment

A Django-based application for managing workflows and core functionalities.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)

## Overview

This project is a Django web application that provides workflow management and core business logic functionalities. It follows Django best practices and includes comprehensive testing with pytest.

## Features

- Django-based backend architecture
- Workflow management system
- Core business logic modules
- Environment-based configuration
- Pre-commit hooks for code quality
- Comprehensive test coverage with pytest

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (venv or virtualenv)
- Git

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/viperthapa/fairchoices-assignment.git
cd fairchoices-assignment
```

2. **Create and activate a virtual environment**

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirement.txt
```

4. **Install pre-commit hooks**

```bash
pre-commit install
```

## Configuration

1. **Create environment file**

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

2. **Update environment variables**

Edit the `.env` file with your configuration:

```env
# Database Configuration
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name


# Django Settings
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Add other environment variables as needed
```

3. **Run database migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Create a superuser (optional)**

```bash
python manage.py createsuperuser
```

## Running the Application

**Start the development server:**

```bash
python manage.py runserver or python3 manage.py runserver

```

The application will be available at `http://127.0.0.1:8000/`

## Running Tests

This project uses pytest for testing. To run the tests:

```bash
# Run all tests
pytest

```

## Project Structure

```
fairchoices-assignment/
│
├── core/                      # Core application modules
│   ├── migrations/           # Database migrations
│   ├── models.py            # Database models
│   ├── views.py             # View logic
│   ├── urls.py              # URL routing
│   └── ...
│
├── workflow/                 # Workflow management modules
│   ├── settings.py/
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
│
├── .env.example             # Example environment variables
├── .gitignore              # Git ignore rules
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── manage.py               # Django management script
├── pytest.ini              # Pytest configuration
├── requirement.txt         # Python dependencies
└── README.md              # Project documentation
```

## Technologies Used

- **Python** - Programming language
- **Django** - Web framework
- **pytest** - Testing framework
- **pre-commit** - Git hooks for code quality

### Core Dependencies

The following packages are required to run this application. Exact versions are specified in `requirement.txt`:

```
# Core Framework
Django==X.X.X

# Database
psycopg2-binary==X.X.X  # PostgreSQL adapter (if using PostgreSQL)

# Testing
pytest==X.X.X
pytest-django==X.X.X

# Code Quality
pre-commit==X.X.X
black==X.X.X  # Code formatter (if used)
flake8==X.X.X  # Linter (if used)

# Environment Management
python-decouple==X.X.X  # or python-dotenv

# API (if applicable)
djangorestframework==X.X.X

# Additional packages as per your requirement.txt
```

**Note:** Replace X.X.X with actual versions from your `requirement.txt` file.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Quality

This project uses pre-commit hooks to maintain code quality. Make sure all checks pass before committing:

```bash
pre-commit run --all-files
```


## Support

For questions or support, please open an issue in the GitHub repository.

---

**Note:** Make sure to update the `.env` file with your specific configuration before running the application.
