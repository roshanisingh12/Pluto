"""
api/filters.py

FastAPI routes for multi-criteria predicate filtering of satellite imagery.
"""

import time
from fastapi import APIRouter, HTTPException, status

from models.schemas import FilterRequest, FilterResponse, ImageRecordResponse
from services.catalog import catalog_service
from dsa.searching import filter_records

router = APIRouter(prefix="/filter", tags=["Filtering"])


@router.post("", response_model=FilterResponse, summary="Filter catalog by multiple criteria")
def filter_images(payload: FilterRequest):
    """
    Evaluates multi-criteria predicate filters in a single pass O(n) scan.

    Criteria:
    - **land_type**: Matches specific land type (or all if omitted/'All').
    - **image_format**: Matches specific format (JPG, PNG, TIFF, etc.).
    - **start_date**: Ingestion date >= start_date (YYYY-MM-DD).
    - **end_date**: Ingestion date <= end_date (YYYY-MM-DD).
    """
    records = catalog_service.get_all()
    if not records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Catalog is empty. Please upload images or load sample datasets first.",
        )

    start_time = time.perf_counter()

    land_type_arg = payload.land_type if payload.land_type and payload.land_type.lower() != "all" else None
    fmt_arg = payload.image_format if payload.image_format and payload.image_format.lower() != "all" else None

    filtered, comparisons = filter_records(
        records,
        land_type=land_type_arg,
        image_format=fmt_arg,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return FilterResponse(
        land_type=payload.land_type,
        image_format=payload.image_format,
        start_date=payload.start_date,
        end_date=payload.end_date,
        comparisons=comparisons,
        time_ms=elapsed_ms,
        matches_count=len(filtered),
        results=[ImageRecordResponse.from_domain(r) for r in filtered],
    )
