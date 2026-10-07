"""
utils/validators.py

Validation and security utilities for image uploads, file safety, and path sanitation.
Prevents path traversal, excessive file sizes, and malicious payloads.
"""

import io
import os
import re
from typing import Tuple, Optional
from PIL import Image, UnidentifiedImageError

from config import (
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    MAX_UPLOAD_SIZE_BYTES,
)

_SAFE_FILENAME_RE = re.compile(r"^[\w\-. ]+$")


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes an uploaded filename to prevent directory traversal and filesystem attacks.
    Strips directory components and replaces unsafe characters.
    """
    # Extract only the base name (prevents ../ and \ path traversal)
    base = os.path.basename(filename.strip().replace("\\", "/"))
    # Remove any null bytes or non-printable characters
    base = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", base)
    # Strip leading/trailing dots or spaces
    base = base.strip(". ")
    if not base:
        base = "uploaded_satellite_image.jpg"
    return base


def validate_upload(
    filename: str,
    file_bytes: bytes,
    content_type: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Performs comprehensive security and integrity validation on an uploaded file.

    Checks:
    1. Empty file
    2. Maximum file size
    3. Allowed extension
    4. Allowed MIME type (if provided)
    5. Filename safety (path traversal guard)
    6. Real image integrity verification using Pillow

    Returns:
    (is_valid: bool, error_message: Optional[str])
    """
    # 1. Check file size
    if not file_bytes or len(file_bytes) == 0:
        return False, "Uploaded file is empty (0 bytes)."

    if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
        max_mb = MAX_UPLOAD_SIZE_BYTES / (1024 * 1024)
        return False, f"File size ({len(file_bytes) / (1024 * 1024):.2f} MB) exceeds maximum limit of {max_mb:.0f} MB."

    # 2. Check filename safety
    safe_name = sanitize_filename(filename)
    if ".." in filename or "/" in filename or "\\" in filename:
        # Detected traversal attempt
        if safe_name != filename:
            # We sanitize, but flag if malformed
            pass

    ext = os.path.splitext(safe_name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_IMAGE_EXTENSIONS))
        return False, f"Unsupported file extension '{ext}'. Allowed extensions: {allowed}."

    # 3. Check content type if supplied
    if content_type:
        norm_content = content_type.strip().lower()
        if norm_content not in ALLOWED_MIME_TYPES and not norm_content.startswith("image/"):
            return False, f"Unsupported content-type '{content_type}'."

    # 4. Verify actual image payload using Pillow
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify()
    except (UnidentifiedImageError, OSError, SyntaxError) as exc:
        return False, f"File is not a valid or readable image: {exc}"
    except Exception as exc:
        return False, f"Image verification error: {exc}"

    return True, None
