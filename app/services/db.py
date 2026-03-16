from supabase import create_client, Client
from app.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SupabaseDB:
    """Supabase database client wrapper with lazy initialization."""

    def __init__(self):
        self.client: Optional[Client] = None

    def get_client(self) -> Client:
        """
        Get Supabase client instance (lazy initialization).

        Initializes the client on first call to provide better error handling
        if .env is missing or invalid.
        """
        if self.client is None:
            try:
                self.client = create_client(
                    settings.supabase_url,
                    settings.supabase_key
                )
                logger.info(f"Supabase client initialized: {settings.supabase_url}")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                raise RuntimeError(
                    f"Failed to connect to Supabase. Check your .env file. Error: {e}"
                )
        return self.client

# Global database instance
db = SupabaseDB()

def get_supabase_client() -> Client:
    """FastAPI dependency to get Supabase client."""
    return db.get_client()

async def verify_schema():
    """
    Verify database schema exists (tables are created).

    Raises RuntimeError if tables are missing.
    Should be called on FastAPI startup.
    """
    client = get_supabase_client()
    try:
        # Test that both tables exist
        client.table('boxes').select('id').limit(1).execute()
        client.table('items').select('id').limit(1).execute()
        logger.info("✓ Database schema verified (boxes and items tables exist)")
    except Exception as e:
        logger.error(f"✗ Database schema verification failed: {e}")
        raise RuntimeError(
            "Database tables not found. Please run the SQL migration from PRD.md Section 16.5"
        )
