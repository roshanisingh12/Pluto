"""
services/image_reader.py

Uses Pillow to open a satellite image file and extract:
    - Width (pixels)
    - Height (pixels)
    - Format (e.g. JPEG, PNG, TIFF)
    - File size (bytes)
    - Basic validity check

Returns a populated ImageRecord or enriches an existing one.
"""

import os
from typing import Optional, Tuple

from PIL import Image, UnidentifiedImageError

from models.image_record import ImageRecord


# ------------------------------------------------------------------ #
# Public API                                                           #
# ------------------------------------------------------------------ #

class ImageReadResult:
    """
    Outcome of attempting to read an image file.

    Attributes:
        success  : True when the file could be opened and read.
        record   : ImageRecord with width/height/format/file_size populated.
        error    : Human-readable error message (empty string on success).
    """

    def __init__(self, success: bool, record: ImageRecord, error: str = ""):
        self.success = success
        self.record = record
        self.error = error

    def __repr__(self) -> str:
        if self.success:
            return (
                f"ImageReadResult(OK, {self.record.width}x{self.record.height}, "
                f"format={self.record.image_format}, size={self.record.file_size}B)"
            )
        return f"ImageReadResult(FAIL, error={self.error!r})"


def read_image(file_path: str, record: Optional[ImageRecord] = None) -> ImageReadResult:
    """
    Open *file_path* with Pillow and populate image properties.

    Parameters
    ----------
    file_path : str
        Path to the image file on disk.
    record : ImageRecord, optional
        An existing ImageRecord to enrich.  If None, a new one is created
        with file_path and image_name pre-filled.

    Returns
    -------
    ImageReadResult
        .success is True when all properties were successfully read.
    """
    if record is None:
        record = ImageRecord(
            image_name=os.path.basename(file_path),
            file_path=file_path,
        )

    # ---------------------------------------------------------------- #
    # 1. Check file existence                                           #
    # ---------------------------------------------------------------- #
    if not os.path.isfile(file_path):
        return ImageReadResult(
            success=False,
            record=record,
            error=f"File not found: '{file_path}'",
        )

    # ---------------------------------------------------------------- #
    # 2. Read file size (OS level – no need to open the image)         #
    # ---------------------------------------------------------------- #
    try:
        record.file_size = os.path.getsize(file_path)
    except OSError as exc:
        return ImageReadResult(
            success=False,
            record=record,
            error=f"Cannot read file size: {exc}",
        )

    # ---------------------------------------------------------------- #
    # 3. Open with Pillow                                               #
    # ---------------------------------------------------------------- #
    try:
        with Image.open(file_path) as img:
            record.width, record.height = img.size
            # Pillow format strings e.g. "JPEG", "PNG", "TIFF"
            pillow_fmt = img.format or ""
            # Normalise to lowercase extension style
            fmt_map = {
                "JPEG": "jpg",
                "PNG": "png",
                "TIFF": "tiff",
                "BMP": "bmp",
                "GIF": "gif",
                "WEBP": "webp",
            }
            record.image_format = fmt_map.get(pillow_fmt.upper(), pillow_fmt.lower())

    except UnidentifiedImageError:
        return ImageReadResult(
            success=False,
            record=record,
            error=f"File '{file_path}' is not a valid or recognised image.",
        )
    except Exception as exc:  # noqa: BLE001
        return ImageReadResult(
            success=False,
            record=record,
            error=f"Unexpected error reading image: {exc}",
        )

    return ImageReadResult(success=True, record=record)


def validate_image(file_path: str) -> Tuple[bool, str]:
    """
    Quick validity check.

    Returns
    -------
    (is_valid : bool, message : str)
    """
    result = read_image(file_path)
    if result.success:
        return True, (
            f"Valid image: {result.record.width}x{result.record.height} px, "
            f"format={result.record.image_format}, "
            f"size={result.record.file_size} bytes."
        )
    return False, result.error


def enrich_record_from_file(record: ImageRecord) -> ImageReadResult:
    """
    Enrich an existing ImageRecord with pixel dimensions and file size
    by reading the file at record.file_path.
    """
    return read_image(record.file_path, record=record)
