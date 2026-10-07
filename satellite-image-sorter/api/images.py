"""
api/images.py

FastAPI routes for querying image records, inspecting metadata, editing attributes,
and serving image file previews.
"""

from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse

from config import BASE_DIR, UPLOAD_DIR, SAMPLE_DIR, ORGANIZED_DIR
from models.schemas import (
    ImageRecordResponse,
    ImageListResponse,
    UpdateMetadataRequest,
)
from services.catalog import catalog_service

from dsa.sorting import merge_sort

router = APIRouter(prefix="/images", tags=["Images"])


@router.get("", response_model=ImageListResponse, summary="List catalog images")
def list_images(
    land_type: Optional[str] = Query(None, description="Filter by land type (e.g. Forest, Water, etc.)"),
    format: Optional[str] = Query(None, description="Filter by format extension (e.g. jpg, png, tiff)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: Optional[int] = Query(None, ge=1, description="Maximum records to return"),
    page: Optional[int] = Query(None, ge=1, description="1-based page number"),
    page_size: Optional[int] = Query(None, ge=1, description="Number of records per page"),
    search: Optional[str] = Query(None, description="Search keyword for filename, id, or land type"),
    sort_by: Optional[str] = Query(None, description="Sort key field: datetime, image_name, file_size, land_type, image_id"),
    order: Optional[str] = Query("asc", description="Sort direction: 'asc' or 'desc'"),
):
    """
    Returns all cataloged satellite images with complete metadata,
    optionally filtered by classification, format, or search term,
    with pagination support via (page, page_size) or (skip, limit),
    and sorting support via manual merge_sort.
    """
    records = catalog_service.get_all(land_type=land_type, format_ext=format)

    if search and search.strip():
        q = search.strip().lower()
        records = [
            r for r in records
            if q in (r.image_name or "").lower()
            or q in (r.image_id or "").lower()
            or q in (r.land_type or "").lower()
            or q in (r.datetime or "").lower()
            or q in (r.date or "").lower()
        ]

    if sort_by and sort_by.strip():
        is_asc = (order or "asc").strip().lower() == "asc"
        records, _ = merge_sort(records, key=sort_by.strip(), ascending=is_asc)

    total = len(records)

    if page is not None:
        effective_page_size = page_size if page_size is not None else 10
        effective_skip = (page - 1) * effective_page_size
        paged = records[effective_skip : effective_skip + effective_page_size]
    elif limit is not None:
        paged = records[skip : skip + limit]
    elif page_size is not None:
        paged = records[skip : skip + page_size]
    else:
        paged = records[skip:]

    items = [ImageRecordResponse.from_domain(r) for r in paged]
    return ImageListResponse(total=total, items=items)


@router.get("/{image_id}", response_model=ImageRecordResponse, summary="Get image metadata by ID")
def get_image(image_id: str):
    """
    Retrieves full metadata for a specific image by its unique ID.
    Performs an O(1) hash table lookup via ImageHashTable.
    """
    record = catalog_service.get_by_id(image_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID '{image_id}' not found in catalog.",
        )
    return ImageRecordResponse.from_domain(record)


@router.put("/{image_id}", response_model=ImageRecordResponse, summary="Update image metadata")
def update_image_metadata(image_id: str, payload: UpdateMetadataRequest):
    """
    Updates editable metadata fields (date, time, land type) for an image.
    Automatically recalculates combined datetime.
    """
    record = catalog_service.update_metadata(
        image_id=image_id,
        date=payload.date,
        time=payload.time,
        land_type=payload.land_type,
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID '{image_id}' not found in catalog.",
        )
    return ImageRecordResponse.from_domain(record)


@router.delete("/{image_id}", summary="Delete an image from catalog")
def delete_image(image_id: str):
    """
    Removes an image record from the catalog and index table.
    """
    success = catalog_service.delete_record(image_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID '{image_id}' not found in catalog.",
        )
    return {"success": True, "message": f"Image '{image_id}' removed from catalog."}


@router.get("/{image_id}/file", summary="Serve raw image file for preview/display")
def get_image_file(image_id: str):
    """
    Streams the raw satellite image file from disk for direct browser rendering.
    Enforces path traversal and directory containment checks.
    """
    record = catalog_service.get_by_id(image_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID '{image_id}' not found in catalog.",
        )

    if not record.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Physical file for image '{image_id}' is not accessible on disk.",
        )

    resolved_path = Path(record.file_path).resolve()
    if not resolved_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Physical file for image '{image_id}' is not accessible on disk.",
        )

    # Security check: Ensure file resides within allowed project directories to prevent path traversal
    allowed_dirs = [BASE_DIR.resolve(), UPLOAD_DIR.resolve(), SAMPLE_DIR.resolve(), ORGANIZED_DIR.resolve()]
    is_safe = any(
        resolved_path == d or d in resolved_path.parents
        for d in allowed_dirs
    )
    if not is_safe:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to the specified file path is forbidden.",
        )

    ext = (record.image_format or resolved_path.suffix.lstrip(".")).lower()
    media_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "tiff": "image/tiff",
        "tif": "image/tiff",
        "webp": "image/webp",
        "bmp": "image/bmp",
    }
    media_type = media_map.get(ext, "application/octet-stream")

    return FileResponse(
        path=str(resolved_path),
        media_type=media_type,
        filename=record.image_name,
    )
