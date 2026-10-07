"""
api/export.py

FastAPI routes for exporting catalog metadata to CSV format.
"""

from fastapi import APIRouter, Response, HTTPException, status

from services.catalog import catalog_service
from services.organizer import generate_metadata_csv

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/csv", summary="Download metadata as CSV (GET)")
@router.post("/csv", summary="Download metadata as CSV (POST)")
def export_csv():
    """
    Generates and downloads a structured CSV file representing all current
    catalog image records and their extracted metadata attributes.
    """
    records = catalog_service.get_all()
    if not records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Catalog is empty. No metadata available to export.",
        )

    csv_content = generate_metadata_csv(records)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=satellite_imagery_metadata.csv",
        },
    )
