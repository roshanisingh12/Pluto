"""
api/searching.py

FastAPI routes for executing manual DSA searching algorithms (Linear Search, Binary Search)
on satellite image collections without library search utilities.
"""

import time
from fastapi import APIRouter, HTTPException, status

from models.schemas import SearchRequest, SearchResponse, ImageRecordResponse
from services.catalog import catalog_service
from dsa.searching import linear_search, binary_search

router = APIRouter(prefix="/search", tags=["Searching"])

SEARCH_FIELD_ALIASES = {
    "image_id": "image_id",
    "image id": "image_id",
    "id": "image_id",
    "image_name": "image_name",
    "image name": "image_name",
    "name": "image_name",
    "filename": "image_name",
    "land_type": "land_type",
    "land type": "land_type",
    "land": "land_type",
    "type": "land_type",
    "image_format": "image_format",
    "image format": "image_format",
    "format": "image_format",
    "ext": "image_format",
    "date": "date",
    "datetime": "datetime",
    "date & time": "datetime",
    "file_size": "file_size",
    "file size": "file_size",
    "size": "file_size",
}


@router.post("", response_model=SearchResponse, summary="Execute manual DSA searching")
def search_images(payload: SearchRequest):
    """
    Executes a manual search algorithm from first principles on cataloged images.

    Supported Algorithms:
    - **Linear Search**: Sequential scan across all elements, O(n). Works on unsorted data.
    - **Binary Search**: Logarithmic divide-and-conquer, O(log n). Requires data to be sorted
      by the search key (automatically sorts using Merge Sort if unsorted). Gathers duplicate matches.

    Supported Keys:
    - image_id
    - image_name
    - land_type
    - image_format
    - date
    - datetime
    - file_size
    """
    records = catalog_service.get_all()
    if not records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Catalog is empty. Please upload images or load sample datasets first.",
        )

    if not payload.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty.",
        )

    norm_field = payload.field.strip().lower()
    canonical_field = SEARCH_FIELD_ALIASES.get(norm_field, norm_field)

    algo_norm = payload.algorithm.strip().lower().replace(" ", "").replace("_", "")

    start_time = time.perf_counter()

    if algo_norm in ("linearsearch", "linear"):
        canonical_algo = "Linear Search"
        matches, comparisons = linear_search(
            records,
            target=payload.query.strip(),
            key=canonical_field,
            find_all=payload.find_all,
        )
    elif algo_norm in ("binarysearch", "binary"):
        canonical_algo = "Binary Search"
        matches, comparisons = binary_search(
            records,
            target=payload.query.strip(),
            key=canonical_field,
            is_sorted=False,
            find_all=payload.find_all,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported search algorithm '{payload.algorithm}'. Choose 'Linear Search' or 'Binary Search'.",
        )

    elapsed_sec = time.perf_counter() - start_time
    time_ms = elapsed_sec * 1000.0
    time_us = elapsed_sec * 1000000.0

    return SearchResponse(
        algorithm=canonical_algo,
        field=canonical_field,
        query=payload.query.strip(),
        comparisons=comparisons,
        time_ms=time_ms,
        time_us=time_us,
        matches_count=len(matches),
        results=[ImageRecordResponse.from_domain(r) for r in matches],
    )
