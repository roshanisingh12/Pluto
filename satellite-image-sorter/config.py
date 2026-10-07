"""
config.py

Configuration settings for Satellite Image Sorter & Organizer API backend.
Supports environment variables with safe development defaults.
"""

import os
from pathlib import Path
from typing import List

# Base directories
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads")))
SAMPLE_DIR = Path(os.getenv("SAMPLE_DIR", str(BASE_DIR / "sample_images")))
ORGANIZED_DIR = Path(os.getenv("ORGANIZED_DIR", str(BASE_DIR / "Organized")))

# Ensure necessary directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ORGANIZED_DIR.mkdir(parents=True, exist_ok=True)

# Server host and port
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

# CORS Configuration
# Accepts comma-separated list of allowed origins from environment variable
_env_cors = os.getenv("CORS_ORIGINS", "")
if _env_cors.strip():
    CORS_ORIGINS: List[str] = [origin.strip() for origin in _env_cors.split(",") if origin.strip()]
else:
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

# Upload Security Constraints
MAX_UPLOAD_SIZE_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(50 * 1024 * 1024)))  # 50 MB
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp", ".bmp"}
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/tiff",
    "image/webp",
    "image/bmp",
    "image/x-ms-bmp",
    "application/octet-stream",
}
