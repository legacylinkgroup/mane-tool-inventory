"""CSV parsing service with merge strategy (Item Name + Container as composite key)."""
import csv
import io
from typing import Dict, List, Tuple, Optional
from decimal import Decimal, InvalidOperation
import logging

logger = logging.getLogger(__name__)


class CSVParseError(Exception):
    """Custom exception for CSV parsing errors."""
    pass


class CSVParser:
    """Parse CSV files for tool inventory with flexible format support."""

    # New format required columns
    NEW_REQUIRED_COLUMNS = ['Item Name', 'Category', 'Quantity', 'Container Name', 'Location']

    # Legacy format required columns (backward compat)
    LEGACY_REQUIRED_COLUMNS = ['Item Name', 'Category', 'Quantity', 'Box/Location']

    # Optional columns (extended format)
    OPTIONAL_COLUMNS = [
        'Brand/Platform',
        'Serial Number',
        'Estimated Value',
        'Dropbox URL',
        'Image URL',
        'Low Stock Threshold'
    ]

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.is_legacy_format: bool = False

    def parse_csv_content(self, content: bytes) -> Tuple[List[Dict], List[Dict]]:
        """
        Parse CSV content and return validated rows.

        Args:
            content: Raw CSV file bytes

        Returns:
            Tuple of (parsed_rows, unique_containers)
            unique_containers is a list of dicts: {'container_name': str, 'location': str}

        Raises:
            CSVParseError: If CSV is malformed or missing required columns
        """
        self.errors = []
        self.warnings = []

        try:
            content_str = content.decode('utf-8')
        except UnicodeDecodeError:
            raise CSVParseError("File encoding error. Please ensure CSV is UTF-8 encoded.")

        csv_file = io.StringIO(content_str)
        reader = csv.DictReader(csv_file)

        if not reader.fieldnames:
            raise CSVParseError("CSV file is empty or has no header row.")

        # Detect format and validate headers
        self._validate_headers(reader.fieldnames)

        # Parse rows
        parsed_rows = []
        unique_containers = {}  # key: container_name -> location

        for row_num, row in enumerate(reader, start=2):
            try:
                parsed_row = self._parse_row(row, row_num)
                if parsed_row:
                    parsed_rows.append(parsed_row)
                    unique_containers[parsed_row['container_name']] = parsed_row['location']
            except Exception as e:
                self.errors.append(f"Row {row_num}: {str(e)}")
                continue

        if not parsed_rows:
            raise CSVParseError("No valid rows found in CSV file.")

        # Build unique containers list
        containers_list = [
            {'container_name': name, 'location': loc}
            for name, loc in sorted(unique_containers.items())
        ]

        logger.info(f"Parsed {len(parsed_rows)} rows, found {len(containers_list)} unique containers")

        return parsed_rows, containers_list

    def _validate_headers(self, fieldnames: List[str]) -> None:
        """Validate that all required columns are present. Supports new and legacy formats."""
        # Check for new format first
        new_missing = [c for c in self.NEW_REQUIRED_COLUMNS if c not in fieldnames]

        if not new_missing:
            self.is_legacy_format = False
            return

        # Fall back to legacy format
        legacy_missing = [c for c in self.LEGACY_REQUIRED_COLUMNS if c not in fieldnames]

        if not legacy_missing:
            self.is_legacy_format = True
            self.warnings.append(
                "Using legacy CSV format (Box/Location column). "
                "New format uses separate 'Container Name' and 'Location' columns."
            )
            return

        # Neither format matches
        raise CSVParseError(
            f"Missing required columns. Use new format: {', '.join(self.NEW_REQUIRED_COLUMNS)} "
            f"or legacy format: {', '.join(self.LEGACY_REQUIRED_COLUMNS)}"
        )

    def _parse_row(self, row: Dict[str, str], row_num: int) -> Optional[Dict]:
        """Parse and validate a single CSV row."""
        item_name = row.get('Item Name', '').strip()
        category = row.get('Category', '').strip()
        quantity_str = row.get('Quantity', '').strip()

        if not item_name:
            raise ValueError("Item Name is required")
        if not category:
            raise ValueError("Category is required")

        # Parse container_name and location based on format
        if self.is_legacy_format:
            box_location = row.get('Box/Location', '').strip()
            if not box_location:
                raise ValueError("Box/Location is required")
            # In legacy format, use box_location as both container name and location
            container_name = box_location
            location = box_location
        else:
            container_name = row.get('Container Name', '').strip()
            location = row.get('Location', '').strip()
            if not container_name:
                raise ValueError("Container Name is required")
            if not location:
                raise ValueError("Location is required")

        # Parse quantity
        try:
            quantity = int(quantity_str)
            if quantity < 0:
                raise ValueError("Quantity cannot be negative")
        except ValueError:
            raise ValueError(f"Invalid quantity '{quantity_str}'. Must be a non-negative integer.")

        parsed = {
            'name': item_name,
            'category': category,
            'quantity': quantity,
            'container_name': container_name,
            'location': location,
        }

        self._parse_optional_fields(row, parsed, row_num)

        return parsed

    def _parse_optional_fields(self, row: Dict[str, str], parsed: Dict, row_num: int) -> None:
        """Parse optional fields from CSV row."""
        # Brand/Platform
        brand = row.get('Brand/Platform', '').strip()
        if brand:
            parsed['brand_platform'] = brand

        # Serial Number
        serial = row.get('Serial Number', '').strip()
        if serial:
            parsed['serial_number'] = serial

        # Estimated Value
        value_str = row.get('Estimated Value', '').strip()
        if value_str:
            try:
                clean_value = value_str.replace('$', '').replace(',', '').strip()
                if clean_value:
                    value = Decimal(clean_value)
                    if value < 0:
                        self.warnings.append(f"Row {row_num}: Negative value ignored")
                    else:
                        parsed['estimated_value'] = value
            except InvalidOperation:
                self.warnings.append(f"Row {row_num}: Invalid estimated value '{value_str}' ignored")

        # Dropbox URL (accept any URL format - no validation)
        dropbox_url = row.get('Dropbox URL', '').strip()
        if dropbox_url:
            parsed['dropbox_manual_url'] = dropbox_url

        # Image URL (accept any URL format - no validation)
        image_url = row.get('Image URL', '').strip()
        if image_url:
            parsed['image_url'] = image_url

        # Low Stock Threshold
        threshold_str = row.get('Low Stock Threshold', '').strip()
        if threshold_str:
            try:
                threshold = int(threshold_str)
                if threshold < 0:
                    self.warnings.append(f"Row {row_num}: Negative threshold ignored, using default")
                else:
                    parsed['low_stock_threshold'] = threshold
            except ValueError:
                self.warnings.append(f"Row {row_num}: Invalid threshold '{threshold_str}' ignored, using default")

    def get_merge_key(self, item_data: Dict) -> Tuple[str, str]:
        """
        Generate composite unique key for merge strategy.

        Returns:
            Tuple of (item_name, container_name)
        """
        return (item_data['name'], item_data['container_name'])
