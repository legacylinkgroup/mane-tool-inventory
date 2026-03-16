"""CSV parsing service with merge strategy (Item Name + Box as composite key)."""
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

    # Required columns (minimal format)
    REQUIRED_COLUMNS = ['Item Name', 'Category', 'Quantity', 'Box/Location']

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

    def parse_csv_content(self, content: bytes) -> Tuple[List[Dict], List[str]]:
        """
        Parse CSV content and return validated rows.

        Args:
            content: Raw CSV file bytes

        Returns:
            Tuple of (parsed_rows, unique_box_locations)

        Raises:
            CSVParseError: If CSV is malformed or missing required columns
        """
        self.errors = []
        self.warnings = []

        try:
            # Decode bytes to string
            content_str = content.decode('utf-8')
        except UnicodeDecodeError:
            raise CSVParseError("File encoding error. Please ensure CSV is UTF-8 encoded.")

        # Parse CSV
        csv_file = io.StringIO(content_str)
        reader = csv.DictReader(csv_file)

        if not reader.fieldnames:
            raise CSVParseError("CSV file is empty or has no header row.")

        # Validate required columns
        self._validate_headers(reader.fieldnames)

        # Parse rows
        parsed_rows = []
        unique_boxes = set()

        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                parsed_row = self._parse_row(row, row_num)
                if parsed_row:
                    parsed_rows.append(parsed_row)
                    unique_boxes.add(parsed_row['box_location'])
            except Exception as e:
                self.errors.append(f"Row {row_num}: {str(e)}")
                continue

        if not parsed_rows:
            raise CSVParseError("No valid rows found in CSV file.")

        logger.info(f"Parsed {len(parsed_rows)} rows, found {len(unique_boxes)} unique box locations")

        return parsed_rows, sorted(list(unique_boxes))

    def _validate_headers(self, fieldnames: List[str]) -> None:
        """Validate that all required columns are present."""
        missing_columns = []
        for required in self.REQUIRED_COLUMNS:
            if required not in fieldnames:
                missing_columns.append(required)

        if missing_columns:
            raise CSVParseError(
                f"Missing required columns: {', '.join(missing_columns)}. "
                f"Required columns are: {', '.join(self.REQUIRED_COLUMNS)}"
            )

    def _parse_row(self, row: Dict[str, str], row_num: int) -> Optional[Dict]:
        """Parse and validate a single CSV row."""
        # Extract required fields
        item_name = row.get('Item Name', '').strip()
        category = row.get('Category', '').strip()
        quantity_str = row.get('Quantity', '').strip()
        box_location = row.get('Box/Location', '').strip()

        # Validate required fields
        if not item_name:
            raise ValueError("Item Name is required")
        if not category:
            raise ValueError("Category is required")
        if not box_location:
            raise ValueError("Box/Location is required")

        # Parse quantity
        try:
            quantity = int(quantity_str)
            if quantity < 0:
                raise ValueError("Quantity cannot be negative")
        except ValueError:
            raise ValueError(f"Invalid quantity '{quantity_str}'. Must be a non-negative integer.")

        # Build parsed row with required fields
        parsed = {
            'name': item_name,
            'category': category,
            'quantity': quantity,
            'box_location': box_location,
        }

        # Parse optional fields
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
                # Remove currency symbols and commas
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
            Tuple of (item_name, box_location)
        """
        return (item_data['name'], item_data['box_location'])
