"""
models/schemas.py

Pydantic schemas for request validation and response serialization.
Ensures strict typings, OpenAPI schema generation, and clean frontend contracts.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


def format_file_size_helper(size_in_bytes: Optional[int]) -> str:
    """Helper to produce human-readable file size string."""
    if size_in_bytes is None:
        return "N/A"
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"


# ==============================================================================
# Image Record Representation
# ==============================================================================

class ImageRecordResponse(BaseModel):
    """Pydantic model representing an ImageRecord returned to the client."""
    image_id: str = Field(..., description="Unique identifier for the image (e.g. SAT001)")
    image_name: str = Field(..., description="Filename of the image")
    file_path: str = Field(..., description="File path on disk")
    date: Optional[str] = Field(None, description="Acquisition date (YYYY-MM-DD)")
    time: Optional[str] = Field(None, description="Acquisition time (HH-MM)")
    datetime: Optional[str] = Field(None, description="Combined acquisition datetime (YYYY-MM-DD HH:MM)")
    image_format: Optional[str] = Field(None, description="Lowercase image format extension (jpg, png, etc.)")
    land_type: Optional[str] = Field(None, description="Land classification type")
    file_size: Optional[int] = Field(None, description="Size in bytes")
    file_size_formatted: Optional[str] = Field(None, description="Human-readable file size")
    width: Optional[int] = Field(None, description="Width in pixels")
    height: Optional[int] = Field(None, description="Height in pixels")
    dominant_percentage: Optional[str] = Field(None, description="Purity / land type coverage percentage")
    source: Optional[str] = Field(None, description="Source mission or dataset")
    is_complete: bool = Field(False, description="True if all core metadata fields are populated")
    missing_fields: List[str] = Field(default_factory=list, description="List of unpopulated metadata fields")
    preview_url: Optional[str] = Field(None, description="API URL to stream/render image file")

    @classmethod
    def from_domain(cls, record, base_api_url: str = "/api") -> "ImageRecordResponse":
        return cls(
            image_id=record.image_id,
            image_name=record.image_name,
            file_path=record.file_path,
            date=record.date,
            time=record.time,
            datetime=record.datetime,
            image_format=record.image_format,
            land_type=record.land_type,
            file_size=record.file_size,
            file_size_formatted=format_file_size_helper(record.file_size),
            width=record.width,
            height=record.height,
            dominant_percentage=record.dominant_percentage,
            source=record.source,
            is_complete=record.is_complete(),
            missing_fields=record.missing_fields(),
            preview_url=f"{base_api_url}/images/{record.image_id}/file",
        )


class ImageListResponse(BaseModel):
    """List response for image catalog queries."""
    total: int = Field(..., description="Total images in catalog matching query")
    items: List[ImageRecordResponse] = Field(..., description="Image records")


class UpdateMetadataRequest(BaseModel):
    """Request model for updating an image's editable metadata."""
    date: Optional[str] = Field(None, description="Acquisition date (YYYY-MM-DD)")
    time: Optional[str] = Field(None, description="Acquisition time (HH-MM)")
    land_type: Optional[str] = Field(None, description="Land classification category")


# ==============================================================================
# Sorting Schemas
# ==============================================================================

class SortRequest(BaseModel):
    """Request parameters for sorting catalog images using manual DSA algorithms."""
    algorithm: str = Field(
        default="Merge Sort",
        description="Sorting algorithm: 'Merge Sort', 'Quick Sort', or 'Bubble Sort'",
    )
    field: str = Field(
        default="datetime",
        description="Key field to sort by: 'datetime', 'image_name', 'land_type', 'image_format', 'file_size', 'image_id'",
    )
    ascending: bool = Field(
        default=True,
        description="True for ascending order, False for descending",
    )


class SortResponse(BaseModel):
    """Response containing sorted records and performance benchmark metrics."""
    algorithm: str = Field(..., description="Algorithm used")
    field: str = Field(..., description="Field sorted by")
    order: str = Field(..., description="'Ascending' or 'Descending'")
    comparisons: int = Field(..., description="Total comparisons performed by the manual algorithm")
    time_ms: float = Field(..., description="Execution time in milliseconds")
    time_us: float = Field(..., description="Execution time in microseconds")
    total_count: int = Field(..., description="Total items sorted")
    results: List[ImageRecordResponse] = Field(..., description="Sorted image records")


# ==============================================================================
# Searching Schemas
# ==============================================================================

class SearchRequest(BaseModel):
    """Request parameters for manual DSA searching."""
    algorithm: str = Field(
        default="Linear Search",
        description="Search algorithm: 'Linear Search' or 'Binary Search'",
    )
    field: str = Field(
        default="image_name",
        description="Search key field: 'image_id', 'image_name', 'land_type', 'image_format', 'date', 'datetime', 'file_size'",
    )
    query: str = Field(
        ...,
        description="Target query string or value to search for",
    )
    find_all: bool = Field(
        default=True,
        description="Whether to return all matching occurrences or stop at first match",
    )


class SearchResponse(BaseModel):
    """Response containing matched records and search performance metrics."""
    algorithm: str = Field(..., description="Algorithm used")
    field: str = Field(..., description="Field searched on")
    query: str = Field(..., description="Query searched")
    comparisons: int = Field(..., description="Total comparisons performed")
    time_ms: float = Field(..., description="Execution time in milliseconds")
    time_us: float = Field(..., description="Execution time in microseconds")
    matches_count: int = Field(..., description="Number of matching records found")
    results: List[ImageRecordResponse] = Field(..., description="Matching image records")


