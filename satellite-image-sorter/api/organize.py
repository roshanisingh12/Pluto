"""
api/organize.py

FastAPI routes for physical filesystem organization of satellite images into land classification subfolders.
"""

from fastapi import APIRouter, HTTPException, status

from config import ORGANIZED_DIR
from models.schemas import OrganizeRequest, OrganizeResponse
from services.catalog import catalog_service
from services.organizer import organize_images_by_land_type

router = APIRouter(prefix="/organize", tags=["Organization"])


@router.post("", response_model=OrganizeResponse, summary="Physically organize images by land type")
def organize_images(payload: OrganizeRequest = None):
    """
    Physically organizes satellite imagery files on disk by copying them into
    land classification subfolders:
    - Forest/
    - Water/
    - Agriculture/
    - Urban/
    - Barren_Land/
    - Other/

    Guarantees:
    - Non-destructive (copies files safely using shutil.copy2)
    - Safely handles filename collisions with suffixes
    """
    records = catalog_service.get_all()
    if not records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Catalog is empty. Please upload or load images before organizing.",
        )

    target_dir = payload.output_dir if (payload and payload.output_dir) else str(ORGANIZED_DIR)

    summary = organize_images_by_land_type(
        records,
        output_root=target_dir,
    )

    return OrganizeResponse(
        success=summary["success"],
        total_copied=summary["total_copied"],
        category_counts=summary["category_counts"],
        output_dir=summary["output_dir"],
        errors=summary["errors"],
    )
