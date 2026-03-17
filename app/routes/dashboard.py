from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from supabase import Client
from app.services.db import get_supabase_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/dashboard", summary="Get dashboard summary stats")
async def get_dashboard(db: Client = Depends(get_supabase_client)):
    """
    Returns aggregate inventory metrics for the dashboard view.
    """
    try:
        # Fetch all items with box info
        result = db.table('items').select('*, boxes(id, name, location)').execute()
        items = result.data if result.data else []

        # Fetch all boxes
        boxes_result = db.table('boxes').select('id').execute()
        total_containers = len(boxes_result.data) if boxes_result.data else 0

        # Compute aggregates
        total_items = len(items)
        total_quantity = sum(item.get('quantity', 0) for item in items)
        total_value = sum(
            (item.get('quantity', 0) * float(item.get('estimated_value', 0)))
            for item in items
            if item.get('estimated_value') is not None
        )

        # Recent items (top 5 by updated_at)
        sorted_items = sorted(
            items,
            key=lambda x: x.get('updated_at', '') or '',
            reverse=True
        )
        recent_items = sorted_items[:5]

        # Low stock items
        low_stock_items = [
            item for item in items
            if item.get('quantity', 0) <= item.get('low_stock_threshold', 5)
        ]

        return jsonable_encoder({
            "success": True,
            "data": {
                "total_items": total_items,
                "total_containers": total_containers,
                "total_quantity": total_quantity,
                "total_value": round(total_value, 2),
                "recent_items": recent_items,
                "low_stock_items": low_stock_items
            }
        })

    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard: {str(e)}")
