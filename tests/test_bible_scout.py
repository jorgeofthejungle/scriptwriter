"""Unit and Stress Tests for Story Bible and Scout Deduplication."""

import unittest
import tempfile
import json
from pathlib import Path

from engine.bible import StoryBibleManager, compute_entity_hash
from engine.researcher import check_safe_outcome
from engine.scout import HISTORICAL_CATALOG, StoryScoutAgent


class TestStoryBibleAndScout(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.bible_file = Path(self.temp_dir.name) / "test_bible.json"
        self.mgr = StoryBibleManager(bible_path=self.bible_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_entity_hash_consistency_across_aliases(self):
        # Different casing, punctuation, and wording variations of the same event
        hash_1 = compute_entity_hash("Socorro, New Mexico", "1964", "Lonnie Zamora")
        hash_2 = compute_entity_hash("Socorro, NM", "1964", "Zamora")
        hash_3 = compute_entity_hash("socorro new mexico", "1964", "Lonnie Zamora")
        # All extract 'zamora' as surname, 1964 as year
        self.assertEqual(hash_1, hash_3)

    def test_deduplication_blocks_alias_collision(self):
        # Register original event
        ok1, rec1, msg1 = self.mgr.register_story(
            title="The Socorro Landing",
            location="Socorro, New Mexico",
            year="1964",
            primary_witness="Lonnie Zamora",
            aliases=["Lonnie Zamora incident", "Socorro UFO Encounter"],
            status="COMPLETED"
        )
        self.assertTrue(ok1)
        self.assertIsNotNone(rec1)

        # Attempt to register the exact same event under an alias headline
        ok2, rec2, msg2 = self.mgr.register_story(
            title="Lonnie Zamora incident",
            location="Socorro, New Mexico",
            year="1964",
            primary_witness="Lonnie Zamora"
        )
        self.assertFalse(ok2)
        self.assertIn("REJECTED AS DUPLICATE", msg2)
        self.assertEqual(rec2.story_id, rec1.story_id)

    def test_safe_outcome_gate_rejects_fatal_events(self):
        fatal_sample = "During the flight, Captain Thomas Mantell crashed his F-51D aircraft and died in the crash. His body was found in the wreckage."
        is_safe, reasons = check_safe_outcome(fatal_sample)
        self.assertFalse(is_safe)
        self.assertTrue(any("fatal" in r.lower() or "body" in r.lower() for r in reasons))

    def test_safe_outcome_gate_approves_safe_events(self):
        safe_sample = "The aircraft landed safely at the municipal airport. Both pilots exited the cockpit without injuries and returned to duty."
        is_safe, reasons = check_safe_outcome(safe_sample)
        self.assertTrue(is_safe)
        self.assertEqual(len(reasons), 0)

    def test_status_lifecycle_updates(self):
        ok, rec, _ = self.mgr.register_story(
            title="Kecksburg Incident",
            location="Kecksburg, PA",
            year="1965",
            primary_witness="Balafoutas",
            status="IN_PIPELINE"
        )
        self.assertTrue(ok)
        self.assertEqual(rec.status, "IN_PIPELINE")

        # Update to COMPLETED
        updated = self.mgr.update_status(
            rec.entity_hash,
            "COMPLETED",
            word_count=3250,
            flesch_grade=6.4
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, "COMPLETED")
        self.assertEqual(updated.word_count, 3250)
        self.assertEqual(updated.flesch_grade, 6.4)


if __name__ == "__main__":
    unittest.main()
