# Parcel Tracking Service

Backend service for parcel registration, tracking, and status management, built with Django and Django REST Framework.

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

## Installation and Setup

### 1. Clone repository

```bash
git clone https://github.com/bayur-yuliya/parcel_tracking_service
cd parcel_tracking_service
```

### 2. Create .env file

### 3. Build and run containers

```bash
docker-compose up --build
```
### 4. Load seed data

```bash
docker-compose exec web python manage.py create_info
```

### 5. Create superuser (optional)

```bash
docker-compose exec web python manage.py createsuperuser
```


---

## API Endpoints

### 1. Create parcel

POST `/api/parcels/`

```json
{
  "sender": 1,
  "recipient": 2,
  "weight": "5.50",
  "declared_value": "1000.00",
  "origin_office": "UUID",
  "destination_office": "UUID"
}
```

---

### 2. Get parcel details

GET `/api/parcels/{tracking_number}/`

---

### 3. Update parcel status

POST `/api/parcels/{tracking_number}/status/`

```json
{
  "status": "accepted",
  "office_id": "UUID",
  "comment": "Parcel accepted at office"
}
```

---

### 4. Get parcels in a specific office

Responses are paginated:

{
  "count": 10,
  "next": "...",
  "previous": "...",
  "results": [...]
}

GET `/api/offices/{id}/parcels/`

---

### 5. Filter parcels

GET `/api/parcels/?status=in_transit&from_city=Kyiv`

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

## API Documentation (Swagger)

Available at:

```
/api/schema/swagger-ui/
```

## What Docker does

### PostgreSQL service (db)
- PostgreSQL 15
- Persistent volume: postgres_data
- Port: 5432

### Django service (web)
- Builds from Dockerfile
- Workdir:
  ```
  /app/parcel_tracking_service
  ```

---

## Logging

* `audit.log` — records business actions
* `errors.log` — records system errors

---

## Implementation Notes

* Status updates are wrapped in `transaction.atomic()`
* `select_for_update()` is used to prevent race conditions
* Each status change creates a history record
* Model-level validation is enforced via `clean()` and database constraints

