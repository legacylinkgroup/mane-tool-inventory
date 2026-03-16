"""CSV upload endpoint."""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
import logging

from app.services.upload import UploadService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)) -> Dict:
    """
    Upload CSV file to create/update inventory.

    Supports both minimal and extended CSV formats.
    Merge strategy: (Item Name + Box/Location) as composite unique key.

    **Minimal Format:**
    - Item Name, Category, Quantity, Box/Location, Dropbox URL

    **Extended Format:**
    - Item Name, Category, Quantity, Box/Location, Brand/Platform,
      Serial Number, Estimated Value, Dropbox URL, Image URL, Low Stock Threshold

    Returns:
        Summary with counts of items/boxes created/updated and any errors
    """
    # Validate file type
    if not file.filename.endswith(('.csv', '.CSV')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a CSV file."
        )

    try:
        # Read file content
        content = await file.read()

        # Process upload
        upload_service = UploadService()
        result = await upload_service.process_csv_upload(content)

        logger.info(
            f"CSV upload complete: {result['summary']['items_created']} created, "
            f"{result['summary']['items_updated']} updated, "
            f"{result['summary']['boxes_created']} new boxes"
        )

        return result

    except Exception as e:
        logger.error(f"CSV upload failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
