"""
models/image_record.py

Defines the ImageRecord dataclass, which is the core data structure used to
represent a single satellite image and all its associated metadata.
"""

from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class ImageRecord:
    """
    Represents a single satellite image with its metadata.

    Attributes:
        image_id     : Unique identifier (UUID) auto-generated for each record.
        image_name   : Filename without the directory path (e.g. "2026-01-15_10-30_Forest.jpg").
        file_path    : Absolute or relative path to the image file on disk.
        date         : Date extracted from the filename (string "YYYY-MM-DD").
        time         : Time extracted from the filename (string "HH-MM").
        datetime     : Combined datetime string "YYYY-MM-DD HH:MM".
        image_format : File extension / format (e.g. "jpg", "png", "tiff", "jpeg").
        land_type    : Land classification extracted from the filename
                       (Forest | Water | Agriculture | Urban | Barren_Land | Other).
        file_size    : Size of the image file in bytes.
        width        : Width of the image in pixels (None if image could not be read).
        height       : Height of the image in pixels (None if image could not be read).
    """

    image_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    image_name: str = ""
    file_path: str = ""
    date: Optional[str] = None          # "YYYY-MM-DD"
    time: Optional[str] = None          # "HH-MM"
    datetime: Optional[str] = None      # "YYYY-MM-DD HH:MM"
    image_format: Optional[str] = None  # lowercase extension
    land_type: Optional[str] = None
    file_size: Optional[int] = None     # bytes
    width: Optional[int] = None         # pixels
    height: Optional[int] = None        # pixels

    dominant_percentage: Optional[str] = None
    source: Optional[str] = None

    # ------------------------------------------------------------------ #
    # Convenience helpers                                                  #
    # ------------------------------------------------------------------ #

    def is_complete(self) -> bool:
        """Return True when all metadata fields have been populated."""
        return all([
            self.date,
            self.time,
            self.datetime,
            self.image_format,
            self.land_type,
            self.file_size is not None,
            self.width is not None,
            self.height is not None,
        ])

    def missing_fields(self) -> list:
        """Return a list of field names that are still None / empty."""
        checks = {
            "date": self.date,
            "time": self.time,
            "datetime": self.datetime,
            "image_format": self.image_format,
            "land_type": self.land_type,
            "file_size": self.file_size,
            "width": self.width,
            "height": self.height,
        }
        return [name for name, value in checks.items() if value is None]

    def to_dict(self) -> dict:
        """Return a plain dictionary representation of the record."""
        return {
            "image_id": self.image_id,
            "image_name": self.image_name,
            "file_path": self.file_path,
            "date": self.date,
            "time": self.time,
            "datetime": self.datetime,
            "image_format": self.image_format,
            "land_type": self.land_type,
            "dominant_percentage": self.dominant_percentage,
            "source": self.source,
            "file_size": self.file_size,
            "width": self.width,
            "height": self.height,
        }

    def __repr__(self) -> str:
        return (
            f"ImageRecord(image_name={self.image_name!r}, date={self.date!r}, "
            f"time={self.time!r}, land_type={self.land_type!r}, "
            f"format={self.image_format!r}, size={self.file_size}B, "
            f"dims={self.width}x{self.height})"
        )
