# Design Rules & Architecture Guidelines

**Last Updated:** March 15, 2026
**Purpose:** Maintain consistency across API design, database patterns, and frontend UI.

---

## API Design Rules

### 1. Endpoint Naming Conventions
- **RESTful patterns:** Use plural nouns for collections (`/items`, `/boxes`)
- **Actions on collections:** `POST /items` (create), `GET /items` (list)
- **Actions on resources:** `GET /items/{id}`, `PUT /items/{id}`, `DELETE /items/{id}`
- **Special operations:** Use clear action verbs (`/upload`, `/export`, `/filters`)
- **Avoid:** Deep nesting beyond 2 levels (e.g., `/boxes/{id}/items/{id}/edit` ❌)

### 2. Request/Response Formats

#### Success Response Pattern
```json
{
  "success": true,
  "data": { ... },          // Single object
  "items": [ ... ],         // Array of objects
  "total": 100,             // For paginated lists
  "summary": { ... }        // For batch operations
}
```

#### Error Response Pattern
```json
{
  "error": true,
  "message": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": { ... }        // Optional: validation errors
}
```

### 3. Query Parameter Naming
- **Search:** `?search=keyword`
- **Filtering:** `?location=Truck1&category=Electrical`
- **Pagination:** `?limit=50&offset=0`
- **Sorting:** `?sort=name&order=asc` (if needed in future)

### 4. HTTP Status Codes
- `200 OK` - Successful GET, PUT
- `201 Created` - Successful POST (new resource)
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation errors
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Unexpected errors

### 5. Field Naming Conventions
- **Database columns:** `snake_case` (e.g., `box_id`, `created_at`)
- **JSON API fields:** `snake_case` (matches database, easier for Python)
- **Timestamps:** Always include `created_at` and `updated_at` (or `last_updated`)
- **IDs:** Use `UUID` for all primary keys, exposed as strings in API

---

## Database Design Rules

### 1. Table Naming
- **Plural nouns:** `boxes`, `items` (not `box`, `item`)
- **Lowercase:** Always lowercase table names
- **No prefixes:** Avoid `tbl_` or `app_` prefixes

### 2. Column Naming
- **snake_case:** All column names in snake_case
- **Descriptive:** `brand_platform` not `brand`, `dropbox_manual_url` not `url`
- **Foreign keys:** `{table}_id` (e.g., `box_id` references `boxes.id`)

### 3. Indexes
- **Foreign keys:** Always index foreign key columns
- **Search fields:** Index columns used in WHERE clauses (e.g., `name`, `category`)
- **Composite indexes:** Use for common filter combinations
- **Unique constraints:** Use composite unique for business logic (e.g., `UNIQUE (name, box_id)`)

### 4. Triggers
- **Auto-timestamps:** Use triggers for `last_updated` fields
- **Naming:** `trigger_{action}_{table}_{field}` (e.g., `trigger_update_items_last_updated`)

---

## Frontend UI Rules (TailwindCSS)

### 1. Color Palette
```css
/* Primary Colors (Tool Inventory Brand) */
--primary: #2563eb;      /* Blue 600 - primary actions */
--primary-hover: #1d4ed8; /* Blue 700 - hover state */

/* Status Colors */
--success: #10b981;      /* Green 500 - success states */
--warning: #f59e0b;      /* Amber 500 - low stock */
--error: #ef4444;        /* Red 500 - errors */
--info: #3b82f6;         /* Blue 500 - info messages */

/* Neutral Colors */
--gray-50: #f9fafb;      /* Background */
--gray-100: #f3f4f6;     /* Cards */
--gray-200: #e5e7eb;     /* Borders */
--gray-900: #111827;     /* Text */
```

### 2. Typography Scale
- **Page title:** `text-3xl font-bold` (30px)
- **Section heading:** `text-2xl font-semibold` (24px)
- **Card title:** `text-lg font-medium` (18px)
- **Body text:** `text-base` (16px)
- **Small text:** `text-sm` (14px)
- **Tiny text:** `text-xs` (12px)

### 3. Spacing Scale
- **Page padding:** `p-6` (24px) on desktop, `p-4` (16px) on mobile
- **Card padding:** `p-4` (16px)
- **Section gap:** `gap-6` (24px)
- **Element gap:** `gap-4` (16px)

### 4. Component Patterns

#### Button Styles
```html
<!-- Primary Button -->
<button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
  Button Text
</button>

<!-- Secondary Button -->
<button class="px-4 py-2 bg-gray-200 text-gray-900 rounded-lg hover:bg-gray-300 transition">
  Cancel
</button>

<!-- Danger Button -->
<button class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">
  Delete
</button>
```

#### Card Styles
```html
<div class="bg-white rounded-lg shadow p-4 border border-gray-200">
  <!-- Card content -->
</div>
```

#### Form Input Styles
```html
<input
  type="text"
  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
  placeholder="Enter item name"
>
```

### 5. Mobile Responsiveness Breakpoints
- **Mobile:** `< 768px` (default, mobile-first)
- **Tablet:** `md:` (>= 768px)
- **Desktop:** `lg:` (>= 1024px)

#### Responsive Patterns
```html
<!-- Stack on mobile, grid on desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <!-- Cards -->
</div>

<!-- Hide on mobile, show on desktop -->
<div class="hidden md:block">Desktop only</div>

<!-- Full width on mobile, max-width on desktop -->
<div class="w-full max-w-4xl mx-auto px-4">
  <!-- Content -->
</div>
```

