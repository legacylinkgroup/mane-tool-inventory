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
    Upload tool image to Supabase Storage and update item.

    Supports mobile camera capture via <input type="file" accept="image/*" capture="environment">

    Args:
        item_id: UUID of the item
        image: Image file from form upload or mobile camera

    Returns:
        Dict with success status and image_url
    """
    try:
        # Verify item exists
        item_result = db.table('items').select('id, name').eq('id', item_id).execute()
        if not item_result.data:
            raise HTTPException(status_code=404, detail="Item not found")

        item_name = item_result.data[0]['name']

        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if not image.content_type or image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image type. Allowed: {', '.join(allowed_types)}"
            )

        # Read and validate file size
        max_size = settings.max_image_size_mb * 1024 * 1024
        contents = await image.read()
        if len(contents) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"Image too large ({len(contents) / (1024*1024):.1f}MB). Max: {settings.max_image_size_mb}MB"
            )

        # Generate unique filename
        from uuid import uuid4
        file_ext = image.content_type.split('/')[-1]
        if file_ext == 'jpeg':
            file_ext = 'jpg'
        filename = f"{item_id}_{uuid4().hex[:8]}.{file_ext}"
        file_path = f"items/{filename}"

        # Upload to Supabase Storage bucket 'tool-images'
        db.storage.from_('tool-images').upload(
            file_path,
            contents,
            file_options={
                "content-type": image.content_type,
                "upsert": "true"
            }
        )

        # Get public URL
        public_url = db.storage.from_('tool-images').get_public_url(file_path)

        # Update item with image URL
        db.table('items').update({'image_url': public_url}).eq('id', item_id).execute()

        logger.info(f"Image uploaded for item {item_name}: {public_url} ({len(contents)} bytes)")

        return {
            "success": True,
            "data": {
                "image_url": public_url,
                "message": f"Image uploaded successfully for {item_name}"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading image for item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")
