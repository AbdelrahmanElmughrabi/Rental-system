# API v1 Design Spec

## Inventory

### Model: Item (proposed)
- id: integer (auto)
- name: string (required, max 120)
- sku: string (required, unique, max 64)
- description: text (optional)
- price: decimal(10,2) (required)
- quantity: integer (required, default 0)
- is_active: boolean (default true)
- created_at: datetime (auto)
- updated_at: datetime (auto)

### Endpoints
- GET /api/v1/items/
  - Query: `search` (name/sku), `page`, `page_size`, `is_active`
  - 200: `{ count, next, previous, results: [Item] }`
- POST /api/v1/items/
  - Body: `{ name, sku, description?, price, quantity?, is_active? }`
  - 201: `Item`
- GET /api/v1/items/{id}/
  - 200: `Item`
- PATCH /api/v1/items/{id}/
  - Body: partial fields
  - 200: `Item`
- DELETE /api/v1/items/{id}/
  - 204

### Errors
- 400: validation errors
- 404: not found

### Notes
- Business logic in `inventory/services.py`
- Read queries in `inventory/selectors.py`
- Serializers/Views live under `api/v1/serializers` and `api/v1/views`

---

## Rentals

### Model: Rental (proposed)
- id: integer (auto)
- item: FK -> Item (required)
- customer_name: string (required, max 120)
- rented_at: datetime (auto_now_add)
- due_date: date (required)
- returned_at: datetime (nullable)
- status: string (choices: `active`, `returned`, `overdue`) default `active`

### Endpoints
- POST /api/v1/rentals/
  - Body: `{ item_id, customer_name, due_date }`
  - 201: `Rental`
- GET /api/v1/rentals/
  - Query: `status`, `item_id`, `date_from`, `date_to`, `page`
  - 200: paginated list of `Rental`
- GET /api/v1/rentals/{id}/
  - 200: `Rental`
- POST /api/v1/rentals/{id}/return/
  - Body: `{ returned_at? }` (optional; default now)
  - 200: `Rental` with updated status/returned_at

### Errors
- 400: invalid transitions (e.g., returning an already returned rental)
- 404: not found
- 409: insufficient inventory (`quantity` < 1)

### Notes
- `RentalService.create_rental(item_id, customer_name, due_date)` reduces item quantity atomically.
- `RentalService.return_rental(rental_id, returned_at=None)` increments item quantity and sets status.

---

## Auth & Permissions (v1 minimal)
- Default `AllowAny` for now; tighten later.
- `whoami` exists for session verification.

## Pagination
- Use `core.pagination.DefaultPagination` with `page_size` and `page_size_query_param`. 