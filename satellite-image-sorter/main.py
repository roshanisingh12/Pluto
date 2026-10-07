"""
main.py

FastAPI application entrypoint for the Satellite Image Sorter & Organizer REST API.
Serves as the decoupled backend layer for the future React frontend.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from config import CORS_ORIGINS, HOST, PORT
from models.schemas import HealthResponse
from services.catalog import catalog_service
from api import (
    images,
    upload,
    sorting,
    searching,
    filters,
    statistics,
    benchmark,
    export,
    organize,
    dsa,
    dataset,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle management.
    """
    # Startup: Ensure services are ready
    yield
    # Shutdown: Clean up any background resources if needed


app = FastAPI(
    title="Satellite Image Sorter & Organizer API",
    version="1.0.0",
    description=(
        "REST API backend for satellite imagery cataloging, metadata extraction, "
        "manual Data Structures & Algorithms (Merge/Quick/Bubble Sort, Linear/Binary Search, "
        "Separate Chaining Hash Table), and filesystem organization."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ------------------------------------------------------------------------------
# CORS Middleware
# ------------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# API Routers
# ------------------------------------------------------------------------------
app.include_router(images.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(sorting.router, prefix="/api")
app.include_router(searching.router, prefix="/api")
app.include_router(filters.router, prefix="/api")
app.include_router(statistics.router, prefix="/api")
app.include_router(benchmark.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(organize.router, prefix="/api")
app.include_router(dsa.router, prefix="/api")
app.include_router(dataset.router, prefix="/api")


# ------------------------------------------------------------------------------
# Root & Health Endpoints
# ------------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
def root():
    """Redirect root path to interactive Swagger documentation."""
    return RedirectResponse(url="/docs")


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    System health check returning API status, version, and catalog count.
    """
    return HealthResponse(
        status="ok",
        app="Satellite Image Sorter & Organizer",
        version="1.0.0",
        catalog_count=catalog_service.get_count(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
