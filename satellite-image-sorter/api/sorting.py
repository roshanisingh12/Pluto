"""
api/sorting.py

FastAPI routes for executing manual DSA sorting algorithms (Merge Sort, Quick Sort, Bubble Sort)
on the satellite image catalog without library sort dependencies.
"""

import time
from fastapi import APIRouter, HTTPException, status

from models.schemas import SortRequest, SortResponse, ImageRecordResponse
from services.catalog import catalog_service
from dsa.sorting import merge_sort, quick_sort, bubble_sort

router = APIRouter(prefix="/sort", tags=["Sorting"])

FIELD_ALIASES = {
    "datetime": "datetime",
    "date & time": "datetime",
    "date": "date",
    "time": "time",
    "image_name": "image_name",
    "name": "image_name",
    "filename": "image_name",
    "image name": "image_name",
    "land_type": "land_type",
    "land type": "land_type",
    "land": "land_type",
    "image_format": "image_format",
    "image format": "image_format",
    "format": "image_format",
    "file_size": "file_size",
    "file size": "file_size",
    "size": "file_size",
    "image_id": "image_id",
    "image id": "image_id",
    "id": "image_id",
}


@router.post("", response_model=SortResponse, summary="Execute manual DSA sorting")
def sort_images(payload: SortRequest):
    """
    Executes a manual sorting algorithm from first principles on cataloged images.

    Supported Algorithms:
    - **Merge Sort**: Divide-and-conquer, stable, O(n log n).
    - **Quick Sort**: In-place divide-and-conquer, unstable, O(n log n) avg.
    - **Bubble Sort**: Adjacent element swapping, stable, O(n²) avg, O(n) best.

    Supported Keys:
    - datetime (or date, time)
    - image_name
    - land_type
    - image_format
    - file_size
    - image_id

    Returns the sorted records along with the exact number of comparisons
    and execution time in milliseconds and microseconds.
    """
    records = catalog_service.get_all()
    if not records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Catalog is empty. Please upload images or load sample datasets first.",
        )

    norm_field = payload.field.strip().lower()
    canonical_field = FIELD_ALIASES.get(norm_field, norm_field)

    algo_norm = payload.algorithm.strip().lower().replace(" ", "").replace("_", "")

    start_time = time.perf_counter()

    if algo_norm in ("mergesort", "merge"):
        canonical_algo = "Merge Sort"
        sorted_records, comparisons = merge_sort(
            records,
            key=canonical_field,
            ascending=payload.ascending,
        )
    elif algo_norm in ("quicksort", "quick"):
        canonical_algo = "Quick Sort"
        sorted_records, comparisons = quick_sort(
            records,
            key=canonical_field,
            ascending=payload.ascending,
        )
    elif algo_norm in ("bubblesort", "bubble"):
        canonical_algo = "Bubble Sort"
        sorted_records, comparisons = bubble_sort(
            records,
            key=canonical_field,
            ascending=payload.ascending,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported sorting algorithm '{payload.algorithm}'. Choose 'Merge Sort', 'Quick Sort', or 'Bubble Sort'.",
        )

    elapsed_sec = time.perf_counter() - start_time
    time_ms = elapsed_sec * 1000.0
    time_us = elapsed_sec * 1000000.0

    return SortResponse(
        algorithm=canonical_algo,
        field=canonical_field,
        order="Ascending" if payload.ascending else "Descending",
        comparisons=comparisons,
        time_ms=time_ms,
        time_us=time_us,
        total_count=len(sorted_records),
        results=[ImageRecordResponse.from_domain(r) for r in sorted_records],
    )
