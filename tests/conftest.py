import pytest
from uuid import uuid4

@pytest.fixture
def sample_box_data():
    """Sample box data for testing."""
    return {
        "name": "Test Box A",
        "location": "Test Warehouse",
        "sublocation": "Shelf 1"
    }

@pytest.fixture
def sample_item_data():
    """Sample item data for testing."""
    return {
        "name": "Test Wire Stripper",
        "category": "Electrical",
        "quantity": 5,
        "box_id": uuid4(),
        "brand_platform": "Klein Tools",
        "estimated_value": 29.99
    }
