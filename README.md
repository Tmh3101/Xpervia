# Xpervia LMS

Xpervia is a Learning Management System (LMS) project. This repository contains the backend built with Python Django REST Framework. The frontend will be developed later and will be placed at the same level as the backend directory.

## Project Structure

xpervia/ ├── backend/ │ ├── .gitignore │ ├── api/ │ ├── backend/ │ ├── manage.py │ └── requirements.txt ├── frontend/ │ ├── .gitignore │ └── src/ ├── .gitignore └── README.md

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Django 5.1.4
- Django REST Framework 3.15.2

### Installation

1. Clone the repository:

git clone https://github.com/yourusername/xpervia.git
cd xpervia/backend

2. Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install the dependencies:

pip install -r requirements.txt

4. Set up the PostgreSQL database and update the DATABASES settings in settings.py accordingly.

5. Apply the migrations:

python manage.py migrate

6. Create a superuser:

python manage.py createsuperuser

7. Run the development server:

python manage.py runserver

API Endpoints
The API endpoints are defined in the urls.py file. Here are some of the available endpoints:

POST /api/register/ - Register a new user
POST /api/token/login/ - Login and obtain a token
POST /api/token/logout/ - Logout and invalidate the token
GET /api/users/ - List all users (Admin only)
GET /api/users/<uuid:id>/ - Retrieve, update, or delete a user by ID (Admin only)
PUT /api/users/<uuid:id>/update/ - Update user information (Admin only)
PUT /api/users/<uuid:id>/update-password/ - Update user password (Requires old password)
GET /api/courses/ - List all courses
POST /api/courses/create/ - Create a new course (Teacher only)
GET /api/courses/<int:id>/ - Retrieve a course by ID
PUT /api/courses/<int:id>/update/ - Update a course by ID (Teacher and owner only)
DELETE /api/courses/<int:id>/delete/ - Delete a course by ID (Teacher and owner only)