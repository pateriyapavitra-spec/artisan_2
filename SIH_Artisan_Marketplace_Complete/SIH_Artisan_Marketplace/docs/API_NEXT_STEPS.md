# Production API / Backend Next Steps

The current MVP is intentionally local and simple.

For a production version:

- FastAPI backend
- PostgreSQL database
- S3-compatible image storage
- JWT/OAuth authentication
- Celery/RQ background jobs
- Redis cache
- Structured Pydantic schemas
- Marketplace order service
- Payment gateway integration
- Admin moderation
- Audit logs
- Rate limiting
- Monitoring and error tracking

Suggested API endpoints:

POST /auth/login
POST /artisans
POST /products/analyse-image
POST /products
GET /products
GET /products/{id}
PATCH /products/{id}
DELETE /products/{id}
POST /pricing/estimate
POST /orders
GET /orders/{id}
