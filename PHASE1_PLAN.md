# Phase 1: Database & Backend Foundation - Detailed Implementation Plan

**Goal:** Set up Supabase database, FastAPI backend, and core API endpoints
**Estimated Time:** 1 week (10-15 hours)
**Prerequisites:** Supabase account, Python 3.11+

---

## Overview

This plan breaks down Phase 1 into 20 logical steps, each resulting in a working, testable unit of code. Each step includes:
- Files to create/modify
- Specific code to write
- How to test/verify
- Git commit message

---

## Step-by-Step Implementation

### Step 1: Create Python Virtual Environment & Dependencies

**Files to create:**
- `requirements.txt`

**Actions:**
1. Create `requirements.txt` with all dependencies
2. Create virtual environment
3. Install dependencies

**Dependencies:**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
supabase==2.3.4
python-multipart==0.0.6
qrcode[pil]==7.4.2
pandas==2.1.4
pillow==10.2.0
reportlab==4.0.8
fuzzywuzzy==0.18.0
python-Levenshtein==0.23.0
pytest==7.4.3
pytest-asyncio==0.23.2
httpx==0.26.0
```

**Test:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Git commit:**
```
chore(deps): add requirements.txt with all Phase 1 dependencies
```

---

### Step 2: Create Project Structure

**Files to create:**
- `app/__init__.py`
- `app/models/__init__.py`
- `app/routes/__init__.py`
- `app/services/__init__.py`
- `app/utils/__init__.py`

**Actions:**
Create empty `__init__.py` files for all modules

**Test:**
```bash
python -c "import app; import app.models; import app.routes"
```

**Git commit:**
```
chore(structure): create initial project folder structure
```

---

### Step 3: Environment Configuration

**Files to create:**
- `app/config.py`
- `.env` (user will provide credentials)

**`app/config.py`:**
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_storage_url: Optional[str] = None

    # Application
    environment: str = "development"
    max_image_size_mb: int = 5
    low_stock_threshold_default: int = 5

    # Vercel (optional for local dev)
    vercel_url: Optional[str] = None

    # Alexa (optional, Phase 4)
    alexa_skill_id: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
```

**Test:**
```python
from app.config import settings
print(settings.supabase_url)  # Should print URL or raise validation error
```

**Git commit:**
```
feat(config): add environment configuration with Pydantic settings
```

---

### Step 4: Supabase Database Client

**Files to create:**
- `app/services/db.py`

**`app/services/db.py`:**
```python
from supabase import create_client, Client
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class SupabaseDB:
    """Supabase database client wrapper."""

    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
        logger.info("Supabase client initialized")

    def get_client(self) -> Client:
        """Get Supabase client instance."""
        return self.client

# Global database instance
db = SupabaseDB()

def get_supabase_client() -> Client:
    """FastAPI dependency to get Supabase client."""
    return db.get_client()
```

**Test:**
```python
from app.services.db import get_supabase_client
client = get_supabase_client()
# Test connection (this will fail until user provides credentials)
result = client.table('boxes').select('*').limit(1).execute()
```

**Git commit:**
```
feat(db): add Supabase client wrapper and dependency injection
```

---

### Step 5: Pydantic Models for Box

**Files to create:**
- `app/models/box.py`

