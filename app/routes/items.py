from fastapi import APIRouter, Depends, Query, HTTPException, Path
from supabase import Client
from app.services.db import get_supabase_client
from app.models.item import Item, ItemCreate, ItemUpdate
from app.utils.helpers import serialize_for_supabase
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/items", summary="Search and filter items")
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
        # Start with base query including box info
        query = db.table('items').select('*, boxes(id, name, location)')

        # Apply search filter
        if search:
            query = query.ilike('name', f'%{search}%')

        # Apply category filter
        if category:
            query = query.eq('category', category)

        # Apply location filter using foreign table syntax
        if location:
            query = query.eq('boxes.location', location)

        # Get total count first (before pagination)
        count_query = db.table('items').select('id', count='exact')
        if search:
            count_query = count_query.ilike('name', f'%{search}%')
        if category:
            count_query = count_query.eq('category', category)
        if location:
            count_query = count_query.eq('boxes.location', location)

        count_result = count_query.execute()
        total = count_result.count if hasattr(count_result, 'count') else len(count_result.data or [])

        # Apply pagination
        query = query.range(offset, offset + limit - 1)

        # Execute query
        result = query.execute()
        items = result.data if result.data else []

        # Calculate low_stock flag for each item
        for item in items:
            item['low_stock'] = item['quantity'] < item.get('low_stock_threshold', 5)

        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": items
        }

    except Exception as e:
        logger.error(f"Error fetching items: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching items: {str(e)}")


@router.get("/filters", summary="Get dynamic filter options")
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
            "success": True,
            "data": {
                "locations": locations,
                "categories": categories
            }
        }

    except Exception as e:
        logger.error(f"Error fetching filters: {e}")
        raise HTTPException(status_code=500, detail="Error fetching filter options")


@router.post("/item", status_code=201, summary="Create new item")
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

        # Prepare item data with UUID serialization
        item_data = serialize_for_supabase(item.model_dump())

        # Create item
        result = db.table('items').insert(item_data).execute()

        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create item")

        return {
            "success": True,
            "data": result.data[0]
        }

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

        # Serialize UUIDs if present
        update_data = serialize_for_supabase(update_data)

        # Update item
        result = db.table('items').update(update_data).eq('id', item_id).execute()

        return {
            "success": True,
            "data": result.data[0] if result.data else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating item: {str(e)}")
