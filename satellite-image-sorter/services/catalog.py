"""
services/catalog.py

Centralized state manager for the satellite image catalog.
Maintains in-memory records and synchronizes with the manual ImageHashTable (from dsa/hashing.py)
for O(1) primary key lookups by image_id.
"""

import os
import csv
import threading
from pathlib import Path
from typing import List, Optional, Dict, Any

from models.image_record import ImageRecord
from dsa.hashing import ImageHashTable
from services.image_reader import read_image
from services.metadata_parser import parse_filename
from config import SAMPLE_DIR


class CatalogService:
    """
    Catalog manager encapsulating the dataset state, primary key hashing,
    and dataset loading routines extracted from the application layer.
    """

    def __init__(self, sample_dir: Optional[Path] = None):
        self.sample_dir = sample_dir or SAMPLE_DIR
        self._lock = threading.Lock()
        self.records: List[ImageRecord] = []
        self.hash_table: ImageHashTable = ImageHashTable()
        self.next_id_num: int = 1
        self.processed_upload_keys: set = set()

    def get_next_image_id(self) -> str:
        """Generates sequential image IDs such as SAT001, SAT002."""
        with self._lock:
            img_id = f"SAT{self.next_id_num:03d}"
            self.next_id_num += 1
            return img_id

    def get_all(self, land_type: Optional[str] = None, format_ext: Optional[str] = None) -> List[ImageRecord]:
        """Returns all records, optionally filtered by land_type or format."""
        with self._lock:
            items = list(self.records)

        if land_type and land_type.lower() != "all":
            norm = land_type.lower().replace(" ", "_")
            items = [
                r for r in items
                if (r.land_type or "").lower().replace(" ", "_") == norm
                or (norm == "barren" and (r.land_type or "").lower().replace(" ", "_") in ("barren", "barren_land"))
            ]

        if format_ext and format_ext.lower() != "all":
            norm_fmt = format_ext.lower().replace(".", "")
            items = [
                r for r in items
                if (r.image_format or "").lower().replace(".", "") == norm_fmt
            ]

        return items

    def get_by_id(self, image_id: str) -> Optional[ImageRecord]:
        """
        O(1) average lookup using the manual Separate Chaining ImageHashTable.
        """
        with self._lock:
            return self.hash_table.search(image_id)

    def add_record(self, record: ImageRecord) -> ImageRecord:
        """Adds a new ImageRecord to the list and indexes it into the hash table."""
        with self._lock:
            self.records.append(record)
            if record.image_id:
                self.hash_table.insert(record.image_id, record)
        return record

    def update_metadata(
        self,
        image_id: str,
        date: Optional[str] = None,
        time: Optional[str] = None,
        land_type: Optional[str] = None,
    ) -> Optional[ImageRecord]:
        """Updates editable metadata fields for a specific image."""
        with self._lock:
            record = self.hash_table.search(image_id)
            if not record:
                return None

            if date is not None:
                record.date = date.strip() if date.strip() else None

            if time is not None:
                record.time = time.strip() if time.strip() else None

            if record.date and record.time:
                record.datetime = f"{record.date} {record.time.replace('-', ':')}"
            else:
                record.datetime = None

            if land_type is not None:
                record.land_type = land_type.strip() if land_type.strip() else "Other"

            return record

    def delete_record(self, image_id: str) -> bool:
        """Deletes a record from the catalog and hash table."""
        with self._lock:
            record = self.hash_table.search(image_id)
            if not record:
                return False

            self.hash_table.delete(image_id)
            self.records = [r for r in self.records if r.image_id != image_id]
            return True

    def clear(self) -> None:
        """Clears all records and resets state."""
        with self._lock:
            self.records.clear()
            self.hash_table.clear()
            self.next_id_num = 1
            self.processed_upload_keys.clear()

    def get_count(self) -> int:
        """Returns the current catalog size."""
        with self._lock:
            return len(self.records)

    def load_samples(self, target_land_type: Optional[str] = None) -> int:
        """
        Loads satellite imagery from sample_images/ directory and its class subfolders
        (Forest, Water, Agriculture, Urban, Barren), referencing metadata.csv.
        Extracted directly from working application logic.
        """
        sample_path = Path(self.sample_dir)
        if not sample_path.exists():
            return 0

        # 1. Read metadata.csv if available
        metadata_map: Dict[str, Dict[str, str]] = {}
        metadata_file = sample_path / "metadata.csv"
        if metadata_file.exists():
            try:
                with open(metadata_file, mode="r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        fname = row.get("original_filename", "").strip()
                        if fname:
                            metadata_map[fname] = row
            except Exception:
                pass

        # 2. Gather image files from class subdirectories and root
        class_folders = ["Forest", "Water", "Agriculture", "Urban", "Barren"]
        image_candidates = []

        for folder_name in class_folders:
            folder_dir = sample_path / folder_name
            if folder_dir.is_dir():
                if target_land_type and target_land_type not in ("All", "All Classes") and folder_name.lower() != target_land_type.lower():
                    continue
                for img_file in sorted(folder_dir.iterdir()):
                    if img_file.is_file() and img_file.suffix.lower() in (".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp"):
                        image_candidates.append((img_file, folder_name))

        # Fallback to root sample_images folder only if class subdirectories have no matching files
        if not image_candidates:
            for img_file in sorted(sample_path.iterdir()):
                if img_file.is_file() and img_file.suffix.lower() in (".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp"):
                    image_candidates.append((img_file, None))

        loaded_count = 0
        with self._lock:
            existing_names = {r.image_name for r in self.records}

            for file_p, default_land_type in image_candidates:
                filename = file_p.name
                if filename in existing_names:
                    continue

                meta = metadata_map.get(filename, {})
                img_id = meta.get("image_id") or f"SAT{self.next_id_num:03d}"
                if not meta.get("image_id"):
                    self.next_id_num += 1

                land_type = meta.get("land_type") or default_land_type
                if not land_type:
                    parsed = parse_filename(filename)
                    land_type = parsed.record.land_type or "Other"

                record = ImageRecord(
                    image_id=str(img_id),
                    image_name=filename,
                    file_path=str(file_p.resolve()),
                    land_type=land_type,
                    dominant_percentage=meta.get("dominant_percentage"),
                    source=meta.get("source", "DeepGlobe Land Cover Challenge (DigitalGlobe)"),
                    date=None,
                    time=None,
                    datetime=None,
                )

                # Check if filename contains standard date/time pattern (e.g. root samples)
                fn_parsed = parse_filename(filename)
                if fn_parsed.success:
                    record.date = fn_parsed.record.date
                    record.time = fn_parsed.record.time
                    record.datetime = fn_parsed.record.datetime
                    if not record.land_type or record.land_type == "Other":
                        record.land_type = fn_parsed.record.land_type

                read_res = read_image(str(file_p.resolve()), record=record)
                if read_res.success:
                    self.records.append(record)
                    self.hash_table.insert(record.image_id, record)
                    existing_names.add(filename)
                    loaded_count += 1

        return loaded_count

    def get_dataset_info(self) -> Dict[str, Any]:
        """Returns statistics on the sample dataset available on disk."""
        sample_path = Path(self.sample_dir)
        class_folders = ["Forest", "Water", "Agriculture", "Urban", "Barren"]
        info: Dict[str, int] = {}
        total = 0

        for cf in class_folders:
            folder_dir = sample_path / cf
            count = 0
            if folder_dir.is_dir():
                count = sum(1 for f in folder_dir.iterdir() if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp"))
            info[cf] = count
            total += count

        return {
            "dataset_name": "DeepGlobe Land Cover Challenge (DigitalGlobe)",
            "available_classes": class_folders,
            "class_counts": info,
            "total_available_images": total,
        }


# Global singleton instance for backend services
catalog_service = CatalogService()
