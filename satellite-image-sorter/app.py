"""
app.py

Satellite Image Sorter and Metadata Manager
Phase 6: Image Upload and Metadata Management

Allows multiple satellite image uploads (JPG, JPEG, PNG, TIFF, WEBP),
validates images using Pillow, parses filename metadata, assigns sequential
image IDs (SAT001, SAT002, ...), displays image previews and metadata cards,
and provides a manual metadata editor for missing or customized attributes.
"""

import os
import sys
from typing import List, Optional
import streamlit as st
from PIL import Image

# Ensure project root is available on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from models.image_record import ImageRecord
from services.image_reader import process_uploaded_image, read_image
from services.metadata_parser import parse_filename

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_images")
os.makedirs(UPLOAD_DIR, exist_ok=True)

LAND_TYPE_OPTIONS = ["Forest", "Water", "Agriculture", "Urban", "Barren_Land", "Other"]


def init_session_state() -> None:
    """Initialize session state variables."""
    if "records" not in st.session_state:
        st.session_state.records = []  # List[ImageRecord]
    if "next_id_num" not in st.session_state:
        st.session_state.next_id_num = 1
    if "processed_upload_keys" not in st.session_state:
        st.session_state.processed_upload_keys = set()


def get_next_image_id() -> str:
    """Generate sequential image IDs like SAT001, SAT002, SAT003."""
    img_id = f"SAT{st.session_state.next_id_num:03d}"
    st.session_state.next_id_num += 1
    return img_id


def format_file_size(size_in_bytes: Optional[int]) -> str:
    """Format file size in bytes to human-readable string."""
    if size_in_bytes is None:
        return "N/A"
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"