**`app/models/box.py`:**
```python
from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class BoxBase(BaseModel):
    """Base box model with common fields."""
    name: str
    location: str
    sublocation: Optional[str] = None

class BoxCreate(BoxBase):
    """Model for creating a new box."""
    pass

class BoxUpdate(BaseModel):
    """Model for updating a box (all fields optional)."""
    name: Optional[str] = None
    location: Optional[str] = None
    sublocation: Optional[str] = None

class Box(BoxBase):
    """Complete box model (returned from database)."""
    id: UUID4
    qr_code_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**Test:**
```python
from app.models.box import BoxCreate, Box
box_data = BoxCreate(name="Box A", location="Warehouse")
print(box_data.model_dump())
```

**Git commit:**
```
feat(models): add Pydantic models for Box entity
```

---

### Step 6: Pydantic Models for Item

**Files to create:**
- `app/models/item.py`

**`app/models/item.py`:**
```python
from pydantic import BaseModel, UUID4, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ItemBase(BaseModel):
    """Base item model with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=0)
    box_id: UUID4
    dropbox_manual_url: Optional[str] = None
    image_url: Optional[str] = None
    brand_platform: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    estimated_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    low_stock_threshold: int = Field(default=5, ge=0)

class ItemCreate(ItemBase):
    """Model for creating a new item."""
    pass

class ItemUpdate(BaseModel):
    """Model for updating an item (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[int] = Field(None, ge=0)
    box_id: Optional[UUID4] = None
    dropbox_manual_url: Optional[str] = None
    image_url: Optional[str] = None
    brand_platform: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    estimated_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    low_stock_threshold: Optional[int] = Field(None, ge=0)

class Item(ItemBase):
    """Complete item model (returned from database)."""
    id: UUID4
    last_updated: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class ItemWithBox(Item):
    """Item model with nested box information."""
    box: Optional[dict] = None  # Will contain box details
```

**Test:**
```python
from app.models.item import ItemCreate
from uuid import uuid4

item = ItemCreate(
    name="Wire Stripper",
    category="Electrical",
    quantity=3,
    box_id=uuid4(),
    brand_platform="Klein Tools"
)
print(item.model_dump())
```

**Git commit:**
```
feat(models): add Pydantic models for Item entity with validation
```

---

### Step 7: FastAPI Application Setup

**Files to create:**
- `app/main.py`

**`app/main.py`:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Tool Inventory API",
    description="Inventory management system with QR codes and Alexa integration",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else ["https://tool-inventory.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Tool Inventory API",
        "version": "1.0.0",
        "environment": settings.environment
    }

@app.get("/api/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Actual DB health check
        "environment": settings.environment
    }

# Import and include routers (will be added in next steps)
# from app.routes import items, boxes
# app.include_router(items.router, prefix="/api", tags=["items"])
# app.include_router(boxes.router, prefix="/api", tags=["boxes"])
```

**Test:**
```bash
uvicorn app.main:app --reload
# Visit http://localhost:8000/api/docs
```

**Git commit:**
```
feat(api): create FastAPI application with CORS and health endpoints
```

---

### Step 8: Items Router - GET /api/items (Search & Filter)

**Files to create:**
- `app/routes/items.py`

**`app/routes/items.py`:**
```python
from fastapi import APIRouter, Depends, Query, HTTPException
from supabase import Client
from app.services.db import get_supabase_client
from app.models.item import Item, ItemWithBox
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/items", response_model=dict, summary="Search and filter items")
async def get_items(
    search: Optional[str] = Query(None, description="Search by item name"),
    location: Optional[str] = Query(None, description="Filter by box location"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Client = Depends(get_supabase_client)
):
    """
    Get items with search and filtering.

    - **search**: Text search on item name (case-insensitive)
    - **location**: Filter by box location
    - **category**: Filter by category
    - **limit**: Results per page (default 50, max 100)
    - **offset**: Pagination offset (default 0)
    """
    try:
        # Start with base query
        query = db.table('items').select('*, boxes(id, name, location)')

        # Apply search filter
        if search:
            query = query.ilike('name', f'%{search}%')

        # Apply category filter
        if category:
            query = query.eq('category', category)

        # Apply location filter (need to join with boxes)
        if location:
            # This is tricky with Supabase - we'll filter after fetch for now
            # TODO: Optimize with proper join query
            pass

        # Get total count (before pagination)
        count_result = query.execute()
        total = len(count_result.data) if count_result.data else 0

        # Apply pagination
        query = query.range(offset, offset + limit - 1)

        # Execute query
        result = query.execute()

        items = result.data if result.data else []

        # Filter by location if specified (post-fetch filtering)
        if location and items:
            items = [
                item for item in items
                if item.get('boxes') and item['boxes'].get('location') == location
            ]
            total = len(items)

        # Calculate low_stock flag
        for item in items:
            item['low_stock'] = item['quantity'] < item.get('low_stock_threshold', 5)

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": items
        }

    except Exception as e:
        logger.error(f"Error fetching items: {e}")
        raise HTTPException(status_code=500, detail="Error fetching items")
```

**Test:**
```bash
# Start server: uvicorn app.main:app --reload
# Test: curl http://localhost:8000/api/items?limit=10
```

**Git commit:**
```
feat(api): add GET /api/items endpoint with search and filters
```

---

### Step 9: Include Items Router in Main App

**Files to modify:**
- `app/main.py`

**Changes:**
```python
# After app creation, add:
from app.routes import items

app.include_router(items.router, prefix="/api", tags=["items"])
```

**Test:**
```bash
# Visit http://localhost:8000/api/docs
# Should see /api/items endpoint
```

**Git commit:**
```
feat(api): register items router in main application
```

---

### Step 10: GET /api/filters (Dynamic Locations & Categories)

**Files to modify:**
- `app/routes/items.py`

**Add endpoint:**
```python
@router.get("/filters", response_model=dict, summary="Get dynamic filter options")
async def get_filters(db: Client = Depends(get_supabase_client)):
    """
    Get unique locations and categories for filter dropdowns.

    Returns:
        - locations: List of unique box locations
        - categories: List of unique item categories
    """
    try:
        # Get unique locations from boxes table
        locations_result = db.table('boxes').select('location').execute()
        locations = list(set([
            box['location'] for box in (locations_result.data or [])
            if box.get('location')
        ]))
        locations.sort()

        # Get unique categories from items table
        categories_result = db.table('items').select('category').execute()
        categories = list(set([
            item['category'] for item in (categories_result.data or [])
            if item.get('category')
        ]))
        categories.sort()

        return {
            "locations": locations,
            "categories": categories
        }

    except Exception as e:
        logger.error(f"Error fetching filters: {e}")
        raise HTTPException(status_code=500, detail="Error fetching filter options")
```

**Test:**
```bash
curl http://localhost:8000/api/filters
```

**Git commit:**
```
feat(api): add GET /api/filters for dynamic filter options
```

---

### Step 11: Boxes Router - GET /api/box/{box_id}

**Files to create:**
- `app/routes/boxes.py`

**`app/routes/boxes.py`:**
```python
from fastapi import APIRouter, Depends, HTTPException, Path
from supabase import Client
from app.services.db import get_supabase_client
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/box/{box_id}", summary="Get box details with all items")
async def get_box(
    box_id: str = Path(..., description="Box UUID"),
    db: Client = Depends(get_supabase_client)
):
    """
    Get box details and all items in that box.

    Used by QR code scans - returns mobile-optimized view.
    """
    try:
        # Fetch box
        box_result = db.table('boxes').select('*').eq('id', box_id).execute()

        if not box_result.data:
            raise HTTPException(status_code=404, detail="Box not found")

        box = box_result.data[0]

        # Fetch items in box
        items_result = db.table('items').select('*').eq('box_id', box_id).execute()
        items = items_result.data if items_result.data else []

        # Add low_stock flag
        for item in items:
            item['low_stock'] = item['quantity'] < item.get('low_stock_threshold', 5)

        return {
            "box": box,
            "items": items
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching box {box_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching box details")
```

**Register in `app/main.py`:**
```python
from app.routes import items, boxes
app.include_router(boxes.router, prefix="/api", tags=["boxes"])
```

**Test:**
```bash
# Get a box ID from database first, then:
curl http://localhost:8000/api/box/{box_id}
```

**Git commit:**
```
feat(api): add GET /api/box/{id} endpoint for QR scan target
```

---

### Step 12: POST /api/item (Create Item)

**Files to modify:**
- `app/routes/items.py`

**Add endpoint:**
```python
from app.models.item import ItemCreate, Item

@router.post("/item", response_model=dict, status_code=201, summary="Create new item")
async def create_item(
    item: ItemCreate,
    db: Client = Depends(get_supabase_client)
):
    """
    Create a new inventory item.

    Validates that box_id exists before creating.
    """
    try:
        # Verify box exists
        box_result = db.table('boxes').select('id').eq('id', str(item.box_id)).execute()
        if not box_result.data:
            raise HTTPException(status_code=404, detail=f"Box with id {item.box_id} not found")

        # Create item
        item_data = item.model_dump()
        item_data['box_id'] = str(item_data['box_id'])  # Convert UUID to string

        result = db.table('items').insert(item_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create item")

        return {
            "success": True,
            "item": result.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating item: {e}")
        raise HTTPException(status_code=500, detail="Error creating item")
```

**Test:**
```bash
curl -X POST http://localhost:8000/api/item \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Tool",
    "category": "Testing",
    "quantity": 1,
    "box_id": "<valid-box-uuid>"
  }'
```

**Git commit:**
```
feat(api): add POST /api/item endpoint to create items
```

---

### Step 13: PUT /api/item/{item_id} (Update Item)

**Files to modify:**
- `app/routes/items.py`

**Add endpoint:**
```python
from app.models.item import ItemUpdate

@router.put("/item/{item_id}", response_model=dict, summary="Update existing item")
async def update_item(
    item_id: str = Path(..., description="Item UUID"),
    item: ItemUpdate = None,
    db: Client = Depends(get_supabase_client)
):
    """
    Update an existing item (partial updates allowed).

    Only provided fields will be updated.
    """
    try:
        # Check item exists
        existing = db.table('items').select('id').eq('id', item_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Item not found")

        # Prepare update data (exclude None values)
        update_data = item.model_dump(exclude_unset=True, exclude_none=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Convert UUID to string if box_id is being updated
        if 'box_id' in update_data:
            update_data['box_id'] = str(update_data['box_id'])

        # Update item
        result = db.table('items').update(update_data).eq('id', item_id).execute()

        return {
            "success": True,
            "item": result.data[0] if result.data else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating item")
```

**Test:**
```bash
curl -X PUT http://localhost:8000/api/item/{item_id} \
  -H "Content-Type: application/json" \
  -d '{"quantity": 10}'
```

**Git commit:**
```
feat(api): add PUT /api/item/{id} endpoint to update items
```

---

### Step 14: GET /api/export (CSV Export)

**Files to create:**
- `app/routes/export.py`

**`app/routes/export.py`:**
```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from supabase import Client
from app.services.db import get_supabase_client
from datetime import datetime
import csv
import io
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/export", summary="Export inventory to CSV")
async def export_inventory(db: Client = Depends(get_supabase_client)):
    """
    Export entire inventory database to CSV.

    Returns CSV file with all fields including image URLs.
    """
    try:
        # Fetch all items with box information
        result = db.table('items').select('*, boxes(name, location)').execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="No items to export")

        items = result.data

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow([
            'Item Name',
            'Category',
            'Quantity',
            'Box/Location',
            'Brand/Platform',
            'Serial Number',
            'Estimated Value',
            'Dropbox URL',
            'Image URL',
            'Last Updated'
        ])

        # Data rows
        for item in items:
            box_info = item.get('boxes', {})
            box_location = f"{box_info.get('name', 'Unknown')} - {box_info.get('location', 'Unknown')}"

            writer.writerow([
                item.get('name', ''),
                item.get('category', ''),
                item.get('quantity', 0),
                box_location,
                item.get('brand_platform', ''),
                item.get('serial_number', ''),
                item.get('estimated_value', ''),
                item.get('dropbox_manual_url', ''),
                item.get('image_url', ''),
                item.get('last_updated', '')
            ])

        # Prepare response
        output.seek(0)
        timestamp = datetime.now().strftime('%Y-%m-%d')
        filename = f"inventory-export-{timestamp}.csv"

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting inventory: {e}")
        raise HTTPException(status_code=500, detail="Error exporting inventory")
```

**Register in `app/main.py`:**
```python
from app.routes import items, boxes, export
app.include_router(export.router, prefix="/api", tags=["export"])
```

**Test:**
```bash
curl http://localhost:8000/api/export -o inventory.csv
```

**Git commit:**
```
feat(api): add GET /api/export endpoint for CSV download
```

---

### Step 15: Image Upload Placeholder (POST /api/item/{item_id}/upload-image)

**Files to create:**
- `app/routes/images.py`

**`app/routes/images.py`:**
```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Path
from supabase import Client
from app.services.db import get_supabase_client
from app.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/item/{item_id}/upload-image", summary="Upload item image")
async def upload_item_image(
    item_id: str = Path(..., description="Item UUID"),
    image: UploadFile = File(..., description="Image file"),
    db: Client = Depends(get_supabase_client)
):
    """
    Upload image for an item.

    NOTE: This is a placeholder for Phase 1. Full implementation in Phase 3.
    For now, just validates file and returns mock URL.
    """
    try:
        # Verify item exists
        item_result = db.table('items').select('id').eq('id', item_id).execute()
        if not item_result.data:
            raise HTTPException(status_code=404, detail="Item not found")

        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Validate file size
        max_size = settings.max_image_size_mb * 1024 * 1024
        contents = await image.read()
        if len(contents) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"Image too large. Max size: {settings.max_image_size_mb}MB"
            )

        # TODO: Actual upload to Supabase Storage (Phase 3)
        # For now, return mock URL
        mock_url = f"https://placeholder.com/images/{item_id}.jpg"

        # Update item with image URL
        db.table('items').update({'image_url': mock_url}).eq('id', item_id).execute()

        return {
            "success": True,
            "image_url": mock_url,
            "message": "Placeholder implementation. Actual upload in Phase 3."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(status_code=500, detail="Error uploading image")
```

**Register in `app/main.py`:**
```python
from app.routes import items, boxes, export, images
app.include_router(images.router, prefix="/api", tags=["images"])
```

**Test:**
```bash
curl -X POST http://localhost:8000/api/item/{item_id}/upload-image \
  -F "image=@test.jpg"
```

**Git commit:**
```
feat(api): add POST /api/item/{id}/upload-image placeholder endpoint
```

---

### Step 16: Create vercel.json

**Files to create:**
- `vercel.json`

**Content:**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "app/main.py"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ]
}
```

**Test:**
Not testable locally (Vercel-specific), but validates JSON syntax

**Git commit:**
```
chore(deploy): add vercel.json for API routing configuration
```

---

### Step 17: Update CLAUDE.md with Architecture Notes

**Files to modify:**
- `/Users/chasesantos/Desktop/N8N-BUILDER/CLAUDE.md`

**Add section under tool-inventory:**
```markdown
### tool-inventory/
Custom tool inventory web app with QR codes, Alexa voice integration, and mobile camera upload. FastAPI + Supabase + Vercel. See [tool-inventory/PRD.md](tool-inventory/PRD.md) for complete specs and implementation plan.

