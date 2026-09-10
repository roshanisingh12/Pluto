"""
dsa/sorting.py

Manual implementations of classic Data Structures & Algorithms (DSA) sorting
techniques for ImageRecord collections in a satellite image catalog.

Supported Algorithms:
1. Merge Sort (Divide and Conquer, Stable)
2. Quick Sort (Divide and Conquer with Partitioning)
3. Bubble Sort (Comparison-based Adjacent Element Swapping)

Supported Sorting Keys:
- "datetime" / "date & time" / "date" / "time"
- "image_format" / "format"
- "land_type" / "land type"
- "image_name" / "name"
- "file_size" / "size"
- Custom callable functions

Note:
- All sorting algorithms are manually implemented from scratch without using
  Python's built-in sorted(), list.sort(), or external library sorting routines.
- Each algorithm returns a tuple: (sorted_records, comparison_count).
- The original input list is never modified; a new sorted list is returned.
"""

from datetime import datetime as _dt
from typing import List, Tuple, Any, Callable, Union, Optional
import sys
import os

# Ensure the root project directory is on sys.path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.image_record import ImageRecord


# ==============================================================================
# Helper Functions: Key Extraction & Comparison Logic
# ==============================================================================

def get_record_key(record: ImageRecord, key: Union[str, Callable[[ImageRecord], Any]]) -> Any:
    """
    Extracts the comparable value from an ImageRecord based on the requested key.

    Supported string keys (case-insensitive and whitespace/underscore-agnostic):
    - "date & time", "datetime", "date_time", "date", "time" (parsed as real datetime)
    - "image_format", "format", "ext", "extension"
    - "land_type", "land type", "landtype"
    - "image_name", "image name", "name", "filename"
    - "file_size", "file size", "size", "bytes"

    Or a custom callable: key(record) -> Any
    """
    if callable(key):
        return key(record)

    if not isinstance(key, str):
        raise TypeError(f"Sort key must be a string or callable, got {type(key).__name__}")

    normalized = key.strip().lower().replace(" ", "").replace("_", "").replace("&", "")

    if normalized in ("datetime", "dateandtime", "date", "time"):
        if record.datetime:
            try:
                clean_dt = record.datetime.strip().replace(":", "-")
                parts = clean_dt.split()
                if len(parts) == 2:
                    return _dt.strptime(f"{parts[0]} {parts[1]}", "%Y-%m-%d %H-%M")
            except Exception:
                pass
        if record.date:
            try:
                t_str = (record.time or "00-00").replace(":", "-")
                return _dt.strptime(f"{record.date} {t_str}", "%Y-%m-%d %H-%M")
            except Exception:
                pass
        return _dt.min


    elif normalized in ("imageformat", "format", "ext", "extension"):
        return (record.image_format or "").lower()

    elif normalized in ("landtype", "land", "type"):
        return (record.land_type or "").lower()

    elif normalized in ("imagename", "name", "filename"):
        return (record.image_name or "").lower()

    elif normalized in ("filesize", "size", "bytes"):
        return record.file_size if record.file_size is not None else 0

    # Fallback to direct attribute lookup on the ImageRecord
    if hasattr(record, key):
        val = getattr(record, key)
        return val if val is not None else ""

    raise ValueError(f"Unsupported sort key '{key}'. Supported: 'datetime', 'image_format', 'land_type', 'image_name', 'file_size'.")


def _resolve_order(ascending: bool = True, reverse: Optional[bool] = None) -> bool:
    """Resolve ascending / reverse flags into a single boolean (True for ascending)."""
    if reverse is not None:
        return not reverse
    return bool(ascending)


# ==============================================================================
# 1. Bubble Sort
# ==============================================================================

