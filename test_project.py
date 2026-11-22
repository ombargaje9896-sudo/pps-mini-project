"""Tests for the grading and sample-data logic (no external dependencies)."""

import json
import unittest
from pathlib import Path

from main import SUBJECTS, calculate_result, find_student


class StudentMarksTests(unittest.TestCase):
    def test_top_grade(self):
        marks = {subject: 95 for subject in SUBJECTS}
        self.assertEqual(calculate_result(marks), (475, 95.0, "A+", "PASS"))

    def test_one_failed_subject_fails_overall(self):
        marks = {subject: 90 for subject in SUBJECTS}
        marks["Chemistry"] = 32
        self.assertEqual(calculate_result(marks), (392, 78.4, "F", "FAIL"))

    def test_passing_at_35(self):
        marks = {subject: 35 for subject in SUBJECTS}
        self.assertEqual(calculate_result(marks), (175, 35.0, "D", "PASS"))

    def test_invalid_roll_is_not_found(self):
        students = [{"roll_no": "101"}]
        self.assertIsNone(find_student(students, "999"))

    def test_sample_file_has_five_students(self):
        path = Path(__file__).resolve().parent / "sample_students.json"
        students = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(students), 5)
        self.assertEqual(len({s["roll_no"] for s in students}), 5)
        self.assertEqual(find_student(students, "104")["name"], "Isha Kulkarni")


if __name__ == "__main__":
    unittest.main()
