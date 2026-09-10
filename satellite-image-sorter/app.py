"""
app.py

Satellite Image Sorter, Search, Analytics Dashboard & Metadata Manager
Phases 1 - 11 Complete:
- Multi-image upload (JPG, JPEG, PNG, TIFF, WEBP) with Pillow validation
- Automatic metadata parsing and sequential ID generation (SAT001, SAT002, ...)
- Manual metadata editing form
- Manual DSA Sorting Algorithms (Merge Sort, Quick Sort, Bubble Sort)
- Manual DSA Searching Algorithms (Linear Search, Binary Search)
- Multi-Criteria Filtering (Land Type, Format, Date Range)
- Analytics Dashboard & Statistical Charts (Land Type, Format, Timeline)
- Metadata CSV Export & Physical Land-Type Organization
- Head-to-Head DSA Sorting Benchmark & Algorithm Comparison Panel
"""

import os
import sys
import time
from typing import List, Optional
import streamlit as st
from PIL import Image

# Ensure project root is available on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from models.image_record import ImageRecord
from services.image_reader import process_uploaded_image, read_image
from services.metadata_parser import parse_filename
from services.statistics import (
    get_land_type_counts,
    get_format_counts,
    get_timeline_counts,
    get_storage_stats,
    get_overall_summary,
)
from services.organizer import generate_metadata_csv, organize_images_by_land_type
from services.benchmark import benchmark_sorting_algorithms
from dsa.sorting import merge_sort, quick_sort, bubble_sort
from dsa.searching import linear_search, binary_search, filter_records

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_images")
ORGANIZED_DIR = os.path.join(os.path.dirname(__file__), "Organized")
os.makedirs(UPLOAD_DIR, exist_ok=True)

LAND_TYPE_OPTIONS = ["Forest", "Water", "Agriculture", "Urban", "Barren_Land", "Other"]
FILTER_LAND_OPTIONS = ["All", "Forest", "Water", "Agriculture", "Urban", "Barren_Land", "Other"]
FILTER_FORMAT_OPTIONS = ["All", "JPG", "JPEG", "PNG", "TIFF", "WEBP"]

# Sorting Algorithm Reference Information
SORT_ALGO_INFO = {
    "Merge Sort": {
        "purpose": "Divide-and-conquer sorting technique designed for guaranteed O(n log n) time complexity and stable element ordering.",
        "working": (
            "1. **Divide**: Recursively halves the list around the midpoint until sublists contain 0 or 1 element.\n"
            "2. **Conquer**: Recursively sorts the left and right sublists.\n"
            "3. **Combine (Merge)**: Merges the two sorted halves in linear time by repeatedly comparing their smallest elements."
        ),
        "best_time": "O(n log n)",
        "avg_time": "O(n log n)",
        "worst_time": "O(n log n)",
        "space": "O(n) auxiliary",
        "stability": "Stable (preserves relative order of duplicate keys)",
    },
    "Quick Sort": {
        "purpose": "High-efficiency divide-and-conquer algorithm that sorts elements in-place using pivot partitioning.",
        "working": (
            "1. **Pivot Selection**: Selects a pivot element (last element via Lomuto partitioning).\n"
            "2. **Partitioning**: Reorganizes the array so all items smaller than the pivot precede it and larger items follow it.\n"
            "3. **Recursion**: Recursively applies the partition step to the left and right subarrays."
        ),
        "best_time": "O(n log n)",
        "avg_time": "O(n log n)",
        "worst_time": "O(n²)",
        "space": "O(log n) recursive call stack",
        "stability": "Unstable",
    },
    "Bubble Sort": {
        "purpose": "Classic comparison-based sorting technique that bubbles elements to their correct position through adjacent swaps.",
        "working": (
            "1. **Passes**: Iterates through the list n - 1 times.\n"
            "2. **Adjacent Comparison**: Compares adjacent elements arr[j] and arr[j + 1].\n"
            "3. **Swapping**: Swaps out-of-order adjacent elements.\n"
            "4. **Early Exit**: If a full pass completes with 0 swaps, the algorithm halts early in O(n) time."
        ),
        "best_time": "O(n) (when already sorted)",
        "avg_time": "O(n²)",
        "worst_time": "O(n²)",
        "space": "O(1) auxiliary",
        "stability": "Stable",
    },
}

# Searching Algorithm Reference Information
SEARCH_ALGO_INFO = {
    "Linear Search": {
        "purpose": "Sequential scan examining elements one-by-one from index 0 to n - 1.",
        "working": (
            "1. Iterates through the collection element by element.\n"
            "2. Compares each element's key directly with the target value.\n"
            "3. Collects all matching items.\n"
            "4. Does not require the list to be sorted beforehand."
        ),
        "best_time": "O(1) (first item matches)",
        "avg_time": "O(n)",
        "worst_time": "O(n)",
        "space": "O(1) auxiliary",
        "requirement": "None (Works on unsorted data)",
    },
    "Binary Search": {
        "purpose": "Logarithmic divide-and-conquer search halving the remaining search space with each comparison.",
        "working": (
            "1. **Prerequisite**: Dataset must be sorted according to the search key.\n"
            "2. Computes midpoint index: mid = (low + high) // 2.\n"
            "3. Compares target with arr[mid] and narrows boundaries to left or right half.\n"
            "4. Expands to left and right neighbors to gather all contiguous duplicates."
        ),
        "best_time": "O(1) (target at initial midpoint)",
        "avg_time": "O(log n)",
        "worst_time": "O(log n)",
        "space": "O(1) auxiliary",
        "requirement": "Strictly requires dataset sorted by search key",
    },
}