def bubble_sort(
    records: List[ImageRecord],
    key: Union[str, Callable[[ImageRecord], Any]] = "datetime",
    ascending: bool = True,
    reverse: Optional[bool] = None,
) -> Tuple[List[ImageRecord], int]:
    """
    Sorts a list of ImageRecord objects using the Bubble Sort algorithm.

    How Bubble Sort works:
    1. Iterate through the list multiple times.
    2. In each pass, compare adjacent elements: arr[j] and arr[j + 1].
    3. If they are in the wrong order, swap them.
    4. With each pass, the largest (or smallest in descending) unsorted element
       "bubbles up" to its correct final position at the end.
    5. Optimization: If no swaps occur in a pass, the list is already sorted,
       allowing an early exit.

    Time Complexity:
    - Best Case (already sorted): O(n)
    - Average Case: O(n^2)
    - Worst Case (reverse sorted): O(n^2)

    Space Complexity:
    - O(n) for returning a new sorted list (O(1) auxiliary space beyond the copy).

    Parameters:
    - records: List of ImageRecord objects to sort.
    - key: Metadata attribute name or callable key extractor.
    - ascending: True for ascending order, False for descending.
    - reverse: Optional alias; if True, sorts descending.

    Returns:
    - Tuple of (sorted_records_list, total_comparisons_count)
    """
    is_asc = _resolve_order(ascending, reverse)
    # Create a shallow copy to prevent corrupting the caller's original list
    arr = list(records)
    n = len(arr)
    comparisons = 0

    if n <= 1:
        return arr, comparisons

    # Outer loop runs n - 1 passes
    for i in range(n - 1):
        swapped = False

        # Inner loop compares adjacent pairs up to the unsorted boundary
        for j in range(n - 1 - i):
            val_a = get_record_key(arr[j], key)
            val_b = get_record_key(arr[j + 1], key)
            comparisons += 1

            # Determine whether adjacent elements are out of order
            need_swap = (val_a > val_b) if is_asc else (val_a < val_b)

            if need_swap:
                # Swap adjacent elements
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True

        # Early termination: if no swaps occurred, array is already sorted
        if not swapped:
            break

    return arr, comparisons


# ==============================================================================
# 2. Merge Sort
# ==============================================================================

def merge_sort(
    records: List[ImageRecord],
    key: Union[str, Callable[[ImageRecord], Any]] = "datetime",
    ascending: bool = True,
    reverse: Optional[bool] = None,
) -> Tuple[List[ImageRecord], int]:
    """
    Sorts a list of ImageRecord objects using the Merge Sort algorithm.

    How Merge Sort works:
    1. Divide: Split the list into two halves around the midpoint.
    2. Conquer: Recursively sort both the left and right halves.
    3. Combine (Merge): Merge the two sorted sublists back together in order
       by repeatedly comparing their smallest remaining elements.

    Time Complexity:
    - Best Case: O(n log n)
    - Average Case: O(n log n)
    - Worst Case: O(n log n)

    Space Complexity:
    - O(n) auxiliary space for sublist division and merging.

    Stability:
    - Stable sorting algorithm (preserves original order of equal keys).

    Parameters:
    - records: List of ImageRecord objects to sort.
    - key: Metadata attribute name or callable key extractor.
    - ascending: True for ascending order, False for descending.
    - reverse: Optional alias; if True, sorts descending.

    Returns:
    - Tuple of (sorted_records_list, total_comparisons_count)
    """
    is_asc = _resolve_order(ascending, reverse)
    # Work on a copy of the list to keep original input untouched
    arr = list(records)

    def _merge_sort_recursive(sublist: List[ImageRecord]) -> Tuple[List[ImageRecord], int]:
        # Base case: 0 or 1 element is already sorted
        if len(sublist) <= 1:
            return sublist, 0

        # Step 1: Divide into left and right sublists
        mid = len(sublist) // 2
        left_half = sublist[:mid]
        right_half = sublist[mid:]

        # Step 2: Recursively sort both halves
        sorted_left, left_comps = _merge_sort_recursive(left_half)
        sorted_right, right_comps = _merge_sort_recursive(right_half)

        # Step 3: Merge the two sorted halves
        merged = []
        i = 0
        j = 0
        merge_comps = 0

        while i < len(sorted_left) and j < len(sorted_right):
            val_left = get_record_key(sorted_left[i], key)
            val_right = get_record_key(sorted_right[j], key)
            merge_comps += 1

            # Decide which element to take next based on sort order
            # Use <= or >= to preserve stability for equal elements
            take_left = (val_left <= val_right) if is_asc else (val_left >= val_right)

            if take_left:
                merged.append(sorted_left[i])
                i += 1
            else:
                merged.append(sorted_right[j])
                j += 1

        # Append remaining elements from either half (no further comparisons needed)
        while i < len(sorted_left):
            merged.append(sorted_left[i])
            i += 1

        while j < len(sorted_right):
            merged.append(sorted_right[j])
            j += 1

        total_comps = left_comps + right_comps + merge_comps
        return merged, total_comps

    return _merge_sort_recursive(arr)


