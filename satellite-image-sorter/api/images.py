"""
api/images.py

FastAPI routes for querying image records, inspecting metadata, editing attributes,
and serving image file previews.
"""

import os
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse

from models.schemas import (
    ImageRecordResponse,
    ImageListResponse,
    UpdateMetadataRequest,
)
from services.catalog import catalog_service

router = APIRouter(prefix="/images", tags=["Images"])


@router.get("", response_model=ImageListResponse, summary="List catalog images")
def list_images(
    land_type: Optional[str] = Query(None, description="Filter by land type (e.g. Forest, Water, etc.)"),
    format: Optional[str] = Query(None, description="Filter by format extension (e.g. jpg, png, tiff)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: Optional[int] = Query(None, ge=1, description="Maximum records to return"),
):
    """
    Returns all cataloged satellite images with complete metadata,
    optionally filtered by classification or format.
    """
    records = catalog_service.get_all(land_type=land_type, format_ext=format)
    total = len(records)

    if limit is not None:
        paged = records[skip : skip + limit]
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
    """
    record = catalog_service.get_by_id(image_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID '{image_id}' not found in catalog.",
        )

    if not record.file_path or not os.path.exists(record.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Physical file for image '{image_id}' is not accessible on disk.",
        )

    ext = (record.image_format or os.path.splitext(record.file_path)[1].lstrip(".")).lower()
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
        path=record.file_path,
        media_type=media_type,
        filename=record.image_name,
    )
