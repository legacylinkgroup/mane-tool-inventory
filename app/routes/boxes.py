from fastapi import APIRouter, Depends, HTTPException, Path
from supabase import Client
from app.services.db import get_supabase_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/containers", summary="List all containers with their items")
async def get_containers(
    db: Client = Depends(get_supabase_client)
):
    """
    Get all boxes (containers) with their nested items.
    Used by the Containers page accordion view.
    """
    try:
        result = db.table('boxes').select('*, items(*)').order('name').execute()
        boxes = result.data if result.data else []

        for box in boxes:
            items = box.get('items', [])
            box['item_count'] = len(items)
            for item in items:
                item['low_stock'] = item['quantity'] < item.get('low_stock_threshold', 5)

        return {
            "success": True,
            "total": len(boxes),
            "data": boxes
        }

    except Exception as e:
        logger.error(f"Error fetching containers: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching containers: {str(e)}")


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

        # Add low_stock flag to each item
        for item in items:
            item['low_stock'] = item['quantity'] < item.get('low_stock_threshold', 5)

        return {
            "success": True,
            "data": {
                "box": box,
                "items": items
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching box {box_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching box details: {str(e)}")
