"""QR code generation and PDF creation service."""
import qrcode
import io
from typing import List, Dict, Optional
import logging
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from app.services.db import get_supabase_client
from app.config import settings

logger = logging.getLogger(__name__)


class QRCodeGenerator:
    """Generate QR codes and printable PDFs for box locations."""

    def __init__(self):
        self.base_url = settings.supabase_url.replace('/rest/v1', '')
        self.bucket_name = 'qr-codes'

    async def generate_qr_for_box(self, box_id: str, box_name: str) -> str:
        """
        Generate QR code for a box and upload to Supabase Storage.

        Args:
            box_id: UUID of the box
            box_name: Display name of the box

        Returns:
            Public URL of the uploaded QR code image
        """
        client = get_supabase_client()

        # Generate QR code URL (points to /box/{box_id} endpoint)
        # Use environment-aware base URL
        app_url = "http://localhost:8000" if settings.environment == "development" else "https://tool-inventory.vercel.app"
        qr_data = f"{app_url}/box/{box_id}"

        # Generate QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Save to bytes buffer
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # Upload to Supabase Storage
        file_path = f"{box_id}.png"

        try:
            # Upload file
            response = client.storage.from_(self.bucket_name).upload(
                file_path,
                img_buffer.getvalue(),
                file_options={"content-type": "image/png", "upsert": "true"}
            )

            # Get public URL
            public_url = client.storage.from_(self.bucket_name).get_public_url(file_path)

            logger.info(f"QR code uploaded for box {box_name}: {public_url}")
            return public_url

        except Exception as e:
            logger.warning(f"QR code upload failed for box {box_name}: {e}. Using placeholder URL.")
            # Return placeholder URL if upload fails (storage bucket may not exist yet)
            return f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/{file_path}"

    async def generate_printable_pdf(self, boxes: List[Dict]) -> bytes:
        """
        Generate printable PDF with all box QR codes in 2-column layout.

        Args:
            boxes: List of box dicts with id, name, location, qr_url

        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # PDF layout constants
        margin = 0.75 * inch
        qr_size = 2 * inch
        column_width = (width - 2 * margin) / 2
        row_height = 3 * inch
        max_rows_per_page = int((height - 2 * margin) / row_height)

        # Title
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(margin, height - margin, "Tool Inventory - Box QR Codes")

        # Current position
        current_row = 0
        current_col = 0
        current_y = height - margin - 0.5 * inch

        for box in boxes:
            # Calculate position
            x = margin + (current_col * column_width)
            y = current_y - (current_row * row_height)

            # Draw QR code
            try:
                qr_img = self._generate_qr_image(box['id'])
                pdf.drawImage(
                    ImageReader(qr_img),
                    x,
                    y - qr_size,
                    width=qr_size,
                    height=qr_size,
                    preserveAspectRatio=True
                )
            except Exception as e:
                logger.warning(f"Could not embed QR image for {box['name']}: {e}")
                # Draw placeholder rectangle
                pdf.rect(x, y - qr_size, qr_size, qr_size)

            # Draw container name (bold)
            pdf.setFont("Helvetica-Bold", 14)
            label = f"Container: {box['name'][:25]}"
            pdf.drawString(x, y - qr_size - 0.25 * inch, label)

            # Draw location (regular)
            pdf.setFont("Helvetica", 12)
            loc_label = f"Loc: {box['location'][:28]}"
            pdf.drawString(x, y - qr_size - 0.5 * inch, loc_label)

            # Move to next position
            current_col += 1
            if current_col >= 2:
                current_col = 0
                current_row += 1

                # Check if we need a new page
                if current_row >= max_rows_per_page:
                    pdf.showPage()
                    current_row = 0
                    current_y = height - margin - 0.5 * inch

                    # Re-add title on new page
                    pdf.setFont("Helvetica-Bold", 18)
                    pdf.drawString(margin, height - margin, "Tool Inventory - Box QR Codes (continued)")

        # Save PDF
        pdf.save()
        buffer.seek(0)

        logger.info(f"Generated printable PDF with {len(boxes)} QR codes")
        return buffer.getvalue()

    def _generate_qr_image(self, box_id: str) -> io.BytesIO:
        """Generate QR code image as BytesIO object for PDF embedding."""
        app_url = "http://localhost:8000" if settings.environment == "development" else "https://tool-inventory.vercel.app"
        qr_data = f"{app_url}/box/{box_id}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        return img_buffer
