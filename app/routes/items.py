from fastapi import APIRouter, Depends, Query, HTTPException, Path
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from supabase import Client
from app.services.db import get_supabase_client
from app.models.item import ItemUpdate
from app.utils.helpers import serialize_for_supabase
from typing import Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ItemCreateRequest(BaseModel):
    """Request model for creating items via the UI form (uses container_name + location)."""
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=0)
    container_name: str = Field(..., min_length=1, max_length=255)
    location: str = Field(..., min_length=1, max_length=100)
    dropbox_manual_url: Optional[str] = None
    image_url: Optional[str] = None
    brand_platform: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    estimated_value: Optional[Decimal] = Field(None, ge=0)
    low_stock_threshold: int = Field(default=0, ge=0)
    bought_on: Optional[str] = None
    bought_from: Optional[str] = Field(None, max_length=255)


@router.get("/items", summary="Search and filter items")
async def get_items(
    search: Optional[str] = Query(None, description="Search by item name"),
    location: Optional[str] = Query(None, description="Filter by box location"),
    container: Optional[str] = Query(None, description="Filter by container name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Client = Depends(get_supabase_client)
):
    """
    Get items with search and filtering.

    - **search**: Text search on item name (case-insensitive)
    - **location**: Filter by box location
    - **container**: Filter by container name (box name)
    - **category**: Filter by category
    """
    try:
        query = db.table('items').select('*, boxes(id, name, location)')

        if search:
            query = query.ilike('name', f'%{search}%')
        if category:
            query = query.eq('category', category)
        if location:
            query = query.eq('boxes.location', location)
        if container:
            query = query.eq('boxes.name', container)

        # Apply pagination
        query = query.range(offset, offset + limit - 1)
        result = query.execute()
        items = result.data if result.data else []

        # PostgREST returns rows with boxes=null when foreign filter doesn't match
        # Filter those out server-side
        if location or container:
            items = [item for item in items if item.get('boxes') is not None]

        # Get accurate total count (not just page count)
        count_query = db.table('items').select('id', count='exact')
        if search:
            count_query = count_query.ilike('name', f'%{search}%')
        if category:
            count_query = count_query.eq('category', category)
        count_result = count_query.execute()
        total = count_result.count if count_result.count is not None else len(items)

        for item in items:
            threshold = item.get('low_stock_threshold', 0)
            item['low_stock'] = threshold > 0 and item['quantity'] < threshold

        return jsonable_encoder({
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": items
        })

    except Exception as e:
        logger.error(f"Error fetching items: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching items: {str(e)}")


@router.get("/filters", summary="Get dynamic filter options")
async def get_filters(db: Client = Depends(get_supabase_client)):
    """
    Get unique locations, containers, and categories for filter dropdowns.
    """
    try:
        # Get unique locations from boxes table
        locations_result = db.table('boxes').select('location').execute()
        locations = sorted(set(
            box['location'] for box in (locations_result.data or [])
            if box.get('location')
        ))

        # Get unique container names from boxes table
        containers_result = db.table('boxes').select('name').execute()
        containers = sorted(set(
            box['name'] for box in (containers_result.data or [])
            if box.get('name')
        ))

        # Get unique categories from items table
        categories_result = db.table('items').select('category').execute()
        categories = sorted(set(
            item['category'] for item in (categories_result.data or [])
            if item.get('category')
        ))

        # Get unique stores (bought_from) from items table
        stores_result = db.table('items').select('bought_from').execute()
        stores = sorted(set(
            item['bought_from'] for item in (stores_result.data or [])
            if item.get('bought_from')
        ))

        return {
            "success": True,
            "data": {
                "locations": locations,
                "containers": containers,
                "categories": categories,
                "stores": stores
            }
        }

    except Exception as e:
        logger.error(f"Error fetching filters: {e}")
        raise HTTPException(status_code=500, detail="Error fetching filter options")


@router.get("/item/{item_id}", summary="Get single item by ID")
async def get_item(
    item_id: str = Path(..., description="Item UUID"),
    db: Client = Depends(get_supabase_client)
):
    """Get a single item by its UUID, including its box details."""
    try:
        result = db.table('items').select('*, boxes(id, name, location)').eq('id', item_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Item not found")

        item = result.data[0]
        threshold = item.get('low_stock_threshold', 0)
        item['low_stock'] = threshold > 0 and item['quantity'] < threshold

        return jsonable_encoder({
            "success": True,
            "data": item
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching item: {str(e)}")


@router.post("/item", status_code=201, summary="Create new item")
async def create_item(
    item: ItemCreateRequest,
    db: Client = Depends(get_supabase_client)
):
    """
    Create a new inventory item.

    Accepts container_name + location, looks up or creates the box automatically.
    """
    try:
        # Look up or create the box
        box_id = await _get_or_create_box(db, item.container_name, item.location)

        # Prepare item data
        item_data = {
            'name': item.name,
            'category': item.category,
            'quantity': item.quantity,
            'box_id': str(box_id),
            'dropbox_manual_url': item.dropbox_manual_url,
            'image_url': item.image_url,
            'brand_platform': item.brand_platform,
            'serial_number': item.serial_number,
            'estimated_value': float(item.estimated_value) if item.estimated_value else None,
            'low_stock_threshold': item.low_stock_threshold,
            'bought_on': item.bought_on,
            'bought_from': item.bought_from,
        }

        result = db.table('items').insert(item_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create item")

        return jsonable_encoder({
            "success": True,
            "data": result.data[0]
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating item: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating item: {str(e)}")


@router.put("/item/{item_id}", summary="Update existing item")
async def update_item(
    item_id: str = Path(..., description="Item UUID"),
    item: ItemUpdate = None,
    db: Client = Depends(get_supabase_client)
):
    """
    Update an existing item (partial updates allowed).
    """
    try:
        existing = db.table('items').select('id').eq('id', item_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Item not found")

        update_data = item.model_dump(exclude_unset=True, exclude_none=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        # If container_name and location provided, resolve to box_id
        container_name = update_data.pop('container_name', None)
        location = update_data.pop('location', None)
        if container_name and location:
            box_id = await _get_or_create_box(db, container_name, location)
            update_data['box_id'] = str(box_id)

        update_data = serialize_for_supabase(update_data)

        result = db.table('items').update(update_data).eq('id', item_id).execute()

        return jsonable_encoder({
            "success": True,
            "data": result.data[0] if result.data else None
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating item: {str(e)}")


@router.delete("/item/{item_id}", summary="Delete an item")
async def delete_item(
    item_id: str = Path(..., description="Item UUID"),
    db: Client = Depends(get_supabase_client)
):
    """Delete an item by its UUID."""
    try:
        existing = db.table('items').select('id').eq('id', item_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Item not found")

        db.table('items').delete().eq('id', item_id).execute()

        return {"success": True, "message": "Item deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting item: {str(e)}")


async def _get_or_create_box(db: Client, container_name: str, location: str) -> str:
    """Look up a box by container name, or create it with the given location."""
    result = db.table('boxes').upsert(
        {'name': container_name, 'location': location},
        on_conflict='name'
    ).execute()
    return result.data[0]['id']
