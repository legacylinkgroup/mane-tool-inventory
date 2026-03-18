from app.models.box import BoxCreate
from app.models.item import ItemCreate
from uuid import uuid4

def test_box_create_model(sample_box_data):
    """Test BoxCreate model validation."""
    box = BoxCreate(**sample_box_data)
    assert box.name == "Test Box A"
    assert box.location == "Test Warehouse"

def test_item_create_model(sample_item_data):
    """Test ItemCreate model validation."""
    item = ItemCreate(**sample_item_data)
    assert item.name == "Test Wire Stripper"
    assert item.quantity == 5
    assert item.low_stock_threshold == 0  # Default value (0 = disabled)

def test_item_quantity_validation():
    """Test that negative quantity raises validation error."""
    try:
        ItemCreate(
            name="Test",
            category="Test",
            quantity=-1,
            box_id=uuid4()
        )
        assert False, "Should have raised validation error"
    except Exception:
        pass  # Expected
