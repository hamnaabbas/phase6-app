# Phase 4 - Full Stack Application

## Features
- ✅ React frontend dashboard
- ✅ User authentication (login/register)
- ✅ JWT token management
- ✅ CRUD operations for items
- ✅ Protected routes
- ✅ PostgreSQL database
- ✅ Docker containerization
- ✅ Responsive design

## Quick Start

### Run Everything with Docker
```bash
docker-compose up --build
```

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Database**: localhost:5432

### Run Separately

**Backend:**
```bash
docker-compose up app db
```

**Frontend (in separate terminal):**
```bash
cd frontend
npm start
```

## User Flow
1. Visit http://localhost:3000
2. Register a new account
3. Login with credentials
4. Create, view, edit, and delete items
5. View profile and stats

## Tech Stack
- **Frontend**: React 18, React Router, Axios
- **Backend**: Flask, SQLAlchemy, JWT
- **Database**: PostgreSQL
- **Containerization**: Docker, Docker Compose