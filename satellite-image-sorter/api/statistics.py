"""
api/statistics.py

FastAPI routes for catalog analytics, distributions, and storage statistics.
"""

from fastapi import APIRouter

from models.schemas import StatisticsResponse
from services.catalog import catalog_service
from services.statistics import get_overall_summary

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("", response_model=StatisticsResponse, summary="Get catalog statistics and metrics")
def get_statistics():
    """
    Computes aggregated statistical metrics across the catalog:
    - Total catalog image count
    - Complete vs incomplete metadata records
    - Land type classification distribution
    - Image format frequency distribution
    - Chronological acquisition timeline
    - File storage metrics (total bytes, average bytes, min, max)
    """
    records = catalog_service.get_all()
    summary = get_overall_summary(records)

    return StatisticsResponse(
        total_images=summary["total_images"],
        complete_metadata_count=summary["complete_metadata_count"],
        incomplete_metadata_count=summary["incomplete_metadata_count"],
        land_type_counts=summary["land_type_counts"],
        format_counts=summary["format_counts"],
        timeline_counts=summary["timeline_counts"],
        storage_stats=summary["storage_stats"],
        dimension_stats=summary.get("dimension_stats"),
    )