### 6. Low Stock Highlighting
```html
<!-- Yellow background for low stock items -->
<tr class="bg-yellow-50 border-l-4 border-yellow-500">
  <td>Item below threshold</td>
</tr>
```

---

## File Organization Rules

### 1. FastAPI Project Structure
```
app/
├── __init__.py           # Empty or app factory
├── main.py              # FastAPI app entry point
├── config.py            # Environment variables, settings
├── models/              # Pydantic models (request/response schemas)
│   ├── __init__.py
│   ├── box.py
│   └── item.py
├── routes/              # API endpoint handlers
│   ├── __init__.py
│   ├── items.py
│   ├── boxes.py
│   ├── upload.py
│   ├── export.py
│   ├── images.py
│   ├── alexa.py
│   └── qr.py
├── services/            # Business logic, external integrations
│   ├── __init__.py
│   ├── db.py           # Supabase client, database operations
│   ├── csv_parser.py   # CSV parsing and merge logic
│   ├── qr_generator.py # QR code generation
│   ├── image_handler.py # Image upload, resize, storage
│   └── fuzzy_search.py # Alexa fuzzy matching
└── utils/              # Helper functions, validators
    ├── __init__.py
    ├── validators.py
    └── helpers.py
```

### 2. Import Rules
- **Absolute imports:** Use `from app.services.db import get_supabase_client`
- **Group imports:** Standard library → Third-party → Local
- **Avoid circular imports:** Use forward references or restructure

### 3. Logging
- **Use Python logging module:** Not print statements
- **Log levels:**
  - `DEBUG` - Detailed info for debugging
  - `INFO` - General operational events
  - `WARNING` - Unexpected but handled situations
  - `ERROR` - Errors that need attention

---

## Code Quality Rules

### 1. Type Hints
- **Always use type hints** in function signatures
- **Use Pydantic models** for request/response validation
- **Example:**
```python
from typing import List, Optional
from app.models.item import Item, ItemCreate

async def create_item(item: ItemCreate) -> Item:
    ...
```

### 2. Error Handling
- **Always validate input** (Pydantic handles this)
- **Use try-except** for database operations
- **Return consistent error responses**
- **Example:**
```python
from fastapi import HTTPException

try:
    result = await db_operation()
except Exception as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

### 3. Async/Await
- **Use async routes** for I/O-bound operations (database, file upload)
- **Use sync routes** only for CPU-bound operations
- **Example:**
```python
@router.get("/items")
async def get_items(search: Optional[str] = None):
    items = await db.fetch_items(search)
    return {"items": items}
```

### 4. Documentation
- **Docstrings:** Use Google-style docstrings for functions
- **API docs:** FastAPI auto-generates, but add `summary` and `description`
- **Example:**
```python
@router.post("/items", summary="Create new item")
async def create_item(item: ItemCreate):
    """
    Create a new inventory item.

    Args:
        item: Item data with required fields (name, category, quantity, box_id)

    Returns:
        Created item with generated ID and timestamps
    """
    ...
```

---

## Testing Rules

### 1. Test Structure
```
tests/
├── test_items.py       # Test /api/items endpoints
├── test_boxes.py       # Test /api/boxes endpoints
├── test_upload.py      # Test CSV upload and merge logic
├── test_export.py      # Test CSV export
└── conftest.py         # Pytest fixtures (test DB, mock data)
```

### 2. Test Naming
- **Pattern:** `test_{function}_{scenario}_{expected_result}`
- **Example:** `test_create_item_with_valid_data_returns_201`

### 3. Test Coverage Goals
- **Routes:** 80%+ coverage
- **Services:** 90%+ coverage (business logic is critical)
- **Models:** 100% (Pydantic models are simple)

---

## Git Commit Rules

### 1. Commit Message Format
```
<type>(<scope>): <subject>

<optional body>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `refactor` - Code refactoring
- `test` - Adding tests
- `chore` - Build, dependencies, tooling

**Examples:**
- `feat(api): add GET /api/items endpoint with search and filters`
- `fix(csv): handle empty optional fields in CSV parser`
- `docs(readme): update Phase 1 completion status`

### 2. Commit Frequency
- **Logical units:** Commit after completing a logical unit (e.g., one endpoint)
- **Working state:** Every commit should leave code in a working state
- **Avoid:** Massive commits with multiple features

---

## Security Rules

### 1. Environment Variables
- **Never commit `.env`** (add to `.gitignore`)
- **Use `.env.example`** for template
- **Validate on startup:** Fail fast if required vars are missing

### 2. Input Validation
- **Use Pydantic models** for all API inputs
- **Validate file uploads:** Check file type, size
- **Sanitize user input:** Prevent SQL injection (use parameterized queries)

### 3. CORS
- **Development:** Allow `localhost:*`
- **Production:** Whitelist specific domains only

---

## Performance Rules

### 1. Database Queries
- **Use indexes** for all filtered/searched fields
- **Avoid N+1 queries:** Use JOINs or batch fetches
- **Paginate large result sets:** Default limit 50, max 100

### 2. Image Handling
- **Resize on upload:** Max 1920px width
- **Compress:** Use JPEG quality 85% for photos
- **Max file size:** 5MB per image

### 3. API Response Times
- **Target:** < 200ms for GET requests, < 500ms for POST
- **Timeout:** Set reasonable timeouts for external services (Supabase)

---

## Change Log
- **2026-03-15:** Initial design rules created for Phase 1
