# Deployment Guide

## Production Setup
1. Set up PostgreSQL and Redis
2. Configure environment variables in `.env`
3. Build and run:
```bash
docker-compose up --build -d
```

## Periodic Tasks
The system includes these scheduled tasks:
- Daily model retraining (3 AM UTC)
- Hourly post analysis updates

## Scaling
For high traffic:
- Increase Celery workers
- Add Redis cache
- Use PostgreSQL read replicas