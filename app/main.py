from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.services.db import verify_schema
import logging
import uuid
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Tool Inventory API",
    description="Inventory management system with QR codes and Alexa integration",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Parse allowed origins
origins = settings.allowed_origins.split(",") if settings.allowed_origins != "*" else ["*"]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to each request for tracing."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

@app.on_event("startup")
async def startup_event():
    """Verify database schema on startup."""
    logger.info("🚀 Tool Inventory API starting up...")
    try:
        await verify_schema()
        logger.info("✅ Startup complete!")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        # Don't crash the app, but log the error
        # This allows the /api/docs to still be accessible for debugging

# Root route moved to bottom of file to serve frontend HTML
# @app.get("/")
# async def root():
#     """Health check endpoint."""
#     return {
#         "status": "ok",
#         "message": "Tool Inventory API",
#         "version": "1.0.0",
#         "environment": settings.environment
#     }

@app.get("/api/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "environment": settings.environment
    }

# Import and include routers
from app.routes import items, boxes, export, images, upload, qr, dashboard

app.include_router(items.router, prefix="/api", tags=["items"])
app.include_router(boxes.router, prefix="/api", tags=["boxes"])
app.include_router(export.router, prefix="/api", tags=["export"])
app.include_router(images.router, prefix="/api", tags=["images"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(qr.router, prefix="/api", tags=["qr"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])

# Mount static files (frontend)
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    # Mount static assets
    app.mount("/js", StaticFiles(directory=str(frontend_path / "js")), name="js")
    app.mount("/css", StaticFiles(directory=str(frontend_path / "css")), name="css")
    app.mount("/images", StaticFiles(directory=str(frontend_path / "images")), name="images")

    # Manifest and favicon
    @app.get("/manifest.json", include_in_schema=False)
    async def manifest():
        return FileResponse(str(frontend_path / "manifest.json"), media_type="application/manifest+json")

    @app.get("/favicon.svg", include_in_schema=False)
    async def favicon():
        return FileResponse(str(frontend_path / "images" / "favicon.svg"), media_type="image/svg+xml")

    # Frontend routes
    @app.get("/admin.html")
    async def admin_page():
        return FileResponse(str(frontend_path / "admin.html"))

    @app.get("/inventory.html")
    async def inventory_page():
        return FileResponse(str(frontend_path / "inventory.html"))

    @app.get("/containers.html")
    async def containers_page():
        return FileResponse(str(frontend_path / "containers.html"))

    @app.get("/item-form.html")
    async def item_form_page():
        return FileResponse(str(frontend_path / "item-form.html"))

    @app.get("/box/{box_id}")
    async def box_page(box_id: str):
        return FileResponse(str(frontend_path / "box.html"))

    # Override root to serve frontend
    @app.get("/", include_in_schema=False)
    async def frontend_root():
        return FileResponse(str(frontend_path / "index.html"))
