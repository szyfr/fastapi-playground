# FastAPI MVC

A REST API built with FastAPI following the MVC pattern. Includes JWT authentication, role-based access control, product catalog management, and order processing — backed by PostgreSQL with async SQLAlchemy and Alembic migrations.

## How it works

The project is structured as an MVC application:

```
app/
├── controllers/   # Business logic (auth, products, orders)
├── core/          # Config, DB session, auth helpers, dependencies
├── middleware/    # Custom middleware
├── models/        # SQLAlchemy ORM models
├── requests/      # Pydantic input schemas
├── responses/     # Pydantic output schemas
├── routes/        # FastAPI routers
└── tests/         # Pytest test suite
migrations/        # Alembic DB migrations
```

**Request flow:** Route → Controller → Model (via async SQLAlchemy session) → Response

**Auth:** JWT tokens issued on login/register. Protected routes use `Bearer <token>` in the `Authorization` header. Admin-only routes additionally check `user.role == "admin"`.

**M2M auth:** A separate M2M secret signs tokens for service-to-service calls (`M2M_SECRET` in `.env`).

### Models

| Model | Description |
|---|---|
| `User` | Email/password accounts with `user` or `admin` role |
| `Product` | Catalog items with name, slug, price, stock |
| `Order` | User orders with status lifecycle and line items |
| `OrderItem` | Per-product line in an order (price snapshotted at order time) |

### Order status lifecycle

`pending` → `processing` → `completed` → `cancelled` / `refunded`

---

## Step-by-step setup

### 1. Prerequisites

- Python 3.12+
- PostgreSQL running and accessible

### 2. Clone and create a virtual environment

```bash
cd /var/www/fastapi
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Generate a secure secret key:

```bash
openssl rand -hex 32
```

Edit `.env` and set your values:

```env
APP_NAME="FastAPI MVC"
APP_VERSION="1.0.0"
DEBUG=true

DATABASE_URL=postgresql+asyncpg://user:password@localhost/db

CORS_ORIGINS=["http://localhost:3000"]

SECRET_KEY=<output of openssl rand -hex 32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

M2M_SECRET=<output of openssl rand -hex 32>
M2M_ALGORITHM=HS256
```

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the server

```bash
uvicorn app.main:app --reload
```

The API is now available at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`

Health check: `http://localhost:8000/health`

---

## API reference

All endpoints are prefixed with `/api/v1`.

### Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | — | Register a new user, returns token |
| `POST` | `/auth/login` | — | Login, returns token |
| `GET` | `/auth/me` | User | Get current user info |
| `PATCH` | `/auth/password` | User | Update password |

**Register / Login response:**
```json
{
  "access_token": "<jwt>",
  "user": { "id": 1, "email": "you@example.com", "first_name": "...", "last_name": "..." }
}
```

### Products

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/products/` | — | List products (paginated) |
| `GET` | `/products/{id}` | — | Get a single product |
| `POST` | `/products/` | Admin | Create a product |
| `PATCH` | `/products/{id}` | Admin | Update a product |
| `DELETE` | `/products/{id}` | Admin | Delete a product |

Query params for list: `skip`, `limit`, `sort_by` (`id`/`name`/`price`/`created_at`), `order` (`asc`/`desc`).

### Orders

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/orders/` | User | List own orders (paginated, filterable by status) |
| `GET` | `/orders/{id}` | User | Get a single order |
| `POST` | `/orders/` | User | Place a new order |
| `PATCH` | `/orders/{id}/cancel` | User | Cancel an order |

---

## Usage examples

### Register

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "secret", "first_name": "Jane", "last_name": "Doe"}'
```

### Login and save token

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "secret"}' | jq -r .access_token)
```

### List products

```bash
curl http://localhost:8000/api/v1/products/
```

### Create a product (admin only)

```bash
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Widget", "slug": "widget", "price": 9.99, "stock": 100}'
```

### Place an order

```bash
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"product_id": 1, "quantity": 2}], "shipping_address": "123 Main St"}'
```

---

## Running tests

Tests use an in-memory SQLite database — no external DB needed.

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest app/tests/api/test_auth.py -v
```

---

## Making a user an admin

Currently roles are set directly in the database. After creating a user via `/auth/register`, promote them:

```sql
UPDATE users SET role = 'ADMIN' WHERE email = 'you@example.com';
```
