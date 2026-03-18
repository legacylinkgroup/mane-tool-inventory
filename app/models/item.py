from pydantic import BaseModel, UUID4, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

class ItemBase(BaseModel):
    """Base item model with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=0)
    box_id: UUID4
    dropbox_manual_url: Optional[str] = None
    image_url: Optional[str] = None
    brand_platform: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    estimated_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    low_stock_threshold: int = Field(default=0, ge=0)
    bought_on: Optional[date] = None
    bought_from: Optional[str] = Field(None, max_length=255)

class ItemCreate(ItemBase):
    """Model for creating a new item."""
    pass

class ItemUpdate(BaseModel):
    """Model for updating an item (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[int] = Field(None, ge=0)
    box_id: Optional[UUID4] = None
    container_name: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[str] = Field(None, min_length=1, max_length=100)
    dropbox_manual_url: Optional[str] = None
    image_url: Optional[str] = None
    brand_platform: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    estimated_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    bought_on: Optional[date] = None
    bought_from: Optional[str] = Field(None, max_length=255)

class Item(ItemBase):
    """Complete item model (returned from database)."""
    id: UUID4
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class ItemWithBox(Item):
    """Item model with nested box information."""
    box: Optional[dict] = None  # Will contain box details
