"""Test suite for Scriptwriter Linter using standard unittest."""

import unittest
from engine.linter import ScriptLinter


class TestScriptLinter(unittest.TestCase):
    def setUp(self):
        self.linter = ScriptLinter()

    def test_catches_client_specified_bad_examples(self):
        # User's exact negative examples
        bad_sample_1 = "An eerie silence draped itself over the sleepy town."
        report_1 = self.linter.audit_text(bad_sample_1)
        types_1 = [v.violation_type for v in report_1.violations]
        self.assertTrue("BANNED_WORD" in types_1 or "PERSONIFICATION" in types_1)

        bad_sample_2 = "The moon cast its silver veil across the lonely stretch of asphalt."
        report_2 = self.linter.audit_text(bad_sample_2)
        types_2 = [v.violation_type for v in report_2.violations]
        self.assertTrue("PERSONIFICATION" in types_2 or "BANNED_WORD" in types_2)

        bad_sample_3 = "An icy wave of terror gripped him as he gazed upon the mysterious figure."
        report_3 = self.linter.audit_text(bad_sample_3)
        types_3 = [v.violation_type for v in report_3.violations]
        self.assertTrue("PERSONIFICATION" in types_3)

    def test_catches_ai_suspense_cliches(self):
        sample = "Little did he know, what happened next would shock the town. Fast forward to three days later."
        report = self.linter.audit_text(sample)
        self.assertTrue(any(v.violation_type == "AI_TRANSITION" for v in report.violations))

    def test_catches_overly_long_sentences(self):
        long_sentence = (
            "He walked down the long gravel driveway because his truck had broken down three miles "
            "outside of town and he was trying to find a telephone to call his brother before the sun "
            "went down and the cold air started freezing his hands."
        )
        report = self.linter.audit_text(long_sentence)
        self.assertTrue(any(v.violation_type == "SENTENCE_TOO_LONG" for v in report.violations))

    def test_approves_plain_spoken_clean_examples(self):
        clean_sample = "The town was quiet. The moon lit the road. He was frightened when he saw the figure."
        report = self.linter.audit_text(clean_sample)
        critical_violations = [
            v for v in report.violations
            if v.violation_type in ["BANNED_WORD", "PERSONIFICATION", "AI_TRANSITION"]
        ]
        self.assertEqual(len(critical_violations), 0)

    def test_detects_pronunciation_guides(self):
        sample = "Officer Lonnie Zamora (Zuh-MOR-uh) was driving near Socorro (suh-KOR-oh) when he saw the craft."
        report = self.linter.audit_text(sample)
        self.assertGreaterEqual(len(report.pronunciation_guides_found), 2)
        self.assertTrue(any("Socorro" in pg for pg in report.pronunciation_guides_found))


if __name__ == "__main__":
    unittest.main()