# ==============================================================================
# Filtering Schemas
# ==============================================================================

class FilterRequest(BaseModel):
    """Multi-criteria filter parameters."""
    land_type: Optional[str] = Field(None, description="Land type to filter by (or None/'All' for any)")
    image_format: Optional[str] = Field(None, description="Image format extension to filter by (or None/'All' for any)")
    start_date: Optional[str] = Field(None, description="Lower bound date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Upper bound date (YYYY-MM-DD)")


class FilterResponse(BaseModel):
    """Response containing filtered records and evaluation metrics."""
    land_type: Optional[str] = Field(None, description="Land type criterion applied")
    image_format: Optional[str] = Field(None, description="Format criterion applied")
    start_date: Optional[str] = Field(None, description="Start date criterion applied")
    end_date: Optional[str] = Field(None, description="End date criterion applied")
    comparisons: int = Field(..., description="Total predicate comparisons performed")
    time_ms: float = Field(..., description="Execution time in milliseconds")
    matches_count: int = Field(..., description="Number of matching records")
    results: List[ImageRecordResponse] = Field(..., description="Filtered image records")


# ==============================================================================
# Benchmarking Schemas
# ==============================================================================

class BenchmarkRequest(BaseModel):
    """Request parameters for head-to-head algorithm comparison."""
    field: str = Field(
        default="datetime",
        description="Sorting key field for comparative run",
    )
    ascending: bool = Field(
        default=True,
        description="Order direction",
    )


class BenchmarkItemResponse(BaseModel):
    """Performance result for an individual sorting algorithm."""
    algorithm: str = Field(..., description="Name of the algorithm")
    comparisons: int = Field(..., description="Total comparison count")
    time_ms: float = Field(..., description="Execution time in milliseconds")
    time_us: float = Field(..., description="Execution time in microseconds")
    item_count: int = Field(..., description="Number of items sorted")


class BenchmarkResponse(BaseModel):
    """Head-to-head comparison result across Bubble, Merge, and Quick Sort."""
    field: str = Field(..., description="Field used for benchmark")
    order: str = Field(..., description="Direction: Ascending or Descending")
    dataset_size: int = Field(..., description="Number of items sorted in benchmark")
    results: List[BenchmarkItemResponse] = Field(..., description="Performance entries for each algorithm")


# ==============================================================================
# Statistics & Organization Schemas
# ==============================================================================

class StatisticsResponse(BaseModel):
    """Catalog analytics and metrics response."""
    total_images: int = Field(..., description="Total images in catalog")
    complete_metadata_count: int = Field(..., description="Count of images with all metadata populated")
    incomplete_metadata_count: int = Field(..., description="Count of images with missing metadata")
    land_type_counts: Dict[str, int] = Field(..., description="Distribution across land types")
    format_counts: Dict[str, int] = Field(..., description="Distribution across image formats")
    timeline_counts: Dict[str, int] = Field(..., description="Acquisition frequency chronologically by date")
    storage_stats: Dict[str, Any] = Field(..., description="File storage metrics (total, avg, min, max bytes)")
    dimension_stats: Optional[Dict[str, Any]] = Field(None, description="Image dimension statistics (resolutions, min, max)")


class OrganizeRequest(BaseModel):
    """Request to physically organize images into category folders."""
    output_dir: Optional[str] = Field(None, description="Custom destination directory (defaults to 'Organized')")


class OrganizeResponse(BaseModel):
    """Summary of physical filesystem organization."""
    success: bool = Field(..., description="True if operation executed")
    total_copied: int = Field(..., description="Number of image files copied")
    category_counts: Dict[str, int] = Field(..., description="File counts copied into each category folder")
    output_dir: str = Field(..., description="Absolute path of target organization directory")
    errors: List[str] = Field(default_factory=list, description="Any warnings or errors encountered")


class DatasetLoadRequest(BaseModel):
    """Request to load DeepGlobe sample dataset images."""
    land_type: Optional[str] = Field(
        None,
        description="Optional land classification to load ('Forest', 'Water', 'Agriculture', 'Urban', 'Barren', or None for all)",
    )


class DatasetLoadResponse(BaseModel):
    """Response from loading sample images."""
    success: bool = Field(..., description="Success flag")
    loaded_count: int = Field(..., description="Number of newly loaded images")
    total_catalog_count: int = Field(..., description="Total images currently in catalog")
    message: str = Field(..., description="Status message")


class HealthResponse(BaseModel):
    """API health status model."""
    status: str = Field("ok", description="Health status")
    app: str = Field("Satellite Image Sorter & Organizer", description="Application name")
    version: str = Field("1.0.0", description="API version")
    catalog_count: int = Field(0, description="Current number of images loaded in catalog")


class UploadResponse(BaseModel):
    """Response after uploading files."""
    success: bool = Field(..., description="True if at least one file was successfully uploaded")
    uploaded_count: int = Field(..., description="Count of successfully processed files")
    images: List[ImageRecordResponse] = Field(default_factory=list, description="Processed image records")
    errors: List[str] = Field(default_factory=list, description="Any upload errors encountered")
