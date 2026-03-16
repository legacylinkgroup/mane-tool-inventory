"""QR code PDF download endpoint."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import logging

from app.services.db import get_supabase_client
from app.services.qr_generator import QRCodeGenerator

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/qr/download")
async def download_qr_pdf() -> Response:
    """
    Download printable PDF with all box QR codes.

    Returns:
        PDF file with 2-column layout of QR codes and box labels
    """
    try:
        client = get_supabase_client()

        # Get all boxes
        response = client.table('boxes').select('id, name, location, qr_code_url').execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=404,
                detail="No boxes found. Please upload inventory data first."
            )

        boxes = response.data

        # Generate PDF
        qr_generator = QRCodeGenerator()
        pdf_bytes = await qr_generator.generate_printable_pdf(boxes)

        logger.info(f"Generated QR PDF with {len(boxes)} boxes")

        # Return PDF
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=box-qr-codes.pdf"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"QR PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