def load_sample_images() -> None:
    """Load sample satellite images from sample_images/ directory."""
    if not os.path.exists(SAMPLE_DIR):
        st.warning("Sample images directory not found.")
        return

    sample_files = [
        f for f in os.listdir(SAMPLE_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp"))
    ]

    loaded_count = 0
    for filename in sample_files:
        # Avoid duplicate additions
        if any(r.image_name == filename for r in st.session_state.records):
            continue

        src_path = os.path.join(SAMPLE_DIR, filename)
        dest_path = os.path.join(UPLOAD_DIR, filename)

        # Copy sample file to uploads directory
        try:
            with open(src_path, "rb") as src, open(dest_path, "wb") as dst:
                dst.write(src.read())

            parse_res = parse_filename(filename)
            record = parse_res.record
            record.file_path = dest_path
            record.image_id = get_next_image_id()

            read_res = read_image(dest_path, record=record)
            if read_res.success:
                if not record.land_type:
                    record.land_type = "Other"
                st.session_state.records.append(record)
                loaded_count += 1
        except Exception as exc:
            st.error(f"Error loading sample image '{filename}': {exc}")

    if loaded_count > 0:
        st.success(f"Successfully loaded {loaded_count} sample satellite images!")
        st.rerun()
    else:
        st.info("All sample images are already loaded in the catalog.")


def main():
    st.set_page_config(
        page_title="Satellite Image Sorter & Metadata Manager",
        page_icon="🛰️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    init_session_state()

    # --- Custom CSS Styling ---
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.1rem;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.05rem;
            color: #4B5563;
            margin-bottom: 1.5rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 12px 18px;
            text-align: center;
        }
        .sat-card {
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 14px;
            background-color: #FFFFFF;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
            margin-bottom: 18px;
        }
        .badge-id {
            background-color: #1D4ED8;
            color: white;
            font-weight: bold;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.85rem;
            display: inline-block;
        }
        .badge-land {
            background-color: #059669;
            color: white;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.82rem;
            display: inline-block;
        }
        .badge-format {
            background-color: #6B7280;
            color: white;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.82rem;
            display: inline-block;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Sidebar ---
    with st.sidebar:
        st.header("🛰️ Project Dashboard")
        st.write("DSA Satellite Image Sorter")
        st.markdown("---")

        total_records = len(st.session_state.records)
        st.metric("Total Images", total_records)

        if total_records > 0:
            st.markdown("### Land Types")
            land_counts = {}
            for r in st.session_state.records:
                lt = r.land_type or "Other"
                land_counts[lt] = land_counts.get(lt, 0) + 1
            for lt, count in sorted(land_counts.items()):
                st.write(f"• **{lt}**: {count}")

            st.markdown("### Formats")
            fmt_counts = {}
            for r in st.session_state.records:
                fmt = (r.image_format or "unknown").upper()
                fmt_counts[fmt] = fmt_counts.get(fmt, 0) + 1
            for fmt, count in sorted(fmt_counts.items()):
                st.write(f"• **{fmt}**: {count}")

        st.markdown("---")
        st.subheader("🛠️ Quick Actions")
        if st.button("📥 Load Sample Images", use_container_width=True):
            load_sample_images()

        if total_records > 0:
            if st.button("🗑️ Clear All Images", use_container_width=True):
                st.session_state.records = []
                st.session_state.processed_upload_keys = set()
                st.session_state.next_id_num = 1
                st.success("Catalog cleared.")
                st.rerun()

    # --- Main Header ---
    st.markdown('<div class="main-header">🛰️ Satellite Image Catalog & Metadata Manager</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Upload satellite images, automatically parse sensor acquisition metadata, and manage records.</div>',
        unsafe_allow_html=True,
    )

    # --- Section 1: Image Upload ---
    st.markdown("### 📤 Upload Satellite Images")
    st.caption("Supported image formats: **JPG, JPEG, PNG, TIFF, WEBP**")

    uploaded_files = st.file_uploader(
        "Select satellite images to upload",
        type=["jpg", "jpeg", "png", "tiff", "tif", "webp"],
        accept_multiple_files=True,
        help="Upload multiple satellite images. Metadata will be extracted from filenames (e.g. 2026-01-15_10-30_Forest.jpg) or entered manually.",
        label_visibility="collapsed",
    )

    if uploaded_files:
        newly_processed = 0
        error_messages = []

        for uploaded_file in uploaded_files:
            # Create a unique key for this uploaded file to prevent re-processing on re-runs
            upload_key = f"{uploaded_file.name}_{uploaded_file.size}"
            if upload_key in st.session_state.processed_upload_keys:
                continue

            # Check if record with this filename already exists in session state
            if any(r.image_name == uploaded_file.name for r in st.session_state.records):
                st.session_state.processed_upload_keys.add(upload_key)
                continue

            image_id = get_next_image_id()
            record, error = process_uploaded_image(
                uploaded_file,
                upload_dir=UPLOAD_DIR,
                image_id=image_id,
            )

            if record is not None:
                st.session_state.records.append(record)
                st.session_state.processed_upload_keys.add(upload_key)
                newly_processed += 1
            else:
                error_messages.append(f"❌ **{uploaded_file.name}**: {error}")

        if newly_processed > 0:
            st.success(f"Successfully processed and cataloged {newly_processed} image(s)!")
            st.rerun()

        for err in error_messages:
            st.error(err)

    st.markdown("---")

    # --- Section 2: Image Catalog & Metadata Management ---
    st.markdown("### 🖼️ Image Collection & Metadata")

    if not st.session_state.records:
        st.info("No satellite images uploaded yet. Please upload images above or click **'Load Sample Images'** in the sidebar to get started.")
        return

    # View mode switcher
    view_col1, view_col2 = st.columns([2, 1])
    with view_col1:
        st.write(f"Displaying **{len(st.session_state.records)}** cataloged satellite image(s)")
    with view_col2:
        view_mode = st.radio("Display Layout", ["Card Grid View", "Table View"], horizontal=True, label_visibility="collapsed")

    # --- Card Grid View ---
    if view_mode == "Card Grid View":
        cols_per_row = 3
        records = st.session_state.records

        for row_idx in range(0, len(records), cols_per_row):
            cols = st.columns(cols_per_row)
            for col_idx in range(cols_per_row):
                item_idx = row_idx + col_idx
                if item_idx < len(records):
                    record = records[item_idx]
                    with cols[col_idx]:
                        with st.container(border=True):
                            # Image ID & Format Badges
                            header_col1, header_col2 = st.columns([1, 1])
                            with header_col1:
                                st.markdown(f'<span class="badge-id">{record.image_id}</span>', unsafe_allow_html=True)
                            with header_col2:
                                fmt_str = (record.image_format or "N/A").upper()
                                st.markdown(f'<div style="text-align:right"><span class="badge-format">{fmt_str}</span></div>', unsafe_allow_html=True)

                            # Image Preview
                            if record.file_path and os.path.exists(record.file_path):
                                try:
                                    img = Image.open(record.file_path)
                                    st.image(img, use_container_width=True)
                                except Exception as exc:
                                    st.warning(f"Could not render preview: {exc}")
                            else:
                                st.warning("Image file path not accessible.")

                            # Details
                            st.markdown(f"**Filename:** `{record.image_name}`")
                            
                            date_display = record.date if record.date else "⚠️ _Missing (Edit below)_"
                            time_display = record.time if record.time else "⚠️ _Missing (Edit below)_"
                            dims_display = f"{record.width} × {record.height} px" if record.width and record.height else "N/A"
                            size_display = format_file_size(record.file_size)
                            land_display = record.land_type or "Other"

                            st.markdown(f"""
                            - **Date:** {date_display}
                            - **Time:** {time_display}
                            - **Land Type:** `{land_display}`
                            - **Dimensions:** {dims_display}
                            - **File Size:** {size_display}
                            """)

                            # Manual Metadata Form
                            needs_review = not record.date or not record.time or record.land_type == "Other"
                            expander_label = "⚠️ Complete Metadata" if needs_review else "✏️ Edit Metadata"

                            with st.expander(expander_label, expanded=False):
                                with st.form(key=f"form_{record.image_id}"):
                                    new_date = st.text_input(
                                        "Date (YYYY-MM-DD)",
                                        value=record.date or "2026-01-01",
                                        help="Format: YYYY-MM-DD",
                                    )
                                    new_time = st.text_input(
                                        "Time (HH-MM)",
                                        value=record.time or "12-00",
                                        help="Format: HH-MM (24-hour clock)",
                                    )
                                    
                                    # Selectbox with existing value pre-selected
                                    current_land = record.land_type if record.land_type in LAND_TYPE_OPTIONS else "Other"
                                    land_idx = LAND_TYPE_OPTIONS.index(current_land) if current_land in LAND_TYPE_OPTIONS else 0
                                    new_land = st.selectbox(
                                        "Land Type",
                                        options=LAND_TYPE_OPTIONS,
                                        index=land_idx,
                                    )

                                    save_btn = st.form_submit_button("💾 Save Metadata", use_container_width=True)
                                    if save_btn:
                                        record.date = new_date.strip()
                                        record.time = new_time.strip()
                                        if record.date and record.time:
                                            record.datetime = f"{record.date} {record.time.replace('-', ':')}"
                                        record.land_type = new_land
                                        st.success("Metadata updated successfully!")
                                        st.rerun()

    # --- Structured Table View ---
    else:
        table_data = []
        for r in st.session_state.records:
            table_data.append({
                "Image ID": r.image_id,
                "Image Name": r.image_name,
                "Date": r.date or "N/A",
                "Time": r.time or "N/A",
                "Datetime": r.datetime or "N/A",
                "Land Type": r.land_type or "Other",
                "Format": (r.image_format or "").upper(),
                "Dimensions": f"{r.width}x{r.height}" if r.width and r.height else "N/A",
                "File Size": format_file_size(r.file_size),
            })
        st.dataframe(table_data, use_container_width=True)


if __name__ == "__main__":
    main()
