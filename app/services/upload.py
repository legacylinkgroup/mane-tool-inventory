"""CSV upload service with merge strategy and QR code generation."""
from typing import Dict, List
from uuid import UUID
import logging

from app.services.db import get_supabase_client
from app.services.csv_parser import CSVParser
from app.services.qr_generator import QRCodeGenerator

logger = logging.getLogger(__name__)


class UploadService:
    """Handle CSV upload with box creation and item merge logic."""

    def __init__(self):
        self.csv_parser = CSVParser()
        self.qr_generator = QRCodeGenerator()

    async def process_csv_upload(self, file_content: bytes) -> Dict:
        """
        Process CSV file upload: parse, create/update boxes and items.

        Args:
            file_content: Raw CSV file bytes

        Returns:
            Summary dict with counts and box info
        """
        client = get_supabase_client()

        # Parse CSV — returns containers as list of dicts
        parsed_rows, unique_containers = self.csv_parser.parse_csv_content(file_content)

        # Track statistics
        stats = {
            'items_created': 0,
            'items_updated': 0,
            'boxes_created': 0,
            'boxes_existing': 0,
            'errors': self.csv_parser.errors[:],
            'warnings': self.csv_parser.warnings[:]
        }

        # Step 1: Create or get boxes (containers)
        box_map = await self._create_or_get_boxes(unique_containers, stats)

        # Step 2: Create or update items using merge strategy
        await self._create_or_update_items(parsed_rows, box_map, stats)

        # Step 3: Generate QR codes for newly created boxes
        boxes_info = await self._generate_qr_codes(box_map, stats)

        return {
            'success': True,
            'summary': stats,
            'boxes': boxes_info
        }

    async def _create_or_get_boxes(
        self,
        containers: List[Dict],
        stats: Dict
    ) -> Dict[str, UUID]:
        """
        Create boxes if they don't exist, or get existing ones.

        Args:
            containers: List of dicts with 'container_name' and 'location'

        Returns:
            Dict mapping container_name -> box_id
        """
        client = get_supabase_client()
        box_map = {}

        for container in containers:
            container_name = container['container_name']
            location = container['location']

            # Check if box exists by container name
            response = client.table('boxes').select('id, name').eq('name', container_name).execute()

            if response.data and len(response.data) > 0:
                box_id = UUID(response.data[0]['id'])
                box_map[container_name] = box_id
                stats['boxes_existing'] += 1
                # Update location if it changed
                client.table('boxes').update({'location': location}).eq('id', str(box_id)).execute()
                logger.info(f"Found existing container: {container_name} ({box_id})")
            else:
                # Create new box with explicit container name and location
                new_box = {
                    'name': container_name,
                    'location': location,
                }

                response = client.table('boxes').insert(new_box).execute()
                box_id = UUID(response.data[0]['id'])
                box_map[container_name] = box_id
                stats['boxes_created'] += 1
                logger.info(f"Created new container: {container_name} at {location} ({box_id})")

        return box_map

    async def _create_or_update_items(
        self,
        parsed_rows: List[Dict],
        box_map: Dict[str, UUID],
        stats: Dict
    ) -> None:
        """
        Create or update items using merge strategy (name + box_id as composite key).
        """
        client = get_supabase_client()

        for row in parsed_rows:
            container_name = row.pop('container_name')
            row.pop('location')  # Not stored on items directly
            box_id = box_map[container_name]

            # Prepare item data
            item_data = {
                'name': row['name'],
                'category': row['category'],
                'quantity': row['quantity'],
                'box_id': str(box_id),
                'brand_platform': row.get('brand_platform'),
                'serial_number': row.get('serial_number'),
                'estimated_value': float(row['estimated_value']) if row.get('estimated_value') else None,
                'dropbox_manual_url': row.get('dropbox_manual_url'),
                'image_url': row.get('image_url'),
                'low_stock_threshold': row.get('low_stock_threshold', 5)
            }

            # Check if item exists (composite key: name + box_id)
            response = client.table('items').select('id').eq('name', item_data['name']).eq('box_id', str(box_id)).execute()

            if response.data and len(response.data) > 0:
                item_id = response.data[0]['id']
                update_data = {k: v for k, v in item_data.items() if k not in ['name', 'box_id']}
                client.table('items').update(update_data).eq('id', item_id).execute()
                stats['items_updated'] += 1
                logger.info(f"Updated item: {item_data['name']} in container {container_name}")
            else:
                client.table('items').insert(item_data).execute()
                stats['items_created'] += 1
                logger.info(f"Created item: {item_data['name']} in container {container_name}")

    async def _generate_qr_codes(self, box_map: Dict[str, UUID], stats: Dict) -> List[Dict]:
        """Generate QR codes for boxes (only newly created ones need QR codes)."""
        client = get_supabase_client()
        boxes_info = []

        for container_name, box_id in box_map.items():
            response = client.table('boxes').select('*').eq('id', str(box_id)).execute()
            box_data = response.data[0]

            qr_url = box_data.get('qr_code_url')
            if not qr_url:
                try:
                    qr_url = await self.qr_generator.generate_qr_for_box(str(box_id), container_name)
                    if qr_url and 'placeholder' not in qr_url.lower():
                        client.table('boxes').update({'qr_code_url': qr_url}).eq('id', str(box_id)).execute()
                        logger.info(f"Generated QR code for container: {container_name}")
                    else:
                        logger.warning(f"QR code generation returned placeholder for container: {container_name}")
                        stats['warnings'].append(f"QR code not generated for {container_name} (storage bucket may not exist)")
                except Exception as e:
                    logger.warning(f"Failed to generate QR code for container {container_name}: {e}")
                    qr_url = None
                    stats['warnings'].append(f"QR code generation failed for {container_name}: {str(e)}")

            boxes_info.append({
                'id': str(box_id),
                'name': container_name,
                'location': box_data['location'],
                'qr_url': qr_url or 'Not generated'
            })

        return boxes_info
