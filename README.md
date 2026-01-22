# ShipEngine API Test Project

Test assignment for developing CRUD methods for ShipEngine API endpoints using FastAPI, SQLAlchemy, PostgreSQL, and asynchronous technologies.

## 📋 Project Description

Simplified API implementation for addresses, warehouses, and shipments based on [ShipEngine OpenAPI](https://shipengine.github.io/shipengine-openapi/). Complete end-to-end request processing: from endpoint to database write/read operations.

## 🏗️ Architecture

Based on [FastAPI-boilerplate](https://benavlabs.github.io/FastAPI-boilerplate/) from Benav Labs. Architecture was barely modified as the standard structure is adequate for the tasks.

**Service Layer** (`src/app/services/`) — the only significant addition. Handles:
- Creating/updating entities with relationships (addresses, warehouses, shipments)
- Transaction management for multiple related entities
- Business logic beyond simple CRUD operations

```
src/app/
├── api/v1/          # API endpoints
├── services/         # Business logic (added)
├── crud/             # CRUD operations (FastCRUD)
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic schemas
├── core/             # Configuration, DB, utilities
└── middleware/       # Logging, caching
```

## 📦 Entities

Three main entities from ShipEngine API:

1. **Address** — base entity for address information
2. **Warehouse** — warehouse with origin/return addresses
3. **Shipment** — shipment with warehouse and address references

**Simplifications:**
- Address: simplified structure, no real validation API integration
- Warehouse: basic fields only (name, addresses, default flag)
- Shipment: basic fields, simple status progression logic, no carrier API integration

## 🔧 Technology Stack

**Required:** Python 3.11+, FastAPI, SQLAlchemy 2.0, PostgreSQL, AsyncIO, asyncpg, ARQ

**Additional:** FastCRUD, Pydantic v2, Alembic, Redis, Uvicorn, structlog

## 🚀 Functionality

### CRUD Operations

**Warehouses:** `GET /api/v1/warehouses`, `POST`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}`

**Shipments:** `GET /api/v1/shipments` (paginated), `POST`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}`, `POST /{id}/update-tracking`

All create/update operations use transactions (`async with db.begin()`) for data integrity.

### Background Tasks (ARQ Worker)

Worker `update_shipment_tracking_status` implements status progression: `PENDING → PROCESSING → SHIPPED → IN_TRANSIT → DELIVERED`. Auto-schedules next update in 5 minutes (unless terminal status: `DELIVERED`, `CANCELLED`, `FAILED`).

**Note:** Worker implemented solely to demonstrate ARQ usage. In a real project, endpoints are simple enough and don't require background processing.

## 🧪 Testing

Tests cover:
- API endpoint `update_shipment_tracking` (success, errors, queue handling)
- Worker `update_shipment_tracking_status` (status progression, terminal states, error handling)

Run: `pytest tests/`

## 🔄 Data Flow

```
API Layer → Service Layer → CRUD Layer → Model Layer → Response
```

Example: `POST /api/v1/shipments` → validates warehouse → creates addresses → creates shipment (all in transaction) → enqueues background job

## 📊 Database

**Schema:**
- `address` (id, name, email, phone, address fields, country_code, timestamps)
- `warehouse` (id, name, is_default, origin_address_id, return_address_id, timestamps)
- `shipment` (id, warehouse_id, ship_to_id, ship_from_id, carrier, service_code, tracking_number, status, timestamps)

**Migrations:** `cd src && uv run alembic revision --autogenerate && uv run alembic upgrade head`

## 🚧 Production Requirements

1. **Rate Limiting** — connect existing infrastructure to endpoints
2. **Security/Authorization** — add JWT authentication, protect endpoints
3. **Tests** — integration tests, transaction tests, business logic tests, API tests
4. **Improvements** — address validation API, better error handling, structured logging, monitoring

## 🏃 Running

**Requirements:** Python 3.11+, PostgreSQL, Redis

**Local:**
```bash
uv sync
cp scripts/local_with_uvicorn/.env.example src/.env
docker compose up -d postgres redis
cd src && uv run alembic upgrade head
uv run uvicorn src.app.main:app --reload
# In separate terminal:
cd src && uv run python -m app.core.worker.settings
```

**Docker:** `docker compose up`

App: `http://localhost:8000`, Docs: `http://localhost:8000/docs`

## 📚 Resources

- [FastAPI Boilerplate Guide](https://benavlabs.github.io/FastAPI-boilerplate/user-guide/)
- [ShipEngine OpenAPI](https://shipengine.github.io/shipengine-openapi/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [ARQ Docs](https://arq-docs.helpmanual.io/)

## 📄 License

MIT