SORT_FIELD_MAP = {
    "Date & Time": "datetime",
    "Image Format": "image_format",
    "Land Type": "land_type",
    "Image Name": "image_name",
    "File Size": "file_size",
}

SEARCH_FIELD_MAP = {
    "Image ID": "image_id",
    "Image Name": "image_name",
    "Land Type": "land_type",
    "Image Format": "image_format",
    "Date": "date",
}


def init_session_state() -> None:
    """Initialize session state variables."""
    if "records" not in st.session_state:
        st.session_state.records = []  # List[ImageRecord]
    if "sorted_records" not in st.session_state:
        st.session_state.sorted_records = None
    if "sort_stats" not in st.session_state:
        st.session_state.sort_stats = None
    if "search_results" not in st.session_state:
        st.session_state.search_results = None
    if "search_stats" not in st.session_state:
        st.session_state.search_stats = None
    if "filter_results" not in st.session_state:
        st.session_state.filter_results = None
    if "filter_stats" not in st.session_state:
        st.session_state.filter_stats = None
    if "benchmark_results" not in st.session_state:
        st.session_state.benchmark_results = None
    if "organization_summary" not in st.session_state:
        st.session_state.organization_summary = None
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
        if any(r.image_name == filename for r in st.session_state.records):
            continue

        src_path = os.path.join(SAMPLE_DIR, filename)
        dest_path = os.path.join(UPLOAD_DIR, filename)

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
        st.session_state.sorted_records = None
        st.session_state.sort_stats = None
        st.session_state.search_results = None
        st.session_state.search_stats = None
        st.session_state.filter_results = None
        st.session_state.filter_stats = None
        st.session_state.benchmark_results = None
        st.session_state.organization_summary = None
        st.success(f"Successfully loaded {loaded_count} sample satellite images!")
        st.rerun()
    else:
        st.info("All sample images are already loaded in the catalog.")


def run_manual_sort(algorithm_name: str, sort_field_label: str, ascending: bool) -> None:
    """Execute manual DSA sorting without using any library or built-in sort."""
    if not st.session_state.records:
        st.warning("No images to sort. Please upload or load images first.")
        return

    key_field = SORT_FIELD_MAP[sort_field_label]
    input_records = list(st.session_state.records)

    start_time = time.perf_counter()

    if algorithm_name == "Merge Sort":
        sorted_list, comps = merge_sort(input_records, key=key_field, ascending=ascending)
    elif algorithm_name == "Quick Sort":
        sorted_list, comps = quick_sort(input_records, key=key_field, ascending=ascending)
    elif algorithm_name == "Bubble Sort":
        sorted_list, comps = bubble_sort(input_records, key=key_field, ascending=ascending)
    else:
        st.error(f"Unknown algorithm '{algorithm_name}'")
        return

    elapsed_time = time.perf_counter() - start_time
    elapsed_ms = elapsed_time * 1000.0

    st.session_state.sorted_records = sorted_list
    st.session_state.search_results = None
    st.session_state.filter_results = None
    st.session_state.sort_stats = {
        "algorithm": algorithm_name,
        "field": sort_field_label,
        "order": "Ascending" if ascending else "Descending",
        "comparisons": comps,
        "time_ms": elapsed_ms,
        "count": len(sorted_list),
    }


def run_manual_search(algorithm_name: str, search_field_label: str, query: str) -> None:
    """Execute manual DSA search (Linear or Binary Search)."""
    if not st.session_state.records:
        st.warning("No images in catalog to search.")
        return

    if not query.strip():
        st.warning("Please enter a search query.")
        return

    key_field = SEARCH_FIELD_MAP[search_field_label]
    input_records = list(st.session_state.records)

    start_time = time.perf_counter()

    if algorithm_name == "Linear Search":
        matches, comps = linear_search(input_records, target=query.strip(), key=key_field, find_all=True)
    elif algorithm_name == "Binary Search":
        matches, comps = binary_search(input_records, target=query.strip(), key=key_field, is_sorted=False, find_all=True)
    else:
        st.error(f"Unknown search algorithm '{algorithm_name}'")
        return

    elapsed_time = time.perf_counter() - start_time
    elapsed_ms = elapsed_time * 1000.0

    st.session_state.search_results = matches
    st.session_state.sorted_records = None
    st.session_state.filter_results = None
    st.session_state.search_stats = {
        "algorithm": algorithm_name,
        "field": search_field_label,
        "query": query.strip(),
        "comparisons": comps,
        "matches_count": len(matches),
        "time_ms": elapsed_ms,
    }


