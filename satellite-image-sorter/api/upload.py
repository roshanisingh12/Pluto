"""
api/upload.py

FastAPI routes for secure multipart satellite image uploading,
metadata extraction, validation, and catalog indexing.
"""

import os
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, status

from config import UPLOAD_DIR
from models.schemas import UploadResponse, ImageRecordResponse
from models.image_record import ImageRecord
from services.catalog import catalog_service
from services.metadata_parser import parse_filename
from services.image_reader import read_image
from utils.validators import validate_upload, sanitize_filename

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("", response_model=UploadResponse, summary="Upload satellite imagery")
async def upload_images(files: List[UploadFile] = File(..., description="One or more image files to upload")):
    """
    Ingests satellite imagery through multipart form data.

    Security & Validation:
    - Path traversal prevention
    - File extension whitelisting (.jpg, .jpeg, .png, .tiff, .tif, .webp, .bmp)
    - MIME type verification
    - Payload size boundary check (<= 50MB)
    - Image integrity and corrupt file validation via Pillow

    Workflow:
    1. Validates file header and bytes.
    2. Writes image safely to disk in uploads directory.
    3. Parses filename pattern (YYYY-MM-DD_HH-MM_LandType.ext) for acquisition date, time, and land type.
    4. Extracts pixel dimensions and file size using Pillow.
    5. Indexes new ImageRecord into catalog and ImageHashTable.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided in upload request.",
        )

    processed_records = []
    error_messages = []

    for upload_file in files:
        raw_filename = upload_file.filename or "uploaded_image.jpg"
        safe_name = sanitize_filename(raw_filename)

        try:
            content = await upload_file.read()
        except Exception as exc:
            error_messages.append(f"Could not read upload '{raw_filename}': {exc}")
            continue

        # Run security & integrity validation
        is_valid, validation_error = validate_upload(
            filename=safe_name,
            file_bytes=content,
            content_type=upload_file.content_type,
        )
        if not is_valid:
            error_messages.append(f"Validation failed for '{raw_filename}': {validation_error}")
            continue

        original_name = safe_name

        # Save to disk
        dest_path = os.path.join(str(UPLOAD_DIR), safe_name)
        # Handle collision if file already exists with same name
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(safe_name)
            counter = 1
            while os.path.exists(dest_path):
                dest_path = os.path.join(str(UPLOAD_DIR), f"{base}_{counter}{ext}")
                counter += 1
            safe_name = os.path.basename(dest_path)

        try:
            with open(dest_path, "wb") as f:
                f.write(content)
        except Exception as exc:
            error_messages.append(f"Failed to write '{safe_name}' to disk: {exc}")
            continue

        # Generate unique sequential ID
        image_id = catalog_service.get_next_image_id()

        # Parse filename metadata from original filename
        parse_result = parse_filename(original_name)
        record = parse_result.record
        record.image_name = original_name
        record.image_id = image_id
        record.file_path = str(os.path.abspath(dest_path))

        # Enrich with image dimensions and exact format
        read_res = read_image(dest_path, record=record)
        if not read_res.success:
            # Cleanup invalid file
            try:
                os.remove(dest_path)
            except OSError:
                pass
            error_messages.append(f"Pillow decode error for '{safe_name}': {read_res.error}")
            continue

        if not record.land_type:
            record.land_type = "Other"

        # Index in catalog
        catalog_service.add_record(record)
        processed_records.append(record)

    success = len(processed_records) > 0
    return UploadResponse(
        success=success,
        uploaded_count=len(processed_records),
        images=[ImageRecordResponse.from_domain(r) for r in processed_records],
        errors=error_messages,
    )
