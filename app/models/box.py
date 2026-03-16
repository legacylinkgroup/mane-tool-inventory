from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class BoxBase(BaseModel):
    """Base box model with common fields."""
    name: str
    location: str
    sublocation: Optional[str] = None

class BoxCreate(BoxBase):
    """Model for creating a new box."""
    pass

class BoxUpdate(BaseModel):
    """Model for updating a box (all fields optional)."""
    name: Optional[str] = None
    location: Optional[str] = None
    sublocation: Optional[str] = None

class Box(BoxBase):
    """Complete box model (returned from database)."""
    id: UUID4
    qr_code_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