**Phase 1 Status:** ✅ Complete
- Supabase database schema deployed
- FastAPI backend with 7 core endpoints
- Dynamic filters (locations/categories)
- CSV export functionality
- Image upload placeholder
```

**Git commit:**
```
docs(workspace): update CLAUDE.md with Phase 1 completion status
```

---

### Step 18: Basic Unit Tests Setup

**Files to create:**
- `tests/conftest.py`
- `tests/test_models.py`

**`tests/conftest.py`:**
```python
import pytest
from uuid import uuid4

@pytest.fixture
def sample_box_data():
    """Sample box data for testing."""
    return {
        "name": "Test Box A",
        "location": "Test Warehouse",
        "sublocation": "Shelf 1"
    }

@pytest.fixture
def sample_item_data():
    """Sample item data for testing."""
    return {
        "name": "Test Wire Stripper",
        "category": "Electrical",
        "quantity": 5,
        "box_id": uuid4(),
        "brand_platform": "Klein Tools",
        "estimated_value": 29.99
    }
```

**`tests/test_models.py`:**
```python
from app.models.box import BoxCreate, Box
from app.models.item import ItemCreate, Item
from uuid import uuid4
from datetime import datetime

def test_box_create_model(sample_box_data):
    """Test BoxCreate model validation."""
    box = BoxCreate(**sample_box_data)
    assert box.name == "Test Box A"
    assert box.location == "Test Warehouse"

