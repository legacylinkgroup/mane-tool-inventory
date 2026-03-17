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

    Returns CSV file with separate Container Name and Location columns.
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

        # Header row — new format with separate Container Name and Location
        writer.writerow([
            'Item Name',
            'Category',
            'Quantity',
            'Container Name',
            'Location',
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

            writer.writerow([
                item.get('name', ''),
                item.get('category', ''),
                item.get('quantity', 0),
                box_info.get('name', ''),
                box_info.get('location', ''),
                item.get('brand_platform', ''),
                item.get('serial_number', ''),
                item.get('estimated_value', ''),
                item.get('dropbox_manual_url', ''),
                item.get('image_url', ''),
                item.get('updated_at', '')
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
        raise HTTPException(status_code=500, detail=f"Error exporting inventory: {str(e)}")
