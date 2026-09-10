"""
dsa/hashing.py

Manual implementation of a Hash Table Data Structure using Separate Chaining
for collision resolution.

Purpose:
Provides O(1) average-time key-value lookup, insertion, and deletion for
ImageRecord objects using their unique `image_id` (e.g., 'SAT001' -> ImageRecord).

Key DSA Concepts:
1. Hash Function: Converts arbitrary string keys into integer bucket indices.
2. Collision Resolution: Separate Chaining (each bucket holds a chain/list of (key, value) pairs).
3. Dynamic Resizing (Rehashing): Automatically doubles capacity when load factor > 0.75.
"""

from typing import List, Tuple, Any, Optional, Iterator
import sys
import os

# Ensure the root project directory is on sys.path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.image_record import ImageRecord


class ImageHashTable:
    """
    A manual Hash Table implementing Separate Chaining for ImageRecord storage.

    Complexity Analysis:
    --------------------
    Operation | Average Case | Worst Case
    --------------------------------------
    Insert    | O(1)         | O(n) (all keys hash to the same bucket)
    Search    | O(1)         | O(n) (all keys hash to the same bucket)
    Delete    | O(1)         | O(n) (all keys hash to the same bucket)
    Space     | O(n + m) where m is table capacity, n is number of items.

    Explanation for Viva:
    - Average Case O(1): With a uniform hash function and load factor <= 0.75,
      each bucket contains very few elements (approx. O(1) chain length on average).
    - Worst Case O(n): Occurs if the hash function produces identical indices
      for all keys (extreme hash collision), turning the bucket into a linear list.
    """

    def __init__(self, initial_capacity: int = 16, load_factor_threshold: float = 0.75):
        """
        Initialize the Hash Table.

        Parameters:
        - initial_capacity: Initial number of buckets (default 16).
        - load_factor_threshold: Threshold ratio (size / capacity) triggering dynamic resize.
        """
        if initial_capacity <= 0:
            raise ValueError("Initial capacity must be greater than 0.")

        self.capacity: int = initial_capacity
        self.load_factor_threshold: float = load_factor_threshold
        self.size: int = 0
        # Initialize buckets as empty lists for Separate Chaining
        self.buckets: List[List[Tuple[str, Any]]] = [[] for _ in range(self.capacity)]

    # ==========================================================================
    # Hash Function
    # ==========================================================================

    def _hash(self, key: str) -> int:
        """
        Computes the bucket index for a string key using a polynomial rolling hash.

        Formula:
            hash_val = (hash_val * 31 + ord(char)) % capacity
        Multiplier 31 is an odd prime that produces good distribution for string keys.
        """
        hash_val = 0
        for char in str(key):
            hash_val = (hash_val * 31 + ord(char))
        return hash_val % self.capacity

    # ==========================================================================
    # Core Operations: Insert, Search, Delete
    # ==========================================================================

    def insert(self, key: str, value: Any) -> None:
        """
        Inserts a (key, value) pair into the hash table.
        If the key already exists, updates its value.
        Automatically rehashes and doubles capacity when load factor > threshold.
        """
        if key is None:
            raise ValueError("Key cannot be None.")

        str_key = str(key)
        index = self._hash(str_key)
        bucket = self.buckets[index]

        # Check if key already exists in this bucket chain (update existing)
        for i in range(len(bucket)):
            if bucket[i][0] == str_key:
                bucket[i] = (str_key, value)
                return

        # Key not present: insert new pair into the bucket chain
        bucket.append((str_key, value))
        self.size += 1

        # Check if rehashing / resizing is needed
        if self.load_factor() > self.load_factor_threshold:
            self._resize(self.capacity * 2)

    def search(self, key: str) -> Optional[Any]:
        """
        Searches for a key in the hash table.

        Returns:
        - The associated value (e.g., ImageRecord) if found.
        - None if the key does not exist.
        """
        if key is None:
            return None

        str_key = str(key)
        index = self._hash(str_key)
        bucket = self.buckets[index]

        # Scan the chain at this bucket
        for k, val in bucket:
            if k == str_key:
                return val

        return None

    def delete(self, key: str) -> bool:
        """
        Deletes a (key, value) pair from the hash table by key.

        Returns:
        - True if the key was found and removed.
        - False if the key was not found.
        """
        if key is None:
            return False

        str_key = str(key)
        index = self._hash(str_key)
        bucket = self.buckets[index]

        for i in range(len(bucket)):
            if bucket[i][0] == str_key:
                del bucket[i]
                self.size -= 1
                return True

        return False

    # ==========================================================================
    # Dynamic Resizing & Rehashing
    # ==========================================================================

    def _resize(self, new_capacity: int) -> None:
        """
        Resizes the hash table and re-hashes all existing key-value pairs into new buckets.
        """
        old_buckets = self.buckets
        self.capacity = new_capacity
        self.buckets = [[] for _ in range(new_capacity)]
        self.size = 0

        for bucket in old_buckets:
            for k, val in bucket:
                self.insert(k, val)

    # ==========================================================================
    # Helper & Utility Methods
    # ==========================================================================

    def load_factor(self) -> float:
        """Returns the current load factor: (number of items / capacity)."""
        return self.size / self.capacity

    def get(self, key: str, default: Any = None) -> Any:
        """Convenience method returning default value if key is not found."""
        result = self.search(key)
        return result if result is not None else default

    def contains(self, key: str) -> bool:
        """Checks if a key exists in the hash table."""
        return self.search(key) is not None

    def keys(self) -> List[str]:
        """Returns a list of all keys in the hash table."""
        all_keys = []
        for bucket in self.buckets:
            for k, _ in bucket:
                all_keys.append(k)
        return all_keys

    def values(self) -> List[Any]:
        """Returns a list of all values in the hash table."""
        all_values = []
        for bucket in self.buckets:
            for _, val in bucket:
                all_values.append(val)
        return all_values

    def items(self) -> List[Tuple[str, Any]]:
        """Returns a list of all (key, value) pairs."""
        all_items = []
        for bucket in self.buckets:
            for item in bucket:
                all_items.append(item)
        return all_items

    def clear(self) -> None:
        """Clears all entries from the hash table."""
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0

    def populate_from_records(self, records: List[ImageRecord]) -> None:
        """
        Populates the hash table with a list of ImageRecord objects using their `image_id` as key.
        """
        for record in records:
            if record and record.image_id:
                self.insert(record.image_id, record)

    # Python Magic Methods for natural dict-like syntax:
    def __setitem__(self, key: str, value: Any) -> None:
        self.insert(key, value)

    def __getitem__(self, key: str) -> Any:
        val = self.search(key)
        if val is None:
            raise KeyError(f"Key '{key}' not found in ImageHashTable.")
        return val

    def __delitem__(self, key: str) -> None:
        if not self.delete(key):
            raise KeyError(f"Key '{key}' not found in ImageHashTable.")

    def __contains__(self, key: str) -> bool:
        return self.contains(key)

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return f"<ImageHashTable size={self.size} capacity={self.capacity} load_factor={self.load_factor():.2f}>"