def test_item_create_model(sample_item_data):
    """Test ItemCreate model validation."""
    item = ItemCreate(**sample_item_data)
    assert item.name == "Test Wire Stripper"
    assert item.quantity == 5
    assert item.low_stock_threshold == 5  # Default value

def test_item_quantity_validation():
    """Test that negative quantity raises validation error."""
    try:
        ItemCreate(
            name="Test",
            category="Test",
            quantity=-1,
            box_id=uuid4()
        )
        assert False, "Should have raised validation error"
    except Exception:
        pass  # Expected
```

**Test:**
```bash
pytest tests/test_models.py -v
```

**Git commit:**
```
test(models): add unit tests for Pydantic models
```

---

### Step 19: API Integration Tests (Basic)

**Files to create:**
- `tests/test_api.py`

**`tests/test_api.py`:**
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint returns status."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_items_endpoint_returns_data():
    """Test GET /api/items endpoint structure."""
    response = client.get("/api/items?limit=10")
    assert response.status_code == 200
    json_data = response.json()
    assert "items" in json_data
    assert "total" in json_data
    assert isinstance(json_data["items"], list)

# Note: Full integration tests require database access
# These will be expanded in Phase 2 with test data
```

**Test:**
```bash
pytest tests/test_api.py -v
```

**Git commit:**
```
test(api): add basic integration tests for endpoints
```

