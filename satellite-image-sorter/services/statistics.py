"""
services/statistics.py

Statistical calculation service for the satellite image catalog.
Provides aggregation and frequency counting across land classifications,
file formats, acquisition dates, and storage metrics.
"""

from typing import List, Dict, Any, Optional
import os
import sys

# Ensure root directory is on sys.path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.image_record import ImageRecord
from dsa.sorting import merge_sort

STANDARD_LAND_TYPES = ["Forest", "Water", "Agriculture", "Urban", "Barren_Land", "Other"]
STANDARD_FORMATS = ["JPG", "JPEG", "PNG", "TIFF", "WEBP"]


def get_land_type_counts(records: List[ImageRecord]) -> Dict[str, int]:
    """
    Computes the frequency count for each land type classification.
    Initializes all standard land types with 0 count.
    """
    counts: Dict[str, int] = {lt: 0 for lt in STANDARD_LAND_TYPES}

    for record in records:
        raw_lt = (record.land_type or "Other").strip().replace(" ", "_")
        matched = False
        for std_lt in STANDARD_LAND_TYPES:
            if raw_lt.lower() == std_lt.lower():
                counts[std_lt] += 1
                matched = True
                break
        if not matched:
            counts["Other"] += 1

    return counts


def get_format_counts(records: List[ImageRecord]) -> Dict[str, int]:
    """
    Computes the frequency count for each supported image format.
    Initializes standard formats (JPG, JPEG, PNG, TIFF, WEBP) with 0 count.
    """
    counts: Dict[str, int] = {fmt: 0 for fmt in STANDARD_FORMATS}
    counts["OTHER"] = 0

    for record in records:
        fmt = (record.image_format or "").strip().upper()
        if fmt == "TIF":
            fmt = "TIFF"

        if fmt in counts:
            counts[fmt] += 1
        elif fmt:
            counts["OTHER"] += 1

    # Remove OTHER if 0 for cleaner charts
    if counts["OTHER"] == 0:
        del counts["OTHER"]

    return counts


def get_timeline_counts(records: List[ImageRecord]) -> Dict[str, int]:
    """
    Aggregates image capture frequencies chronologically by date (YYYY-MM-DD).
    Uses manual merge_sort to order the timeline.
    """
    # Filter records that have a valid date
    dated_records = [r for r in records if r.date]
    if not dated_records:
        return {}

    # Sort dated records chronologically using manual merge_sort
    sorted_records, _ = merge_sort(dated_records, key="date", ascending=True)

    timeline: Dict[str, int] = {}
    for r in sorted_records:
        d = r.date.strip()
        timeline[d] = timeline.get(d, 0) + 1

    return timeline


def get_storage_stats(records: List[ImageRecord]) -> Dict[str, Any]:
    """
    Computes total, average, minimum, and maximum file sizes in bytes.
    """
    sizes = [r.file_size for r in records if r.file_size is not None]
    if not sizes:
        return {
            "total_bytes": 0,
            "avg_bytes": 0,
            "min_bytes": 0,
            "max_bytes": 0,
            "count_with_size": 0,
        }

    total_bytes = sum(sizes)
    return {
        "total_bytes": total_bytes,
        "avg_bytes": total_bytes / len(sizes),
        "min_bytes": min(sizes),
        "max_bytes": max(sizes),
        "count_with_size": len(sizes),
    }


def get_overall_summary(records: List[ImageRecord]) -> Dict[str, Any]:
    """
    Generates a comprehensive summary dictionary of catalog metrics.
    """
    total = len(records)
    land_counts = get_land_type_counts(records)
    format_counts = get_format_counts(records)
    timeline_counts = get_timeline_counts(records)
    storage_stats = get_storage_stats(records)

    complete_count = sum(1 for r in records if r.is_complete())

    return {
        "total_images": total,
        "complete_metadata_count": complete_count,
        "incomplete_metadata_count": total - complete_count,
        "land_type_counts": land_counts,
        "format_counts": format_counts,
        "timeline_counts": timeline_counts,
        "storage_stats": storage_stats,
    }
