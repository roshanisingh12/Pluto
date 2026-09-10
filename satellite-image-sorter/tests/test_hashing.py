"""
tests/test_hashing.py

Unit tests for manual Hash Table data structure in dsa/hashing.py (ImageHashTable).
"""

import unittest
from models.image_record import ImageRecord
from dsa.hashing import ImageHashTable


class TestImageHashTable(unittest.TestCase):
    """Test suite for manual ImageHashTable with separate chaining."""

    def setUp(self):
        """Create sample ImageRecord fixtures."""
        self.ht = ImageHashTable(initial_capacity=8)
        self.rec1 = ImageRecord(image_id="SAT001", image_name="Forest.png", land_type="Forest")
        self.rec2 = ImageRecord(image_id="SAT002", image_name="Water.jpg", land_type="Water")
        self.rec3 = ImageRecord(image_id="SAT003", image_name="Urban.tiff", land_type="Urban")

    # ------------------------------------------------------------------
    # 1. Basic Insert & Search
    # ------------------------------------------------------------------
    def test_insert_and_search(self):
        """Verify inserting and retrieving elements by image_id."""
        self.ht.insert("SAT001", self.rec1)
        self.ht.insert("SAT002", self.rec2)

        self.assertEqual(len(self.ht), 2)
        self.assertEqual(self.ht.search("SAT001"), self.rec1)
        self.assertEqual(self.ht.search("SAT002"), self.rec2)
        self.assertIsNone(self.ht.search("SAT999"))

    # ------------------------------------------------------------------
    # 2. Key Update
    # ------------------------------------------------------------------
    def test_insert_update_existing_key(self):
        """Verify inserting with an existing key updates the value without increasing size."""
        self.ht.insert("SAT001", self.rec1)
        updated_rec = ImageRecord(image_id="SAT001", image_name="UpdatedForest.png", land_type="Forest")
        self.ht.insert("SAT001", updated_rec)

        self.assertEqual(len(self.ht), 1)
        self.assertEqual(self.ht.search("SAT001").image_name, "UpdatedForest.png")

    # ------------------------------------------------------------------
    # 3. Delete Operation
    # ------------------------------------------------------------------
    def test_delete(self):
        """Verify deleting an existing key and attempting to delete nonexistent key."""
        self.ht.insert("SAT001", self.rec1)
        self.ht.insert("SAT002", self.rec2)

        # Successful deletion
        self.assertTrue(self.ht.delete("SAT001"))
        self.assertEqual(len(self.ht), 1)
        self.assertIsNone(self.ht.search("SAT001"))

        # Deleting nonexistent key
        self.assertFalse(self.ht.delete("SAT001"))
        self.assertFalse(self.ht.delete("NON_EXISTENT"))

    # ------------------------------------------------------------------
    # 4. Collision Handling via Separate Chaining
    # ------------------------------------------------------------------
    def test_collision_handling(self):
        """
        Verify that multiple items that hash to the same bucket index are
        both preserved and retrievable via separate chaining.
        """
        small_ht = ImageHashTable(initial_capacity=2, load_factor_threshold=10.0)
        # Inserting multiple items into a 2-bucket table guarantees collisions
        records = [
            ImageRecord(image_id=f"SAT00{i}", image_name=f"Img{i}.png")
            for i in range(1, 10)
        ]
        for r in records:
            small_ht.insert(r.image_id, r)

        self.assertEqual(len(small_ht), 9)
        for r in records:
            found = small_ht.search(r.image_id)
            self.assertIsNotNone(found)
            self.assertEqual(found.image_id, r.image_id)

    # ------------------------------------------------------------------
    # 5. Dynamic Resizing / Rehashing
    # ------------------------------------------------------------------
    def test_dynamic_resizing(self):
        """Verify the table doubles capacity and rehashes when load factor threshold is exceeded."""
        initial_cap = self.ht.capacity
        # Default capacity = 8, threshold = 0.75 (resize occurs at > 6 items)
        for i in range(10):
            self.ht.insert(f"KEY_{i}", f"VAL_{i}")

        self.assertGreater(self.ht.capacity, initial_cap)
        self.assertEqual(len(self.ht), 10)
        for i in range(10):
            self.assertEqual(self.ht.search(f"KEY_{i}"), f"VAL_{i}")

    # ------------------------------------------------------------------
    # 6. Dict-like Syntax & Helpers
    # ------------------------------------------------------------------
    def test_magic_methods_and_helpers(self):
        """Verify __getitem__, __setitem__, __delitem__, 'in', keys(), values(), items()."""
        self.ht["SAT001"] = self.rec1
        self.ht["SAT002"] = self.rec2

        self.assertEqual(self.ht["SAT001"], self.rec1)
        self.assertTrue("SAT001" in self.ht)
        self.assertFalse("SAT999" in self.ht)

        # Helper getters
        self.assertEqual(self.ht.get("SAT001"), self.rec1)
        self.assertEqual(self.ht.get("SAT999", "DEFAULT"), "DEFAULT")

        # Keys, values, items
        self.assertCountEqual(self.ht.keys(), ["SAT001", "SAT002"])
        self.assertEqual(len(self.ht.values()), 2)
        self.assertEqual(len(self.ht.items()), 2)

        # __delitem__
        del self.ht["SAT001"]
        self.assertFalse("SAT001" in self.ht)
        with self.assertRaises(KeyError):
            _ = self.ht["SAT001"]
        with self.assertRaises(KeyError):
            del self.ht["SAT001"]

    # ------------------------------------------------------------------
    # 7. Populate from ImageRecord Collection
    # ------------------------------------------------------------------
    def test_populate_from_records(self):
        """Verify batch population from a list of ImageRecords."""
        records = [self.rec1, self.rec2, self.rec3]
        self.ht.populate_from_records(records)

        self.assertEqual(len(self.ht), 3)
        self.assertEqual(self.ht.search("SAT001"), self.rec1)
        self.assertEqual(self.ht.search("SAT002"), self.rec2)
        self.assertEqual(self.ht.search("SAT003"), self.rec3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