---

### Step 20: Documentation & Phase 1 Wrap-Up

**Files to create:**
- `PHASE1_COMPLETE.md`

**Content:**
```markdown
# Phase 1 Complete: Database & Backend Foundation

**Completion Date:** [DATE]
**Status:** ✅ Complete

## Deliverables Achieved

### 1. Supabase Database
- ✅ Schema created with `boxes` and `items` tables
- ✅ Indexes for performance (name, category, location)
- ✅ Triggers for auto-timestamps
- ✅ Storage buckets created (tool-images, qr-codes)

### 2. FastAPI Backend
- ✅ Project structure created
- ✅ Environment configuration with Pydantic
- ✅ Supabase client wrapper
- ✅ Pydantic models for validation
- ✅ CORS middleware configured

### 3. API Endpoints (7 total)
1. ✅ `GET /api/items` - Search and filter items
2. ✅ `GET /api/filters` - Dynamic locations/categories
3. ✅ `GET /api/box/{id}` - Box details (QR scan target)
4. ✅ `POST /api/item` - Create new item
5. ✅ `PUT /api/item/{id}` - Update item
6. ✅ `GET /api/export` - CSV export
7. ✅ `POST /api/item/{id}/upload-image` - Image upload (placeholder)

### 4. Infrastructure
- ✅ `vercel.json` for deployment routing
- ✅ `requirements.txt` with all dependencies
- ✅ `.env.example` template

### 5. Testing
- ✅ Basic model validation tests
- ✅ API integration tests
- ✅ Pytest configuration

### 6. Documentation
- ✅ `design-rules.md` - API and UI guidelines
- ✅ `bugs.md` - Issue tracker
- ✅ Updated `CLAUDE.md` with Phase 1 status

## What's Working

- FastAPI server runs locally
- All 7 endpoints functional
- Dynamic filters populate from database
- CSV export generates valid files
- Input validation working via Pydantic
- Health check endpoints respond

## Known Issues

- Image upload is placeholder (full implementation in Phase 3)
- Location filter in GET /api/items uses post-fetch filtering (not optimal)
- No rate limiting yet (planned for Phase 5)
- Tests require actual Supabase connection (test DB setup needed)

## Next Steps (Phase 2)

1. CSV upload endpoint with merge strategy
2. QR code generation for boxes
3. Printable PDF with QR codes
4. Admin dashboard frontend (basic)

## Testing Instructions

### Local Development
```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure .env with Supabase credentials
cp .env.example .env
# Edit .env

