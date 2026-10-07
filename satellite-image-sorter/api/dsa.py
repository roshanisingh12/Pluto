"""
api/dsa.py

FastAPI routes for providing theoretical DSA specifications, complexity matrices,
and viva examination reference data.
"""

from fastapi import APIRouter
from services.dsa_info import get_all_dsa_info

router = APIRouter(prefix="/dsa", tags=["DSA Information"])


@router.get("", summary="Get DSA educational specifications and viva notes")
def get_dsa_information():
    """
    Returns full theoretical documentation for all DSA concepts implemented in this system:
    - Sorting algorithm mechanics, complexity analysis, and stability
    - Searching algorithm mechanics, prerequisites, and duplicate resolution
    - Hash Table architecture, rolling hash function, separate chaining, and resizing
    - Predicate filtering complexity
    - 15 common college viva examination Q&As
    """
    return get_all_dsa_info()
