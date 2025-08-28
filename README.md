# Event Suit Service

A FastAPI-based service for managing events and registrations.

## Features

- Event management
- User registration
- Host assignments
- Vehicle sharing
- Daily preferences

## Local Development

1. Create a virtual environment:
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
# Edit .env with your database URL
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

## Deployment to Heroku

### Prerequisites

1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Have a Heroku account
3. Set up your database (PostgreSQL recommended for Heroku)

### Quick Deployment

1. **Set your database URL environment variable:**
```bash
export VAANI_DATABASE_URL="your_database_connection_string"
```

2. **Run the deployment script:**
```bash
chmod +x deploy.sh
./deploy.sh
```

### Manual Deployment

1. **Login to Heroku:**
```bash
heroku login
```

2. **Create a new Heroku app:**
```bash
heroku create your-app-name
```

3. **Set environment variables:**
```bash
heroku config:set VAANI_DATABASE_URL="your_database_connection_string"
```

4. **Deploy:**
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

5. **Open the app:**
```bash
heroku open
```

### Database Setup

For production, use a managed PostgreSQL service:

- **Heroku Postgres** (recommended for Heroku apps)
- **AWS RDS**
- **Google Cloud SQL**
- **DigitalOcean Managed Databases**

### Environment Variables

Required environment variables:
- `VAANI_DATABASE_URL`: Database connection string

### Scaling

To scale your application:
```bash
heroku ps:scale web=2  # Scale to 2 dynos
```

### Monitoring

View logs:
```bash
heroku logs --tail
```

View app status:
```bash
heroku ps
```

## API Documentation

Once deployed, visit:
- **Swagger UI**: `https://your-app.herokuapp.com/docs`
- **ReDoc**: `https://your-app.herokuapp.com/redoc`

## Project Structure

```
app/
├── api/           # API endpoints
├── models/        # Database models
├── schemas/       # Pydantic schemas
├── services/      # Business logic
└── utils/         # Utilities (config, database, logger)
```

## Technologies Used

- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server
- **PostgreSQL/MySQL**: Database support
