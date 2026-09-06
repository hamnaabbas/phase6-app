# Phase 6 - Full Stack App with CI/CD

## Features
- ✅ GitHub Actions CI/CD pipeline
- ✅ Automated testing on push
- ✅ Docker image building and pushing
- ✅ Production-ready Dockerfiles
- ✅ Interactive Swagger API docs
- ✅ React frontend
- ✅ JWT authentication
- ✅ PostgreSQL database

## Quick Start

### Local Development
```bash
docker-compose up --build
```

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs

### Production Build
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## CI/CD Pipeline

### What it does:
1. **On every push/PR:**
   - ✅ Runs backend tests with PostgreSQL
   - ✅ Builds frontend and checks for errors
   - ✅ Builds Docker images
   - ✅ Runs code quality checks (flake8, black)

2. **On merge to main:**
   - ✅ Builds production Docker images
   - ✅ Pushes to Docker Hub
   - ✅ Ready for deployment

### Setup GitHub Secrets:
In your GitHub repo → Settings → Secrets and variables → Actions:

- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub access token

### Workflow Status:
- **CI**: `.github/workflows/ci.yml`
- **CD**: `.github/workflows/cd.yml`

## Project Structure