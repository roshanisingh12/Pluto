"""
api/benchmark.py

FastAPI routes for comparative algorithm benchmarking between Bubble Sort, Merge Sort, and Quick Sort.
"""

from fastapi import APIRouter, HTTPException, status

from models.schemas import BenchmarkRequest, BenchmarkResponse, BenchmarkItemResponse
from services.catalog import catalog_service
from services.benchmark import benchmark_sorting_algorithms
from api.sorting import FIELD_ALIASES

router = APIRouter(prefix="/benchmark", tags=["Benchmarking"])


@router.post("", response_model=BenchmarkResponse, summary="Run head-to-head sorting benchmark")
def run_benchmark(payload: BenchmarkRequest):
    """
    Executes Bubble Sort, Merge Sort, and Quick Sort on identical copies of the
    current catalog dataset to measure empirical execution times and comparison counts.
    """
    records = catalog_service.get_all()
    if not records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Catalog is empty. Please upload images or load sample datasets before benchmarking.",
        )

    norm_field = payload.field.strip().lower()
    canonical_field = FIELD_ALIASES.get(norm_field, norm_field)

    results_data = benchmark_sorting_algorithms(
        records,
        key=canonical_field,
        ascending=payload.ascending,
    )

    items = [
        BenchmarkItemResponse(
            algorithm=r["algorithm"],
            comparisons=r["comparisons"],
            time_ms=r["time_ms"],
            time_us=r["time_us"],
            item_count=r["item_count"],
        )
        for r in results_data
    ]

    return BenchmarkResponse(
        field=canonical_field,
        order="Ascending" if payload.ascending else "Descending",
        dataset_size=len(records),
        results=items,
    )
