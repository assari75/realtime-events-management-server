# Events Management API

A real-time event management backend built with FastAPI, SQLAlchemy and Pydantic.

## Features

- RESTful API endpoints for event management
- Real-time updates via WebSocket connections
- Event creation, joining, and cancellation functionality
- Data validation using Pydantic models

## Installation

1. Clone the repository:
```bash
git clone https://github.com/assari75/realtime-events-management-server.git
cd realtime-events-management-server
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Create .env file in the main directory:
```env
DEVELOPMENT = True
DATABASE_URL = "your_database_url"
SECRET_KEY = "your_secret_key"
```

2. Start the server:
```bash
uvicorn main:app --reload
```

3. The API will be available at:
- HTTP endpoints: `http://localhost:8000`
- WebSocket endpoint: `ws://localhost:8000/ws/`

## Running Tests

Execute the test suite:
```bash
pytest
```