def run_manual_filter(land_type: str, image_format: str, start_date: Optional[str], end_date: Optional[str]) -> None:
    """Execute multi-criteria filtering."""
    if not st.session_state.records:
        st.warning("No images in catalog to filter.")
        return

    input_records = list(st.session_state.records)
    start_time = time.perf_counter()

    results, comps = filter_records(
        input_records,
        land_type=land_type if land_type != "All" else None,
        image_format=image_format if image_format != "All" else None,
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None,
    )

    elapsed_time = time.perf_counter() - start_time
    elapsed_ms = elapsed_time * 1000.0

    st.session_state.filter_results = results
    st.session_state.sorted_records = None
    st.session_state.search_results = None
    st.session_state.filter_stats = {
        "land_type": land_type,
        "format": image_format,
        "start_date": start_date or "Any",
        "end_date": end_date or "Any",
        "comparisons": comps,
        "matches_count": len(results),
        "time_ms": elapsed_ms,
    }


def render_image_gallery(records: List[ImageRecord], context_prefix: str = "main") -> None:
    """Renders the image collection in Card Grid or Table layout."""
    if not records:
        st.info("No matching satellite images found.")
        return

    view_col1, view_col2 = st.columns([3, 1])
    with view_col1:
        st.write(f"Displaying **{len(records)}** image(s)")
    with view_col2:
        view_mode = st.radio(
            "Display Layout",
            ["Card Grid View", "Table View"],
            horizontal=True,
            key=f"layout_{context_prefix}",
            label_visibility="collapsed",
        )

    if view_mode == "Card Grid View":
        cols_per_row = 3
        for row_idx in range(0, len(records), cols_per_row):
            cols = st.columns(cols_per_row)
            for col_idx in range(cols_per_row):
                item_idx = row_idx + col_idx
                if item_idx < len(records):
                    record = records[item_idx]
                    with cols[col_idx]:
                        with st.container(border=True):
                            header_col1, header_col2 = st.columns([1, 1])
                            with header_col1:
                                st.markdown(f'<span class="badge-id">{record.image_id}</span>', unsafe_allow_html=True)
                            with header_col2:
                                fmt_str = (record.image_format or "N/A").upper()
                                st.markdown(f'<div style="text-align:right"><span class="badge-format">{fmt_str}</span></div>', unsafe_allow_html=True)

                            if record.file_path and os.path.exists(record.file_path):
                                try:
                                    img = Image.open(record.file_path)
                                    st.image(img, use_container_width=True)
                                except Exception as exc:
                                    st.warning(f"Could not render preview: {exc}")
                            else:
                                st.warning("Image file path not accessible.")

                            st.markdown(f"**Filename:** `{record.image_name}`")

                            date_display = record.date if record.date else "⚠️ _Missing_"
                            time_display = record.time if record.time else "⚠️ _Missing_"
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

                            needs_review = not record.date or not record.time or record.land_type == "Other"
                            expander_label = "⚠️ Complete Metadata" if needs_review else "✏️ Edit Metadata"

                            with st.expander(expander_label, expanded=False):
                                with st.form(key=f"form_{context_prefix}_{record.image_id}_{item_idx}"):
                                    new_date = st.text_input("Date (YYYY-MM-DD)", value=record.date or "2026-01-01")
                                    new_time = st.text_input("Time (HH-MM)", value=record.time or "12-00")

                                    current_land = record.land_type if record.land_type in LAND_TYPE_OPTIONS else "Other"
                                    land_idx = LAND_TYPE_OPTIONS.index(current_land) if current_land in LAND_TYPE_OPTIONS else 0
                                    new_land = st.selectbox("Land Type", options=LAND_TYPE_OPTIONS, index=land_idx)

                                    save_btn = st.form_submit_button("💾 Save Metadata", use_container_width=True)
                                    if save_btn:
                                        record.date = new_date.strip()
                                        record.time = new_time.strip()
                                        if record.date and record.time:
                                            record.datetime = f"{record.date} {record.time.replace('-', ':')}"
                                        record.land_type = new_land
                                        st.success("Metadata updated successfully!")
                                        st.rerun()

    else:
        table_data = []
        for r in records:
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
                "File Path": r.file_path,
            })
        st.dataframe(table_data, use_container_width=True)