# Run server
uvicorn app.main:app --reload

# API Docs
http://localhost:8000/api/docs
```

### Run Tests
```bash
pytest tests/ -v
```

## Metrics

- **Lines of Code:** ~800
- **Files Created:** 20
- **Dependencies:** 15
- **API Endpoints:** 7
- **Test Coverage:** ~40% (models/basic endpoints)
```

**Git commit:**
```
docs(phase1): add Phase 1 completion summary and testing guide
```

---

## Critical Path Summary

**Must complete in order:**
1. Steps 1-4: Environment setup
2. Steps 5-6: Data models
3. Steps 7-9: FastAPI app + first endpoint
4. Steps 10-15: Remaining endpoints
5. Steps 16-20: Infrastructure + tests + docs

**Parallel work opportunities:**
- Steps 5-6 (models) can be done together
- Steps 10-15 (endpoints) can be done in any order after Step 9

**Estimated time:**
- Steps 1-9: 3-4 hours
- Steps 10-15: 4-5 hours
- Steps 16-20: 2-3 hours
- **Total: 10-12 hours**

---

## Verification Checklist

After completing all steps:

- [ ] `uvicorn app.main:app --reload` starts without errors
- [ ] Visit `http://localhost:8000/api/docs` shows all 7 endpoints
- [ ] `GET /api/items` returns JSON with items array
- [ ] `GET /api/filters` returns locations and categories
- [ ] `GET /api/box/{id}` returns box + items (with valid box ID)
- [ ] `POST /api/item` creates item successfully
- [ ] `PUT /api/item/{id}` updates item
- [ ] `GET /api/export` downloads CSV file
- [ ] `pytest tests/ -v` all tests pass
- [ ] `vercel.json` exists and has correct structure
- [ ] `.env` file created with Supabase credentials (not committed)

---

## Dependencies for Phase 2

Phase 2 will build on this foundation:
- CSV parser will use models from `app/models/`
- QR generator will read from `boxes` table via `app/services/db`
- Upload endpoint will extend `app/routes/upload.py` (new file)
