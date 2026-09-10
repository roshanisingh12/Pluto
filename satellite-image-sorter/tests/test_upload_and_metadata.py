"""
tests/test_upload_and_metadata.py

Unit tests for Phase 6 Image Upload and Metadata Management:
- Processing uploaded image bytes (JPG, PNG, TIFF, WEBP)
- Image validation with Pillow
- Width, height, format, file_size extraction
- Filename parsing integration (date, time, land_type)
- Sequential image_id generation (SAT001, SAT002, ...)
- Handling corrupted / invalid files without crashing
- Manual metadata editing behavior
"""

import os
import io
import unittest
import tempfile
from PIL import Image

from models.image_record import ImageRecord
from services.image_reader import process_uploaded_image, read_image, validate_image
from services.metadata_parser import parse_filename


class FakeUploadedFile:
    """Mock Streamlit UploadedFile object."""

    def __init__(self, name: str, data: bytes):
        self.name = name
        self.data = data
        self.size = len(data)

    def getvalue(self) -> bytes:
        return self.data

    def read(self) -> bytes:
        return self.data


class TestUploadAndMetadata(unittest.TestCase):
    """Test suite for Phase 6 image upload and metadata processing."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _create_mock_image_bytes(self, format_name: str, width: int = 200, height: int = 150) -> bytes:
        """Helper to create dummy in-memory image bytes."""
        img = Image.new("RGB", (width, height), color=(50, 100, 150))
        buf = io.BytesIO()
        pillow_fmt = "JPEG" if format_name.upper() in ("JPG", "JPEG") else format_name.upper()
        img.save(buf, format=pillow_fmt)
        return buf.getvalue()

    # ------------------------------------------------------------------
    # 1. Supported Formats Upload & Parsing
    # ------------------------------------------------------------------
    def test_upload_supported_formats(self):
        """Test processing valid JPG, PNG, TIFF, and WEBP uploaded files."""
        formats = [
            ("2026-01-15_10-30_Forest.jpg", "JPEG", "Forest", "2026-01-15", "10-30"),
            ("2026-02-20_14-45_Water.png", "PNG", "Water", "2026-02-20", "14-45"),
            ("2025-12-05_09-20_Urban.tiff", "TIFF", "Urban", "2025-12-05", "09-20"),
            ("2026-03-12_11-20_Barren_Land.webp", "WEBP", "Barren_Land", "2026-03-12", "11-20"),
        ]

        for idx, (fname, fmt_name, expected_land, expected_date, expected_time) in enumerate(formats, start=1):
            img_bytes = self._create_mock_image_bytes(fmt_name, width=320, height=240)
            mock_file = FakeUploadedFile(name=fname, data=img_bytes)
            image_id = f"SAT{idx:03d}"

            record, error = process_uploaded_image(
                mock_file,
                upload_dir=self.temp_dir,
                image_id=image_id,
            )

            self.assertIsNone(error, f"Upload failed for {fname}: {error}")
            self.assertIsNotNone(record)
            self.assertEqual(record.image_id, image_id)
            self.assertEqual(record.image_name, fname)
            self.assertEqual(record.width, 320)
            self.assertEqual(record.height, 240)
            self.assertEqual(record.land_type, expected_land)
            self.assertEqual(record.date, expected_date)
            self.assertEqual(record.time, expected_time)
            self.assertGreater(record.file_size, 0)
            self.assertTrue(os.path.exists(record.file_path))

    # ------------------------------------------------------------------
    # 2. Corrupt / Invalid File Upload Handling
    # ------------------------------------------------------------------
    def test_upload_corrupt_file_does_not_crash(self):
        """Verify uploading corrupted non-image bytes returns a clean error without crashing."""
        corrupt_bytes = b"NOT_A_VALID_IMAGE_DATA_CORRUPT"
        mock_file = FakeUploadedFile(name="corrupted.png", data=corrupt_bytes)

        record, error = process_uploaded_image(
            mock_file,
            upload_dir=self.temp_dir,
            image_id="SAT999",
        )

        self.assertIsNone(record)
        self.assertIsNotNone(error)
        self.assertIn("not a valid", error.lower())

    # ------------------------------------------------------------------
    # 3. Non-standard Filename (Needs Manual Metadata)
    # ------------------------------------------------------------------
    def test_upload_unparsed_filename(self):
        """Verify uploading an image without standard date/time in filename still creates record."""
        img_bytes = self._create_mock_image_bytes("PNG", width=100, height=100)
        mock_file = FakeUploadedFile(name="my_satellite_snapshot.png", data=img_bytes)

        record, error = process_uploaded_image(
            mock_file,
            upload_dir=self.temp_dir,
            image_id="SAT010",
        )

        self.assertIsNone(error)
        self.assertIsNotNone(record)
        self.assertEqual(record.image_name, "my_satellite_snapshot.png")
        self.assertEqual(record.width, 100)
        self.assertEqual(record.height, 100)
        # Date & Time are None because filename was non-standard
        self.assertIsNone(record.date)
        self.assertIsNone(record.time)
        self.assertEqual(record.land_type, "Other")

    # ------------------------------------------------------------------
    # 4. Manual Metadata Editing
    # ------------------------------------------------------------------
    def test_manual_metadata_editing(self):
        """Verify editing date, time, and land_type manually on an ImageRecord."""
        record = ImageRecord(
            image_id="SAT001",
            image_name="custom.jpg",
            file_path="/tmp/custom.jpg",
            image_format="jpg",
            file_size=1000,
            width=200,
            height=200,
        )

        # Simulate user submitting manual metadata form
        new_date = "2026-05-18"
        new_time = "14-30"
        new_land = "Forest"

        record.date = new_date
        record.time = new_time
        record.datetime = f"{new_date} {new_time.replace('-', ':')}"
        record.land_type = new_land

        self.assertEqual(record.date, "2026-05-18")
        self.assertEqual(record.time, "14-30")
        self.assertEqual(record.datetime, "2026-05-18 14:30")
        self.assertEqual(record.land_type, "Forest")
        self.assertTrue(record.is_complete())


if __name__ == "__main__":
    unittest.main(verbosity=2)
