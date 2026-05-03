# ML Diabetes Tracker Backend

FastAPI backend for the ML Diabetes Tracker application.

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Virtual environment (recommended)

### Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize database:
```bash
python scripts/init_db.py
```

### Running the Application

#### Development Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Using Docker
```bash
# From project root
docker-compose up backend
```

### Testing

Run tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app --cov-report=html
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Core configuration
│   ├── db/            # Database configuration
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   └── services/      # Business logic
├── alembic/           # Database migrations
├── scripts/           # Utility scripts
├── tests/             # Test suite
└── main.py           # Application entry point
```