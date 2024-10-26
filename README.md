# Daily Expense Tracker

A Flask-based REST API for tracking daily expenses with PostgreSQL backend.

## Features

- User authentication and authorization
- Expense tracking with categories
- Balance sheet generation
- Swagger documentation
- Dockerized deployment
- Automated testing

## Tech Stack

- Python 3.9
- Flask
- PostgreSQL
- SQLAlchemy
- Docker & Docker Compose
- JWT Authentication
- Swagger/OpenAPI

## Project Structure

```
.
├── app/
│   ├── config/         # Configuration settings
│   ├── exceptions/     # Custom exceptions
│   ├── models/         # Database models
│   ├── resources/      # API endpoints
│   ├── services/       # Business logic
│   └── utils/          # Utility functions
├── tests/              # Test suite
├── migrations/         # Database migrations
├── Dockerfile          # Production dockerfile
├── Dockerfile.test     # Testing dockerfile
├── docker-compose.yml  # Production compose
└── docker-compose.test.yml  # Testing compose
```

## Prerequisites

- Docker
- Docker Compose
- Make (optional, for using Makefile commands)

## Installation & Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/expense-tracker.git
cd expense-tracker
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Build and start the containers:
```bash
docker-compose up --build
```

The API will be available at `http://localhost:5000`

## Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

3. Run migrations:
```bash
flask db upgrade
```

4. Start the development server:
```bash
flask run
```

## Running Tests

Using Docker:
```bash
docker-compose -f docker-compose.test.yml up --build
```

Locally:
```bash
pytest -v
```

## API Documentation

Once the application is running, access the Swagger documentation at:
```
http://localhost:5000/api/docs
```

## Database Migrations

Create a new migration:
```bash
docker-compose exec web flask db migrate -m "description"
```

Apply migrations:
```bash
docker-compose exec web flask db upgrade
```

## Environment Variables

Required environment variables in `.env`:

```
FLASK_APP=run.py
FLASK_ENV=development
DATABASE_URL=postgresql://user:password@db:5432/expenses
SECRET_KEY=your-secret-key
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