# ==============================================================================
# 3. Quick Sort
# ==============================================================================

def quick_sort(
    records: List[ImageRecord],
    key: Union[str, Callable[[ImageRecord], Any]] = "datetime",
    ascending: bool = True,
    reverse: Optional[bool] = None,
) -> Tuple[List[ImageRecord], int]:
    """
    Sorts a list of ImageRecord objects using the Quick Sort algorithm.

    How Quick Sort works:
    1. Pivot Selection: Choose an element from the array as the pivot (e.g. last element).
    2. Partitioning (Lomuto Partition Scheme):
       - Rearrange elements such that all elements with key smaller than (or equal to)
         the pivot are moved to the left of the pivot.
       - All elements with key greater than the pivot are moved to the right.
    3. Recursion: Recursively apply quick sort to the left partition and right partition.

    Time Complexity:
    - Best Case: O(n log n)
    - Average Case: O(n log n)
    - Worst Case (poor pivot selection): O(n^2)

    Space Complexity:
    - O(log n) recursion call stack space (O(n) worst case).
    - O(n) for the shallow copy returned.

    Parameters:
    - records: List of ImageRecord objects to sort.
    - key: Metadata attribute name or callable key extractor.
    - ascending: True for ascending order, False for descending.
    - reverse: Optional alias; if True, sorts descending.

    Returns:
    - Tuple of (sorted_records_list, total_comparisons_count)
    """
    is_asc = _resolve_order(ascending, reverse)
    # Work on a copy of the list so the caller's input list is unmodified
    arr = list(records)
    total_comparisons = 0

    def _partition(low: int, high: int) -> int:
        """
        Lomuto Partitioning:
        Takes the element at 'high' as pivot, places pivot at correct sorted
        position, and places all smaller (or larger if descending) elements
        to the left of pivot.
        """
        nonlocal total_comparisons
        pivot_val = get_record_key(arr[high], key)

        # i points to the boundary of elements placed in the correct partition
        i = low - 1

        for j in range(low, high):
            current_val = get_record_key(arr[j], key)
            total_comparisons += 1

            # Condition for placing arr[j] before the pivot
            should_place_before = (current_val <= pivot_val) if is_asc else (current_val >= pivot_val)

            if should_place_before:
                i += 1
                # Swap elements into the left partition
                arr[i], arr[j] = arr[j], arr[i]

        # Place the pivot in its final correct position
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1

    def _quick_sort_recursive(low: int, high: int) -> None:
        if low < high:
            # Partition the array and get pivot index
            pivot_index = _partition(low, high)

            # Recursively sort elements before and after partition
            _quick_sort_recursive(low, pivot_index - 1)
            _quick_sort_recursive(pivot_index + 1, high)

    if len(arr) > 1:
        _quick_sort_recursive(0, len(arr) - 1)

    return arr, total_comparisons
