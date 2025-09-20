# Music Center Student Registration - Backend

This backend provides a simple REST API to register students for a music center and to retrieve registered students.

Tech stack:
- Flask, flask-smorest (OpenAPI), SQLAlchemy
- MySQL (via PyMySQL)
- CORS enabled for integration with React frontend

## Running locally

1) Install dependencies
   pip install -r backend/requirements.txt

2) Configure database access via either:
   - Environment variables:
     - MYSQL_URL (full SQLAlchemy URL, takes precedence) e.g. mysql+pymysql://user:pass@host:3306/dbname
     - OR provide:
       - MYSQL_USER
       - MYSQL_PASSWORD
       - MYSQL_DB
       - MYSQL_HOST (default: localhost)
       - MYSQL_PORT (default: 3306)
   - Or ensure db_connection.txt is available in the sibling database container path:
     music-center-student-registration-87320-87330/music_center_student_database/db_connection.txt
     Supported format (example):
       mysql -uuser -ppassword -h127.0.0.1 -P3306 dbname

3) Start the server
   cd backend
   python run.py

4) API Docs (Swagger UI)
   Navigate to: /docs

## API

Base URL: /api

- Health Check
  GET / -> {"message":"Healthy"}

- Students
  - GET /api/students/ -> List all students
  - POST /api/students/ -> Create a new student
    JSON body:
    {
      "full_name": "Jane Doe",
      "email": "jane@example.com",
      "phone": "123-456-7890",
      "instrument": "Piano",
      "experience_level": "Beginner"  // One of: Beginner, Intermediate, Advanced
    }

Responses:
- 201 Created with created student payload
- 409 Conflict if email already registered
- 400 Bad Request for validation errors

## OpenAPI Spec
To (re)generate the OpenAPI document:
   cd backend
   python generate_openapi.py
This writes interfaces/openapi.json

## Notes
- Tables are auto-created on startup in this demo. Consider using proper migrations for production.
- CORS is enabled for all routes to support the React frontend.