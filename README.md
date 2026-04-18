# Parcel Tracking Service

Backend service for parcel registration, tracking, and status management, built with Django and Django REST Framework.

---

## Quick Start (Recommended)

```bash
git clone https://github.com/bayur-yuliya/parcel_tracking_service
cd parcel_tracking_service
cp .env.example .env
```

Edit `.env` if needed (DB credentials, etc.)

```bash
docker-compose up --build
```

### Load initial data

```bash
docker-compose exec web python manage.py create_info
```

### Create superuser (optional)

```bash
docker-compose exec web python manage.py createsuperuser
```

App will be available at:

```
http://localhost:8000
```

Swagger:

```
http://localhost:8000/api/schema/swagger-ui/
```

---

## Authentication

This project uses **Token Authentication**.

### Get token

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password"
}'
```

Response:

```json
{
  "token": "your_token_here",
  "username": "admin"
}
```

### Use token in requests

```bash
Authorization: Token your_token_here
```

❗ Not `Bearer`, but `Token`

---

## API Usage Examples (curl)

### Create parcel

```bash
curl -X POST http://localhost:8000/api/parcels/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your_token_here" \
  -d '{
    "sender": 1,
    "recipient": 2,
    "weight": "2.50",
    "declared_value": "1000.00",
    "origin_office": "uuid-origin",
    "destination_office": "uuid-destination"
}'
```

---

### Get parcel details

```bash
curl -X GET http://localhost:8000/api/parcels/ABC123456789/
```

---

### List parcels (with filters)

```bash
curl -X GET "http://localhost:8000/api/parcels/?status=in_transit&page=1" \
  -H "Authorization: Token your_token_here"
```

---

### Update parcel status

```bash
curl -X POST http://localhost:8000/api/parcels/ABC123456789/status/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your_token_here" \
  -d '{
    "status": "in_transit",
    "office_id": "uuid-office",
    "comment": "Sent from warehouse"
}'
```

---

### Get parcels in office

```bash
curl -X GET http://localhost:8000/api/offices/uuid-office/parcels/ \
  -H "Authorization: Token your_token_here"
```

Response is paginated:

```json
{
  "count": 10,
  "next": "...",
  "previous": "...",
  "results": []
}
```

---

## Functionality

* Create parcels with automatically generated tracking numbers
* Track parcels by tracking number
* Update parcel statuses with validation
* Store full status change history
* Filter and paginate parcel list
* Logging of system actions and errors

---

## Technology Stack

* Python 3.11+
* Django
* Django REST Framework
* PostgreSQL
* Docker

---

## Parcel Statuses

| Status     | Description               |
| ---------- | ------------------------- |
| created    | Parcel created            |
| accepted   | Accepted at origin office |
| in_transit | In transit                |
| arrived    | Arrived at destination    |
| delivered  | Delivered (final)         |
| returned   | Returned (final)          |

---

## Business Rules

* A parcel cannot be marked as delivered unless it has arrived at the destination office
* Final statuses (`delivered`, `returned`) cannot be changed
* Weight must be between 0.01 and 30 kg
* Declared value must be greater than or equal to 0
* Sender and recipient must be different
* Origin and destination offices must be different

---

## Docker Services

### PostgreSQL (db)

* PostgreSQL 15
* Volume: `postgres_data`
* Port: 5432

### Django (web)

* Built from Dockerfile
* Working directory:

  ```
  /app/parcel_tracking_service
  ```

---

## Logging

* `audit.log` — business actions
* `errors.log` — system errors

---

## Implementation Notes

* Status updates use `transaction.atomic()`
* `select_for_update()` prevents race conditions
* Each status change is stored in history
* Validation enforced at model and DB level

---

## Important Notes

* UUID fields must contain real values from DB
* Most endpoints require authentication + employee role
* Public endpoint:

  * `GET /api/parcels/{tracking_number}/`

---

## Example Workflow

1. Create users and offices via seed command
2. Get auth token
3. Create parcel
4. Update status through lifecycle
5. Track parcel via public endpoint

---
