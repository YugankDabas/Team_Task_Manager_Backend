# Team Task Manager Backend

This is the backend service for the Team Task Manager application, built with FastAPI. It provides a RESTful API for managing users, projects, and tasks.

## Features

*   **Authentication:** JWT-based user registration and login.
*   **Users:** User profile management.
*   **Projects:** Create, read, update, and delete projects. Manage project members.
*   **Tasks:** Create tasks within projects, assign them to members, and track status.
*   **Database:** SQLAlchemy ORM with support for PostgreSQL and SQLite.

## Tech Stack

*   **Framework:** FastAPI
*   **ORM:** SQLAlchemy
*   **Database:** SQLite (Default for development) / PostgreSQL
*   **Authentication:** JWT (python-jose), Password Hashing (passlib, bcrypt)
*   **Data Validation:** Pydantic

## Getting Started

### Prerequisites

*   Python 3.8+
*   Virtual Environment (recommended)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YugankDabas/Team_Task_Manager_Backend.git
    cd Team_Task_Manager_Backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables:**
    *   Copy the `.env.example` file to `.env`:
        ```bash
        copy .env.example .env  # On Windows
        cp .env.example .env    # On macOS/Linux
        ```
    *   Update the `.env` file with your specific configurations (Database URL, Secret Key, etc.).

### Running the Application

Start the FastAPI development server using `uvicorn`:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### API Documentation

FastAPI automatically generates interactive API documentation. Once the server is running, you can access:

*   **Swagger UI:** `http://127.0.0.1:8000/docs`
*   **ReDoc:** `http://127.0.0.1:8000/redoc`

## Project Structure

```text
backend/
├── auth/            # Authentication logic (JWT, dependencies)
├── models/          # SQLAlchemy database models
├── routes/          # API endpoints (users, projects, tasks, auth)
├── schemas/         # Pydantic schemas for data validation
├── .env.example     # Example environment variables
├── database.py      # Database connection and session setup
├── main.py          # FastAPI application entry point
└── requirements.txt # Project dependencies
```
