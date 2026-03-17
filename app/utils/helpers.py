from uuid import UUID
from decimal import Decimal
from typing import Any, Dict


def serialize_for_supabase(data: dict) -> dict:
    """
    Convert non-JSON-serializable Python types for the Supabase client.

    The supabase-py HTTP client uses standard json.dumps internally,
    which cannot handle UUID or Decimal objects. This converts them
    to strings/floats before the request is sent.
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, UUID):
            result[key] = str(value)
        elif isinstance(value, Decimal):
            result[key] = float(value)
        else:
            result[key] = value
    return result
