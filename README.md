# ShowBay Task Management API

A robust REST API service built with FastAPI and PostgreSQL that acts as a bridge between a local database and an external API, demonstrating complex data flows, strict validation, and comprehensive testing.

## 📋 Table of Contents
- [Problem Understanding & Assumptions](#problem-understanding--assumptions)
- [Design Decisions](#design-decisions)
- [Solution Approach](#solution-approach)
- [Error Handling Strategy](#error-handling-strategy)
- [How to Run the Project](#how-to-run-the-project)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Architecture](#architecture)

## Problem Understanding & Assumptions

### Interpretation
This project implements a task management system that bridges local PostgreSQL storage with an external API (using JSONPlaceholder as an example). The service demonstrates modern backend engineering practices including async processing, data validation, error handling, and comprehensive testing.

### Use Case
The system serves as an **AI-Powered Task Summarizer** where tasks can be created locally, and optionally enriched with data from external sources like content summarization APIs, GitHub repositories, or other data services.

### Assumptions
- **Database**: PostgreSQL is available and accessible via the connection string in environment variables
- **External API Reliability**: External APIs may fail, timeout, or return unexpected responses - the system should handle these gracefully
- **User Authentication**: For this assessment, authentication is not implemented but would use JWT tokens in production
- **Data Formats**: External APIs return JSON data in expected formats; fallback behavior when formats change
- **Rate Limits**: External APIs may have rate limits; the system should handle these appropriately
- **Concurrent Access**: Multiple users may access the API simultaneously, requiring proper connection pooling

## Design Decisions

### Database Schema
The database uses a single `tasks` table with the following structure:
- `id`: Primary key, auto-incrementing integer
- `title`: Required string (1-255 chars), task title
- `description`: Optional string (up to 1000 chars), task description
- `status`: String (default: "pending"), possible values: pending, in_progress, completed
- `priority`: String (default: "medium"), possible values: low, medium, high
- `external_id`: Optional integer, ID from external API
- `user_id`: Optional string (up to 100 chars), to identify the user who created the task
- `external_api_data`: Optional text field to store JSON data fetched from external APIs
- `created_at`: Timestamp when the task was created
- `updated_at`: Timestamp when the task was last updated
- `completed_at`: Optional timestamp when the task was completed

**Indexing choices**: Primary key index on `id`, potential indexes on `status` and `user_id` for efficient filtering.

### Project Structure
```
showbay/
├── api/                    # API route definitions
│   ├── __init__.py
│   └── tasks.py           # Task-related endpoints
├── models/                # SQLModel database models
│   └── task.py
├── schemas/               # Pydantic validation schemas
│   ├── task.py
│   └── error.py
├── database/              # Database configuration
│   └── database.py
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── external_api.py    # External API integration
│   ├── exception_handlers.py # Custom exception handlers
│   └── exceptions.py      # Custom exception classes
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── conftest.py        # Test configuration
│   ├── test_models.py     # Model tests
│   ├── test_api.py        # API integration tests
│   ├── test_external_api.py # External API tests
│   └── test_error_handling.py # Error handling tests
├── main.py               # Application entry point
├── requirements.txt      # Dependencies
├── .env.example          # Environment variables example
├── Dockerfile            # Container configuration
└── README.md
```

### Validation Logic
- **Pydantic Models**: Used for strict request/response validation
- **Field Constraints**: Min/max length, required fields, type validation
- **Business Logic Validation**: Custom validators where needed
- **Database Constraints**: SQLModel enforces constraints at the database level
- **Request Validation**: FastAPI automatically validates and returns 422 for invalid requests

### External API Design
- **Configuration**: Base URL and timeout configurable via environment variables
- **Async Processing**: All external API calls are async to prevent blocking
- **Timeout Handling**: Configurable timeout with fallback behavior
- **Error Resilience**: API failures don't break core functionality
- **Rate Limiting**: Prepared for integration with rate limiting middleware
- **Caching**: Ready for integration with caching layer for repeated requests

## Solution Approach

### Data Flow Walkthrough

1. **Request Entry Point**: Client sends request to FastAPI endpoint
2. **Validation**: Pydantic models validate request data, returning 422 on failure
3. **Authentication**: (Conceptual) JWT validation would occur here in production
4. **Business Logic**: Process request, potentially calling external services
5. **Database Operation**: SQLModel handles database interactions with proper session management
6. **Response Formation**: Convert database models to response schemas
7. **Response**: Return appropriate HTTP status code and JSON response

### API Endpoint Flow

**POST /api/v1/tasks/** - Create Task
1. Validate input using `TaskCreate` schema
2. If `external_id` provided, fetch data from external API
3. Create task record in PostgreSQL
4. Return created task with 201 status

**GET /api/v1/tasks/{id}** - Get Task
1. Query database for task by ID
2. Return task or 404 if not found
3. Return with 200 status

**PUT /api/v1/tasks/{id}** - Update Task
1. Validate input using `TaskUpdate` schema
2. Query for existing task
3. Update fields and save to database
4. Return updated task with 200 status

**DELETE /api/v1/tasks/{id}** - Delete Task
1. Query for existing task
2. Delete from database
3. Return 204 No Content

## Error Handling Strategy

### Exception Types Handled
- **Validation Errors**: 422 Unprocessable Entity for invalid request data
- **Not Found**: 404 Not Found for missing resources
- **External API Errors**: 502 Bad Gateway or 408 Request Timeout
- **Database Errors**: 500 Internal Server Error
- **General Errors**: 500 Internal Server Error

### Global Exception Handlers
- **RequestValidationError**: Handles Pydantic validation errors
- **ExternalAPIException**: Handles external API integration errors
- **General Exception**: Catches unexpected errors

### Resilience Features
- **Graceful Degradation**: When external API fails, core functionality remains available
- **Connection Pooling**: Proper database connection management
- **Timeout Handling**: Prevents hanging requests to external services
- **Logging**: Comprehensive error logging for debugging

## How to Run the Project

### Prerequisites
- Python 3.10+
- PostgreSQL server
- pip package manager

### Setup Instructions

1. **Clone the repository** (or extract the project files)
   ```bash
   # If you have the project files locally
   cd showbay
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   # Edit .env with your database connection details
   ```

5. **Run the application**
   ```bash
   uvicorn showbay.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Using Docker (Alternative)
```bash
# Build the image
docker build -t showbay-api .

# Run the container
docker run -p 8000:8000 --env-file .env showbay-api
```

### Required Environment Variables
- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://username:password@localhost:5432/showbay_db`)
- `EXTERNAL_API_BASE_URL`: Base URL for external API (default: `https://jsonplaceholder.typicode.com`)
- `EXTERNAL_API_TIMEOUT`: Request timeout in seconds (default: `10`)
- `APP_HOST`: Host for the application (default: `0.0.0.0`)
- `APP_PORT`: Port for the application (default: `8000`)
- `DEBUG`: Enable debug mode (default: `False`)

### Example API Calls

#### 1. Create a Task
```bash
curl -X POST "http://localhost:8000/api/v1/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sample Task",
    "description": "This is a sample task",
    "status": "pending",
    "priority": "medium",
    "user_id": "user123"
  }'
```

#### 2. Get a Task
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/1"
```

#### 3. Update a Task
```bash
curl -X PUT "http://localhost:8000/api/v1/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Task Title",
    "status": "completed"
  }'
```

#### 4. Delete a Task
```bash
curl -X DELETE "http://localhost:8000/api/v1/tasks/1"
```

#### 5. List Tasks
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/"
```

### API Documentation
After starting the server, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative API docs**: http://localhost:8000/redoc

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=showbay

# Run specific test file
pytest showbay/tests/test_api.py

# Run tests with verbose output
pytest -v
```

### Test Categories
- **Unit Tests**: Test individual components (models, utility functions)
- **Integration Tests**: Test API endpoints with mocked external dependencies
- **Error Handling Tests**: Verify proper error responses
- **External API Tests**: Test external API integration with mocking

### Test Coverage
The test suite covers:
- Model validation and creation
- All 4 API endpoints (POST, GET, PUT, DELETE)
- Error handling scenarios
- External API integration (with mocking)
- Validation error cases

## Architecture

### Technology Stack
- **Language**: Python 3.10+
- **Framework**: FastAPI (with Pydantic for validation)
- **Database**: PostgreSQL with SQLModel ORM
- **Async HTTP**: httpx for external API calls
- **Testing**: pytest with HTTPX for integration tests
- **Validation**: Pydantic for request/response validation

### Design Patterns Used
- **Dependency Injection**: FastAPI's built-in DI for database sessions
- **Separation of Concerns**: Models, schemas, API routes, and utilities in separate modules
- **Async Programming**: Async/await for non-blocking operations
- **Clean Architecture**: Clear separation between business logic and infrastructure

### Security Considerations
- Input validation through Pydantic models
- SQL injection prevention through ORM
- Prepared for authentication integration (JWT)
- Environment-based configuration

### Performance Considerations
- Connection pooling for database
- Async processing for external API calls
- Efficient query patterns
- Ready for caching integration#   S h o w b a y  
 