def main():
    st.set_page_config(
        page_title="Satellite Image Sorter, Search & Dashboard",
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
            margin-bottom: 1.2rem;
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
        .badge-format {
            background-color: #6B7280;
            color: white;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.82rem;
            display: inline-block;
        }
        .stat-highlight {
            background-color: #EFF6FF;
            border: 1px solid #BFDBFE;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 14px;
        }
        .algo-card {
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 14px;
            background-color: #FFFFFF;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Sidebar ---
    with st.sidebar:
        st.header("🛰️ Catalog Summary")
        total_records = len(st.session_state.records)
        st.metric("Total Catalog Images", total_records)
        st.markdown("---")

        st.subheader("🛠️ Quick Actions")
        if st.button("📥 Load Sample Images", use_container_width=True):
            load_sample_images()

        if total_records > 0:
            if st.button("🗑️ Clear Catalog", use_container_width=True):
                st.session_state.records = []
                st.session_state.sorted_records = None
                st.session_state.sort_stats = None
                st.session_state.search_results = None
                st.session_state.search_stats = None
                st.session_state.filter_results = None
                st.session_state.filter_stats = None
                st.session_state.benchmark_results = None
                st.session_state.organization_summary = None
                st.session_state.processed_upload_keys = set()
                st.session_state.next_id_num = 1
                st.success("Catalog cleared.")
                st.rerun()

    # --- Main Header ---
    st.markdown('<div class="main-header">🛰️ Satellite Image Sorter, Search & Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Professional satellite image analytics, manual DSA sorting & searching, algorithm benchmarking, and metadata management.</div>',
        unsafe_allow_html=True,
    )

    # ==========================================================================
    # Main Feature Tabs
    # ==========================================================================
    tab_dashboard, tab_gallery, tab_sort, tab_compare, tab_search, tab_filter, tab_export, tab_upload = st.tabs([
        "📊 Dashboard & Analytics",
        "🖼️ Image Gallery",
        "⚡ Sort Engine",
        "⚔️ Compare Algorithms",
        "🔍 Search Images",
        "🎯 Filters",
        "📦 Export & Organize",
        "📤 Upload Images",
    ])

    # --------------------------------------------------------------------------
    # TAB 1: Dashboard & Analytics
    # --------------------------------------------------------------------------
    with tab_dashboard:
        st.markdown("### 📊 Satellite Imagery Analytics Dashboard")

        records = st.session_state.records
        summary = get_overall_summary(records)

        # 1. Top Key Metric Cards (Land Types & Total Images)
        st.markdown("#### 🌲 Images by Land Classification")
        lc = summary["land_type_counts"]

        m_row1 = st.columns(6)
        with m_row1[0]:
            st.metric("Total Images", summary["total_images"])
        with m_row1[1]:
            st.metric("Forest", lc.get("Forest", 0))
        with m_row1[2]:
            st.metric("Water", lc.get("Water", 0))
        with m_row1[3]:
            st.metric("Agriculture", lc.get("Agriculture", 0))
        with m_row1[4]:
            st.metric("Urban", lc.get("Urban", 0))
        with m_row1[5]:
            st.metric("Barren Land", lc.get("Barren_Land", 0))

        st.markdown("---")

        # 2. Format Breakdown Metric Cards
        st.markdown("#### 📁 Counts by Format")
        fc = summary["format_counts"]

        m_row2 = st.columns(5)
        with m_row2[0]:
            st.metric("JPG", fc.get("JPG", 0))
        with m_row2[1]:
            st.metric("JPEG", fc.get("JPEG", 0))
        with m_row2[2]:
            st.metric("PNG", fc.get("PNG", 0))
        with m_row2[3]:
            st.metric("TIFF", fc.get("TIFF", 0))
        with m_row2[4]:
            st.metric("WEBP", fc.get("WEBP", 0))

        st.markdown("---")

        # 3. Visual Analytics Charts (Land Type, Format, Timeline)
        if summary["total_images"] == 0:
            st.info("📊 No satellite images uploaded yet. Upload images in the **'Upload Images'** tab or click **'Load Sample Images'** in the sidebar to populate the analytics charts.")
        else:
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                st.markdown("##### 🌲 Images by Land Type")
                land_chart_data = {
                    "Forest": lc.get("Forest", 0),
                    "Water": lc.get("Water", 0),
                    "Agriculture": lc.get("Agriculture", 0),
                    "Urban": lc.get("Urban", 0),
                    "Barren Land": lc.get("Barren_Land", 0),
                    "Other": lc.get("Other", 0),
                }
                st.bar_chart(land_chart_data, color="#059669")

            with chart_col2:
                st.markdown("##### 📁 Images by Format")
                fmt_chart_data = {
                    "JPG": fc.get("JPG", 0),
                    "JPEG": fc.get("JPEG", 0),
                    "PNG": fc.get("PNG", 0),
                    "TIFF": fc.get("TIFF", 0),
                    "WEBP": fc.get("WEBP", 0),
                }
                st.bar_chart(fmt_chart_data, color="#2563EB")

            # Timeline Chart
            st.markdown("##### 📅 Acquisition Timeline (Images over Time)")
            timeline_data = summary["timeline_counts"]
            if timeline_data:
                st.line_chart(timeline_data, color="#7C3AED")
            else:
                st.caption("No dated imagery available to render acquisition timeline.")

            st.markdown("---")

            # Storage & Catalog Health
            st.markdown("#### 💾 Storage & Metadata Health")
            stg = summary["storage_stats"]
            h_col1, h_col2, h_col3, h_col4 = st.columns(4)
            with h_col1:
                st.metric("Total Catalog Storage", format_file_size(stg["total_bytes"]))
            with h_col2:
                st.metric("Average File Size", format_file_size(int(stg["avg_bytes"])))
            with h_col3:
                st.metric("Complete Metadata", f"{summary['complete_metadata_count']} / {summary['total_images']}")
            with h_col4:
                st.metric("Incomplete Metadata", summary["incomplete_metadata_count"])

    # --------------------------------------------------------------------------
    # TAB 2: Image Gallery
    # --------------------------------------------------------------------------
    with tab_gallery:
        st.markdown("### 🖼️ Cataloged Satellite Imagery")

        if st.session_state.search_results is not None:
            stats = st.session_state.search_stats
            st.info(f"🔍 Displaying **Search Results** for **{stats['field']} = '{stats['query']}'** using **{stats['algorithm']}** ({stats['matches_count']} matches found).")
            if st.button("🔄 Clear Search Results", key="clear_search_gallery"):
                st.session_state.search_results = None
                st.session_state.search_stats = None
                st.rerun()
            render_image_gallery(st.session_state.search_results, context_prefix="search_view")

        elif st.session_state.filter_results is not None:
            fstats = st.session_state.filter_stats
            st.info(f"🎯 Displaying **Filtered Results** ({fstats['matches_count']} matches) | Land: **{fstats['land_type']}**, Format: **{fstats['format']}**, Dates: **{fstats['start_date']}** to **{fstats['end_date']}**.")
            if st.button("🔄 Clear Active Filters", key="clear_filter_gallery"):
                st.session_state.filter_results = None
                st.session_state.filter_stats = None
                st.rerun()
            render_image_gallery(st.session_state.filter_results, context_prefix="filter_view")

        elif st.session_state.sorted_records is not None:
            sstats = st.session_state.sort_stats
            st.info(f"⚡ Displaying **Sorted Catalog** by **{sstats['field']}** via **{sstats['algorithm']}** ({sstats['order']}).")
            if st.button("🔄 Reset to Upload Order", key="clear_sort_gallery"):
                st.session_state.sorted_records = None
                st.session_state.sort_stats = None
                st.rerun()
            render_image_gallery(st.session_state.sorted_records, context_prefix="sorted_view")

        else:
            if not st.session_state.records:
                st.info("No satellite images cataloged yet. Please upload images in the **'Upload Images'** tab or load samples from the sidebar.")
            else:
                render_image_gallery(st.session_state.records, context_prefix="default_view")

    # --------------------------------------------------------------------------
    # TAB 3: Sort Engine
    # --------------------------------------------------------------------------
    with tab_sort:
        st.markdown("### ⚡ Manual DSA Sorting Engine")
        st.caption("Pure from-scratch DSA sorting implementations with real-time performance metrics.")

        if not st.session_state.records:
            st.info("Please upload images or load sample images first.")
        else:
            s_col1, s_col2, s_col3 = st.columns([1.2, 1.2, 1.2])
            with s_col1:
                sort_field = st.selectbox(
                    "Sort By Field",
                    options=["Date & Time", "Image Format", "Land Type", "Image Name", "File Size"],
                    key="sort_select_field",
                )
            with s_col2:
                sort_algo = st.selectbox(
                    "Sorting Algorithm",
                    options=["Merge Sort", "Quick Sort", "Bubble Sort"],
                    key="sort_select_algo",
                )
            with s_col3:
                sort_dir = st.radio(
                    "Sort Direction",
                    options=["Ascending", "Descending"],
                    horizontal=True,
                    key="sort_select_order",
                )

            s_btn_col1, s_btn_col2 = st.columns([1.5, 1.5])
            with s_btn_col1:
                if st.button("🚀 Run Sorting", use_container_width=True, type="primary", key="btn_run_sort"):
                    run_manual_sort(sort_algo, sort_field, (sort_dir == "Ascending"))
                    st.rerun()
            with s_btn_col2:
                if st.session_state.sorted_records is not None:
                    if st.button("🔄 Reset Sort", use_container_width=True, key="btn_reset_sort"):
                        st.session_state.sorted_records = None
                        st.session_state.sort_stats = None
                        st.rerun()

            if st.session_state.sort_stats:
                st.markdown("#### Execution Performance")
                st.markdown('<div class="stat-highlight">', unsafe_allow_html=True)
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Algorithm", st.session_state.sort_stats["algorithm"])
                with m2:
                    st.metric("Field", f"{st.session_state.sort_stats['field']} ({st.session_state.sort_stats['order']})")
                with m3:
                    st.metric("Comparisons", f"{st.session_state.sort_stats['comparisons']:,}")
                with m4:
                    st.metric("Time", f"{st.session_state.sort_stats['time_ms']:.3f} ms")
                st.markdown('</div>', unsafe_allow_html=True)

            info = SORT_ALGO_INFO[sort_algo]
            with st.expander(f"ℹ️ **Algorithm Information: {sort_algo}**", expanded=False):
                st.markdown(f"**Purpose**: {info['purpose']}")
                st.markdown(f"**How It Works**:\n{info['working']}")
                st.markdown("#### Complexity Analysis")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Best Case", info["best_time"])
                with c2:
                    st.metric("Average Case", info["avg_time"])
                with c3:
                    st.metric("Worst Case", info["worst_time"])
                with c4:
                    st.metric("Space", info["space"])
                st.caption(f"**Stability**: {info['stability']}")

    # --------------------------------------------------------------------------
    # TAB 4: Compare Sorting Algorithms (Phase 11 Feature)
    # --------------------------------------------------------------------------
    with tab_compare:
        st.markdown("### ⚔️ Head-to-Head Sorting Algorithm Comparison")
        st.caption("Benchmark Bubble Sort, Merge Sort, and Quick Sort on the currently loaded catalog using 100% manual DSA implementations.")

        if not st.session_state.records:
            st.info("No images currently loaded. Please upload images or load sample images to run benchmarks.")
        else:
            b_col1, b_col2, b_col3 = st.columns([1.5, 1.5, 1.0])
            with b_col1:
                benchmark_field = st.selectbox(
                    "Benchmark Sort Field",
                    options=["Date & Time", "Image Format", "Land Type", "Image Name", "File Size"],
                    key="bm_field_select",
                )
            with b_col2:
                benchmark_dir = st.radio(
                    "Sort Direction",
                    options=["Ascending", "Descending"],
                    horizontal=True,
                    key="bm_dir_select",
                )
            with b_col3:
                st.write("")
                run_bm_btn = st.button("🚀 Run Benchmark", type="primary", use_container_width=True, key="btn_run_benchmark")

            if run_bm_btn or st.session_state.benchmark_results is not None:
                if run_bm_btn:
                    key_field = SORT_FIELD_MAP[benchmark_field]
                    is_asc = (benchmark_dir == "Ascending")
                    bm_res = benchmark_sorting_algorithms(
                        st.session_state.records,
                        key=key_field,
                        ascending=is_asc,
                    )
                    st.session_state.benchmark_results = {
                        "results": bm_res,
                        "field": benchmark_field,
                        "order": benchmark_dir,
                        "dataset_size": len(st.session_state.records),
                    }

                bm_data = st.session_state.benchmark_results
                results_list = bm_data["results"]

                st.markdown("---")
                st.markdown(f"#### 📊 Benchmark Results ({bm_data['dataset_size']} items, Sorted by {bm_data['field']} - {bm_data['order']})")

                # Metric Cards for all 3 algorithms
                card_cols = st.columns(3)
                for idx, r in enumerate(results_list):
                    with card_cols[idx]:
                        with st.container(border=True):
                            st.markdown(f"#### 🏆 {r['algorithm']}")
                            st.metric("Comparisons", f"{r['comparisons']:,}")
                            st.metric("Execution Time", f"{r['time_ms']:.4f} ms ({r['time_us']:.1f} µs)")

                # Comparison Table Display
                st.markdown("##### 📋 Comparative Summary Table")
                table_display = [
                    {
                        "Algorithm": r["algorithm"],
                        "Execution Time (ms)": f"{r['time_ms']:.4f} ms",
                        "Execution Time (µs)": f"{r['time_us']:.1f} µs",
                        "Comparisons Count": r["comparisons"],
                        "Items Sorted": r["item_count"],
                    }
                    for r in results_list
                ]
                st.table(table_display)

                # Visual Comparison Bar Charts
                chart_c1, chart_c2 = st.columns(2)
                with chart_c1:
                    st.markdown("##### ⏱️ Execution Time Comparison (ms)")
                    time_chart_data = {r["algorithm"]: r["time_ms"] for r in results_list}
                    st.bar_chart(time_chart_data, color="#2563EB")
                with chart_c2:
                    st.markdown("##### 🔢 Total Comparisons Comparison")
                    comps_chart_data = {r["algorithm"]: r["comparisons"] for r in results_list}
                    st.bar_chart(comps_chart_data, color="#DC2626")

            # In-Depth Theoretical & Empirical Explanation
            st.markdown("---")
            st.markdown("#### 🎓 Algorithm Performance Analysis & Explanations")

            exp_c1, exp_c2, exp_c3 = st.columns(3)

            with exp_c1:
                with st.container(border=True):
                    st.markdown("##### 🟢 Merge Sort")
                    st.markdown("**Why it is efficient for large datasets:**")
                    st.write(
                        "• **Guaranteed O(n log n)**: Regardless of initial array ordering (best, average, or worst case), "
                        "Merge Sort consistently divides the dataset in half.\n"
                        "• **Stable Ordering**: Preserves the original relative position of records with identical keys.\n"
                        "• **Predictability**: Eliminates the risk of quadratic degradation on adversarial data."
                    )

            with exp_c2:
                with st.container(border=True):
                    st.markdown("##### 🔵 Quick Sort")
                    st.markdown("**Why it performs well on average:**")
                    st.write(
                        "• **Low Constant Overhead**: In-place element partitioning minimizes memory writes and maximizes CPU cache locality.\n"
                        "• **Average O(n log n)**: Balanced partitioning around pivots yields rapid subproblem reduction.\n"
                        "• **Trade-off**: Worst-case is O(n²) if partitions are heavily skewed, though rare on diverse datasets."
                    )

            with exp_c3:
                with st.container(border=True):
                    st.markdown("##### 🟡 Bubble Sort")
                    st.markdown("**Why it is simple but slower:**")
                    st.write(
                        "• **Quadratic O(n²)**: Relies on adjacent element swapping across n - 1 passes, resulting in up to n(n-1)/2 comparisons.\n"
                        "• **Educational Value**: Highly intuitive and easy to trace in college viva examinations.\n"
                        "• **Best Case O(n)**: With our implemented early-exit flag, halts in linear time if data is already sorted."
                    )

    # --------------------------------------------------------------------------
    # TAB 5: Search Images
    # --------------------------------------------------------------------------
    with tab_search:
        st.markdown("### 🔍 Manual DSA Searching Engine")
        st.caption("Search across satellite records using custom Linear Search or pre-sorted Binary Search.")

        if not st.session_state.records:
            st.info("Please upload images or load sample images first.")
        else:
            srch_col1, srch_col2, srch_col3 = st.columns([1.2, 1.2, 2.0])
            with srch_col1:
                search_field = st.selectbox(
                    "Search Field",
                    options=["Image ID", "Image Name", "Land Type", "Image Format", "Date"],
                    key="search_select_field",
                )
            with srch_col2:
                search_algo = st.selectbox(
                    "Search Algorithm",
                    options=["Linear Search", "Binary Search"],
                    key="search_select_algo",
                )
            with srch_col3:
                placeholder_text = {
                    "Image ID": "e.g. SAT001",
                    "Image Name": "e.g. Forest.jpg",
                    "Land Type": "e.g. Forest, Water, Urban",
                    "Image Format": "e.g. jpg, png, tiff, webp",
                    "Date": "e.g. 2026-01-15",
                }.get(search_field, "Enter query...")
                search_query = st.text_input("Query", placeholder=placeholder_text, key="search_text_input")

            srch_btn1, srch_btn2 = st.columns([1.5, 1.5])
            with srch_btn1:
                if st.button("🔎 Search", use_container_width=True, type="primary", key="btn_run_search"):
                    run_manual_search(search_algo, search_field, search_query)
                    st.rerun()
            with srch_btn2:
                if st.session_state.search_results is not None:
                    if st.button("🔄 Clear Search", use_container_width=True, key="btn_clear_search"):
                        st.session_state.search_results = None
                        st.session_state.search_stats = None
                        st.rerun()

            if st.session_state.search_stats:
                st.markdown("#### Search Results & Metrics")
                s_stat = st.session_state.search_stats
                st.markdown('<div class="stat-highlight">', unsafe_allow_html=True)
                sm1, sm2, sm3, sm4 = st.columns(4)
                with sm1:
                    st.metric("Algorithm", s_stat["algorithm"])
                with sm2:
                    st.metric("Query", f"{s_stat['field']}: '{s_stat['query']}'")
                with sm3:
                    st.metric("Comparisons", f"{s_stat['comparisons']:,}")
                with sm4:
                    st.metric("Matches Found", s_stat["matches_count"])
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("##### Matching Records")
                render_image_gallery(st.session_state.search_results, context_prefix="search_tab")

            s_info = SEARCH_ALGO_INFO[search_algo]
            with st.expander(f"ℹ️ **Algorithm Information: {search_algo}**", expanded=False):
                st.markdown(f"**Purpose**: {s_info['purpose']}")
                st.markdown(f"**How It Works**:\n{s_info['working']}")
                st.markdown("#### Complexity Analysis")
                sc1, sc2, sc3, sc4 = st.columns(4)
                with sc1:
                    st.metric("Best Case", s_info["best_time"])
                with sc2:
                    st.metric("Average Case", s_info["avg_time"])
                with sc3:
                    st.metric("Worst Case", s_info["worst_time"])
                with sc4:
                    st.metric("Space", s_info["space"])
                st.caption(f"**Prerequisite**: {s_info['requirement']}")

    # --------------------------------------------------------------------------
    # TAB 6: Multi-Criteria Filters
    # --------------------------------------------------------------------------
    with tab_filter:
        st.markdown("### 🎯 Multi-Criteria Filters")
        st.caption("Filter catalog simultaneously across Land Type, Format, and Date Acquisition ranges.")

        if not st.session_state.records:
            st.info("Please upload images or load sample images first.")
        else:
            f_col1, f_col2, f_col3, f_col4 = st.columns([1.2, 1.2, 1.2, 1.2])
            with f_col1:
                filter_land = st.selectbox("Land Type", options=FILTER_LAND_OPTIONS, index=0, key="filter_land_select")
            with f_col2:
                filter_fmt = st.selectbox("Format", options=FILTER_FORMAT_OPTIONS, index=0, key="filter_fmt_select")
            with f_col3:
                start_d = st.text_input("Start Date (YYYY-MM-DD)", placeholder="e.g. 2026-01-01", key="filter_start_date")
            with f_col4:
                end_d = st.text_input("End Date (YYYY-MM-DD)", placeholder="e.g. 2026-12-31", key="filter_end_date")

            f_btn1, f_btn2 = st.columns([1.5, 1.5])
            with f_btn1:
                if st.button("🎯 Apply Filters", use_container_width=True, type="primary", key="btn_apply_filter"):
                    run_manual_filter(filter_land, filter_fmt, start_d, end_d)
                    st.rerun()
            with f_btn2:
                if st.session_state.filter_results is not None:
                    if st.button("🔄 Reset Filters", use_container_width=True, key="btn_reset_filter"):
                        st.session_state.filter_results = None
                        st.session_state.filter_stats = None
                        st.rerun()

            if st.session_state.filter_stats:
                st.markdown("#### Filter Metrics")
                f_stat = st.session_state.filter_stats
                st.markdown('<div class="stat-highlight">', unsafe_allow_html=True)
                fm1, fm2, fm3, fm4 = st.columns(4)
                with fm1:
                    st.metric("Land Type", f_stat["land_type"])
                with fm2:
                    st.metric("Format", f_stat["format"])
                with fm3:
                    st.metric("Total Comparisons", f"{f_stat['comparisons']:,}")
                with fm4:
                    st.metric("Matching Records", f_stat["matches_count"])
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("##### Filtered Records")
                render_image_gallery(st.session_state.filter_results, context_prefix="filter_tab")

    # --------------------------------------------------------------------------
    # TAB 7: Export & Organize
    # --------------------------------------------------------------------------
    with tab_export:
        st.markdown("### 📦 Metadata Export & Filesystem Organization")
        st.caption("Export satellite metadata as CSV or physically organize imagery into land classification subfolders.")

        if not st.session_state.records:
            st.info("No images in catalog. Please upload images or load samples first.")
        else:
            exp_col1, exp_col2 = st.columns(2)

            with exp_col1:
                with st.container(border=True):
                    st.markdown("#### 📄 Export Metadata as CSV")
                    st.write(f"Generate a structured CSV report for all **{len(st.session_state.records)}** cataloged satellite images.")
                    st.caption("Includes: Image ID, Name, Date, Time, Land Type, Format, Width, Height, File Size, and File Path.")

                    csv_data = generate_metadata_csv(st.session_state.records)

                    st.download_button(
                        label="📥 Download Metadata CSV",
                        data=csv_data,
                        file_name="satellite_imagery_metadata.csv",
                        mime="text/csv",
                        use_container_width=True,
                        type="primary",
                        key="btn_download_csv",
                    )

                    with st.expander("👁️ Preview CSV Content", expanded=False):
                        st.code(csv_data[:1200] + ("\n... [truncated]" if len(csv_data) > 1200 else ""), language="csv")

            with exp_col2:
                with st.container(border=True):
                    st.markdown("#### 📁 Organize Images by Land Type")
                    st.write("Copies catalog images into structured folders without modifying originals:")
                    st.code(
                        "Organized/\n├── Forest/\n├── Water/\n├── Agriculture/\n├── Urban/\n├── Barren_Land/\n└── Other/",
                        language="text",
                    )

                    if st.button("🚀 Organize Images into Folders", use_container_width=True, key="btn_run_organize"):
                        summary = organize_images_by_land_type(
                            st.session_state.records,
                            output_root=ORGANIZED_DIR,
                        )
                        st.session_state.organization_summary = summary
                        st.rerun()

            if st.session_state.organization_summary:
                org_summary = st.session_state.organization_summary
                st.markdown("---")
                st.markdown("#### 📁 Organization Results")
                st.success(f"✅ Successfully organized **{org_summary['total_copied']}** satellite images into `{org_summary['output_dir']}`!")

                counts = org_summary["category_counts"]
                c_cols = st.columns(6)
                for idx, (cat_name, cat_count) in enumerate(counts.items()):
                    with c_cols[idx]:
                        st.metric(f"📁 {cat_name}", cat_count)

                if org_summary["errors"]:
                    st.warning("Some files could not be copied:")
                    for err in org_summary["errors"]:
                        st.write(f"• {err}")

    # --------------------------------------------------------------------------
    # TAB 8: Upload Images
    # --------------------------------------------------------------------------
    with tab_upload:
        st.markdown("### 📤 Upload Satellite Imagery")
        st.caption("Supported formats: **JPG, JPEG, PNG, TIFF, WEBP**. Filename format: `YYYY-MM-DD_HH-MM_LandType.ext`")

        uploaded_files = st.file_uploader(
            "Select satellite images to upload",
            type=["jpg", "jpeg", "png", "tiff", "tif", "webp"],
            accept_multiple_files=True,
            help="Upload multiple satellite images. Metadata will be extracted from filenames or entered manually.",
            key="tab_file_uploader",
        )

        if uploaded_files:
            newly_processed = 0
            error_messages = []

            for uploaded_file in uploaded_files:
                upload_key = f"{uploaded_file.name}_{uploaded_file.size}"
                if upload_key in st.session_state.processed_upload_keys:
                    continue

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
                st.session_state.sorted_records = None
                st.session_state.sort_stats = None
                st.session_state.search_results = None
                st.session_state.filter_results = None
                st.session_state.benchmark_results = None
                st.session_state.organization_summary = None
                st.success(f"Successfully cataloged {newly_processed} image(s)!")
                st.rerun()

            for err in error_messages:
                st.error(err)


if __name__ == "__main__":
    main()
