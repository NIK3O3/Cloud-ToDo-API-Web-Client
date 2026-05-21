# Cloud ToDo API + Web Client MVP

Production-oriented MVP for a ToDo API and static web client on AWS.

## Stack

- **Backend:** FastAPI, SQLAlchemy 2, Alembic, Postgres
- **Frontend:** static HTML/CSS/JS, deployable to S3 + CloudFront
- **Runtime:** Docker container, AWS App Runner-ready
- **Database:** Amazon RDS PostgreSQL or Aurora Serverless v2
- **Secrets:** AWS Secrets Manager exposed to App Runner as runtime environment secrets
- **Observability:** JSON/key-value structured logs with request id
- **CI/CD:** GitHub Actions lint/tests/Docker build/ECR push/App Runner deployment trigger

## Local run with Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Services:

- Frontend: `http://localhost:8080`
- API: `http://localhost:8000`
- Swagger/OpenAPI: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

Default local API key:

```text
dev-api-key
```

Use it in requests as:

```bash
curl -H "X-API-Key: dev-api-key" http://localhost:8000/api/tasks
```

## Environment variables

| Variable | Required | Example | Description |
|---|---:|---|---|
| `ENV` | no | `prod` | Runtime environment: `local`, `test`, `dev`, `prod`. |
| `API_KEY` | yes | from Secrets Manager | Required value for `X-API-Key`. |
| `DATABASE_URL` | yes | `postgresql+psycopg://user:pass@host:5432/todo` | SQLAlchemy DB connection string. |
| `CORS_ORIGINS` | yes | `https://d111.cloudfront.net,https://app.example.com` | Comma-separated allowed frontend origins. |
| `LOG_LEVEL` | no | `INFO` | Python logging level. |
| `RUN_MIGRATIONS` | no | `true` | Runs `alembic upgrade head` at container startup. |
| `PORT` | no | `8000` | Container port used by App Runner. |

## Database migrations

Local Docker Compose runs migrations automatically via `RUN_MIGRATIONS=true`.

Manual migration:

```bash
cd backend
DATABASE_URL="postgresql+psycopg://todo:todo@localhost:5432/todo" alembic upgrade head
```

Create a new migration after model changes:

```bash
cd backend
alembic revision --autogenerate -m "describe change"
```

## API contract

Protected endpoints require `X-API-Key`:

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/tasks` | Create task. |
| `GET` | `/api/tasks?status=&priority=&limit=&offset=` | List tasks with filtering and pagination. |
| `GET` | `/api/tasks/{id}` | Get task by id. |
| `PUT` | `/api/tasks/{id}` | Replace task. |
| `PATCH` | `/api/tasks/{id}` | Update status and/or priority. |
| `DELETE` | `/api/tasks/{id}` | Delete task. |
| `GET` | `/health` | Public health check. |

Stable error format:

```json
{ "code": "VALIDATION_ERROR", "message": "Request validation failed", "details": [] }
```

## Tests and lint

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check app tests
pytest
```

Current test suite includes:

- 7 unit tests for service behavior
- 6 integration tests for API behavior, validation, auth and delete flow

## AWS deployment notes

### Backend: App Runner + ECR

1. Create ECR repository.
2. Create Secrets Manager secrets for:
   - `API_KEY`
   - `DATABASE_URL`
3. Create or update App Runner service from the ECR image.
4. Configure runtime environment variables/secrets:
   - `API_KEY` from Secrets Manager
   - `DATABASE_URL` from Secrets Manager
   - `CORS_ORIGINS=https://<cloudfront-domain>`
   - `RUN_MIGRATIONS=true`
   - `PORT=8000`
5. Ensure App Runner instance role can read the referenced Secrets Manager secrets.
6. Attach App Runner to a VPC connector if RDS is private.

### Frontend: S3 + CloudFront

1. Create private S3 bucket for frontend assets.
2. Upload `frontend/` contents.
3. Put CloudFront in front of the bucket.
4. Configure the web UI with API URL and API key on first load.

## CI/CD setup

GitHub repository secrets/variables expected by `.github/workflows/ci-cd.yml`:

| Name | Type | Description |
|---|---|---|
| `AWS_ACCOUNT_ID` | secret | AWS account id. |
| `AWS_REGION` | variable or secret | Example: `eu-central-1`. |
| `AWS_ROLE_TO_ASSUME` | secret | IAM role ARN for GitHub OIDC. |
| `ECR_REPOSITORY` | variable or secret | ECR repository name. |
| `APP_RUNNER_SERVICE_ARN` | secret, optional | If set, workflow starts an App Runner deployment. |

## Submission URLs

Fill these after deployment:

- Frontend CloudFront URL: `TODO`
- API URL: `TODO`

## OpenAPI / Postman

- Swagger UI is available at `/docs`.
- Raw OpenAPI JSON is available at `/openapi.json`.
- Postman collection: `postman_collection.json`.
