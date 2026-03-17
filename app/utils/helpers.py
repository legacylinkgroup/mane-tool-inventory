from uuid import UUID
from typing import Any, Dict


def serialize_for_supabase(data: dict) -> dict:
    """
    Convert UUID objects to strings for Supabase.

    Supabase Python client expects UUIDs as strings, but Pydantic models use UUID4 type.
    This helper ensures consistent serialization across all endpoints.

    Args:
        data: Dictionary with potential UUID values

    Returns:
        Dictionary with UUIDs converted to strings
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, UUID):
            result[key] = str(value)
        else:
            result[key] = value
    return result
