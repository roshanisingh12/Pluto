"""
api/dataset.py

FastAPI routes for inspecting and loading the DeepGlobe sample dataset
and clearing the catalog state.
"""

from fastapi import APIRouter, HTTPException, status

from models.schemas import DatasetLoadRequest, DatasetLoadResponse
from services.catalog import catalog_service

router = APIRouter(tags=["Dataset"])


@router.get("/dataset", summary="Get sample dataset details")
def get_dataset_info():
    """
    Returns information on the pre-bundled DeepGlobe sample satellite dataset,
    including available land classification categories and file quantities on disk.
    """
    return catalog_service.get_dataset_info()


@router.post("/dataset/load", response_model=DatasetLoadResponse, summary="Load sample images into catalog")
def load_dataset(payload: DatasetLoadRequest = None):
    """
    Loads pre-bundled DeepGlobe satellite imagery from sample_images directory
    into the active catalog and indexes them into the ImageHashTable.

    Optional parameter:
    - land_type: 'Forest', 'Water', 'Agriculture', 'Urban', 'Barren', or None for all.
    """
    target = payload.land_type if payload else None
    newly_loaded = catalog_service.load_samples(target_land_type=target)
    total_count = catalog_service.get_count()

    msg = f"Successfully loaded {newly_loaded} satellite images into the catalog."
    if newly_loaded == 0 and total_count > 0:
        msg = "Selected dataset images are already present in the catalog."

    return DatasetLoadResponse(
        success=True,
        loaded_count=newly_loaded,
        total_catalog_count=total_count,
        message=msg,
    )


@router.post("/catalog/clear", summary="Clear active catalog")
def clear_catalog():
    """
    Clears all loaded image records and resets the hash table index and ID counter.
    """
    catalog_service.clear()
    return {
        "success": True,
        "message": "Catalog cleared successfully.",
        "catalog_count": 0,
    }
