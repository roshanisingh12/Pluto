"""
services/metadata_parser.py

Parses satellite image filenames to extract structured metadata.

Expected filename format:
    YYYY-MM-DD_HH-MM_LandType.extension

Examples:
    2026-01-15_10-30_Forest.jpg
    2026-02-20_14-45_Water.png
    2025-12-05_09-20_Urban.tiff
    2026-03-10_16-15_Agriculture.jpeg
    2026-03-12_11-20_Barren_Land.jpg

Supported land types (case-insensitive matching):
    Forest, Water, Agriculture, Urban, Barren_Land, Barren Land, Other
"""

import os
import re
from datetime import datetime as _dt
from typing import Optional

from models.image_record import ImageRecord


# ------------------------------------------------------------------ #
# Constants                                                            #
# ------------------------------------------------------------------ #

VALID_LAND_TYPES = {
    "forest",
    "water",
    "agriculture",
    "urban",
    "barren_land",
    "barren land",
    "other",
}

VALID_FORMATS = {"jpg", "jpeg", "png", "tiff", "tif", "bmp", "gif", "webp"}

# Regex pattern:
#   Group 1 – date      YYYY-MM-DD
#   Group 2 – time      HH-MM
#   Group 3 – land_type any non-dot sequence (may contain underscores / spaces)
#   Group 4 – extension
_FILENAME_RE = re.compile(
    r"^(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})_([^.]+)\.(\w+)$",
    re.IGNORECASE,
)


# ------------------------------------------------------------------ #
# Helper functions                                                     #
# ------------------------------------------------------------------ #

def _normalise_land_type(raw: str) -> str:
    """
    Normalise a raw land-type token extracted from the filename.

    Rules:
    - Replace hyphens and multiple spaces with a single underscore.
    - Title-case the result for display.
    - If the normalised value is a known type, return the canonical form.
    - Otherwise return "Other".
    """
    # Collapse whitespace / hyphens to underscores
    normalised = re.sub(r"[\s\-]+", "_", raw.strip()).lower()

    if normalised in VALID_LAND_TYPES:
        return normalised.replace(" ", "_").title().replace("_", "_")
        # e.g. "barren_land" → "Barren_Land"

    # Also accept "barren land" (space variant)
    if normalised.replace("_", " ") in VALID_LAND_TYPES:
        return "Barren_Land"

    # Check simple membership after stripping underscores
    plain = normalised.replace("_", "")
    for vt in VALID_LAND_TYPES:
        if vt.replace("_", "").replace(" ", "") == plain:
            return vt.replace(" ", "_").title()

    return "Other"


def _validate_date(date_str: str) -> Optional[str]:
    """Return the date string if valid (YYYY-MM-DD), else None."""
    try:
        _dt.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        return None


def _validate_time(time_str: str) -> Optional[str]:
    """Return the time string if valid (HH-MM), else None."""
    try:
        _dt.strptime(time_str, "%H-%M")
        return time_str
    except ValueError:
        return None


# ------------------------------------------------------------------ #
# Public API                                                           #
# ------------------------------------------------------------------ #

class ParseResult:
    """
    Holds the outcome of a filename parse attempt.

    Attributes:
        success        : True when all required fields were extracted.
        record         : Partially or fully populated ImageRecord.
        missing_fields : List of field names that could not be extracted.
        errors         : Human-readable error messages.
    """

    def __init__(
        self,
        success: bool,
        record: ImageRecord,
        missing_fields: list,
        errors: list,
    ):
        self.success = success
        self.record = record
        self.missing_fields = missing_fields
        self.errors = errors

    def __repr__(self) -> str:
        if self.success:
            return f"ParseResult(OK, record={self.record!r})"
        return (
            f"ParseResult(FAIL, missing={self.missing_fields}, "
            f"errors={self.errors})"
        )


def parse_filename(filename: str) -> ParseResult:
    """
    Parse a satellite image filename and return a ParseResult.

    Parameters
    ----------
    filename : str
        The bare filename (with extension) or a full path.  Only the
        basename is analysed.

    Returns
    -------
    ParseResult
        .success is True when date, time, land_type and format were all
        successfully extracted.
    """
    basename = os.path.basename(filename)
    record = ImageRecord(image_name=basename, file_path=filename)
    errors: list = []
    missing: list = []

    match = _FILENAME_RE.match(basename)

    if not match:
        errors.append(
            f"Filename '{basename}' does not match the expected pattern "
            f"'YYYY-MM-DD_HH-MM_LandType.extension'."
        )
        missing = ["date", "time", "land_type", "image_format"]
        return ParseResult(success=False, record=record,
                           missing_fields=missing, errors=errors)

    raw_date, raw_time, raw_land, raw_ext = match.groups()

    # --- Validate date ---
    date_valid = _validate_date(raw_date)
    if date_valid:
        record.date = date_valid
    else:
        errors.append(f"Invalid date '{raw_date}' – must be a real calendar date.")
        missing.append("date")

    # --- Validate time ---
    time_valid = _validate_time(raw_time)
    if time_valid:
        record.time = time_valid
    else:
        errors.append(
            f"Invalid time '{raw_time}' – must be HH-MM with 00≤HH≤23, 00≤MM≤59."
        )
        missing.append("time")

    # --- Build combined datetime ---
    if record.date and record.time:
        hh, mm = record.time.split("-")
        record.datetime = f"{record.date} {hh}:{mm}"

    # --- Validate land type ---
    land_normalised = _normalise_land_type(raw_land)
    record.land_type = land_normalised  # always set; defaults to "Other"
    if land_normalised == "Other" and raw_land.lower() not in {"other"}:
        errors.append(
            f"Unrecognised land type '{raw_land}' – defaulting to 'Other'. "
            f"Known types: Forest, Water, Agriculture, Urban, Barren_Land."
        )

    # --- Validate format ---
    ext = raw_ext.lower()
    record.image_format = ext
    if ext not in VALID_FORMATS:
        errors.append(
            f"Unrecognised image format '.{ext}'. "
            f"Supported: {', '.join(sorted(VALID_FORMATS))}."
        )
        missing.append("image_format")

    success = len(missing) == 0
    return ParseResult(
        success=success,
        record=record,
        missing_fields=missing,
        errors=errors,
    )


def parse_metadata_from_record(record: ImageRecord) -> ParseResult:
    """
    Convenience wrapper: re-parse metadata from an already-created
    ImageRecord (uses image_name as the filename source).
    """
    return parse_filename(record.image_name)
