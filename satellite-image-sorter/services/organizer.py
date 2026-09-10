"""
services/organizer.py

Handles metadata CSV export and physical filesystem organization of
satellite imagery categorized by land type.
"""

import os
import io
import csv
import shutil
from typing import List, Dict, Any, Tuple
import sys

# Ensure root directory is on sys.path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.image_record import ImageRecord

ORGANIZED_CATEGORIES = ["Forest", "Water", "Agriculture", "Urban", "Barren_Land", "Other"]

CSV_COLUMNS = [
    "Image ID",
    "Image Name",
    "Date",
    "Time",
    "Land Type",
    "Format",
    "Width",
    "Height",
    "File Size",
    "File Path",
]


def generate_metadata_csv(records: List[ImageRecord]) -> str:
    """
    Exports a collection of ImageRecord metadata objects into a formatted CSV string.

    Columns:
    - Image ID
    - Image Name
    - Date
    - Time
    - Land Type
    - Format
    - Width
    - Height
    - File Size
    - File Path
    """
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")

    # Write Header
    writer.writerow(CSV_COLUMNS)

    # Write Records
    for r in records:
        writer.writerow([
            r.image_id,
            r.image_name,
            r.date or "",
            r.time or "",
            r.land_type or "Other",
            (r.image_format or "").upper(),
            r.width if r.width is not None else "",
            r.height if r.height is not None else "",
            r.file_size if r.file_size is not None else "",
            r.file_path or "",
        ])

    return output.getvalue()


def _normalize_category_folder(land_type: Optional[str]) -> str:
    """Map arbitrary land_type strings to standardized folder names."""
    if not land_type:
        return "Other"

    norm = land_type.strip().lower().replace(" ", "_")
    if norm == "forest":
        return "Forest"
    elif norm == "water":
        return "Water"
    elif norm == "agriculture":
        return "Agriculture"
    elif norm == "urban":
        return "Urban"
    elif norm in ("barren_land", "barrenland"):
        return "Barren_Land"
    else:
        return "Other"


def organize_images_by_land_type(
    records: List[ImageRecord],
    output_root: str = "Organized",
) -> Dict[str, Any]:
    """
    Physically organizes copies of satellite imagery into subfolders based on Land Type:

    Organized/
    ├── Forest/
    ├── Water/
    ├── Agriculture/
    ├── Urban/
    ├── Barren_Land/
    └── Other/

    Safety Guarantees:
    - Never modifies or deletes original source images.
    - Copies files using shutil.copy2 to preserve metadata.
    - Handles duplicate filenames safely by suffixing the unique image_id or a numerical counter.

    Returns:
    - Summary dictionary with total_copied, category_counts, output_dir, and any errors.
    """
    os.makedirs(output_root, exist_ok=True)

    # Pre-create all category subfolders
    for cat in ORGANIZED_CATEGORIES:
        os.makedirs(os.path.join(output_root, cat), exist_ok=True)

    category_counts = {cat: 0 for cat in ORGANIZED_CATEGORIES}
    errors: List[str] = []
    copied_files: List[Tuple[str, str]] = []

    for r in records:
        if not r.file_path or not os.path.exists(r.file_path):
            errors.append(f"Image '{r.image_name}' ({r.image_id}) skipped: file not found at '{r.file_path}'")
            continue

        target_cat = _normalize_category_folder(r.land_type)
        cat_dir = os.path.join(output_root, target_cat)

        # Generate destination filename and prevent collisions
        base_name = r.image_name if r.image_name else os.path.basename(r.file_path)
        dest_path = os.path.join(cat_dir, base_name)

        if os.path.exists(dest_path):
            name_part, ext_part = os.path.splitext(base_name)
            # Collision detected: suffix with unique image_id
            safe_name = f"{name_part}_{r.image_id}{ext_part}"
            dest_path = os.path.join(cat_dir, safe_name)

            # If still exists (e.g. repeated runs), add numeric counter
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(cat_dir, f"{name_part}_{r.image_id}_{counter}{ext_part}")
                counter += 1

        try:
            shutil.copy2(r.file_path, dest_path)
            category_counts[target_cat] += 1
            copied_files.append((r.file_path, dest_path))
        except Exception as exc:
            errors.append(f"Failed to copy '{r.image_name}': {exc}")

    return {
        "success": True,
        "total_copied": len(copied_files),
        "category_counts": category_counts,
        "output_dir": os.path.abspath(output_root),
        "errors": errors,
        "copied_files": copied_files,
    }
