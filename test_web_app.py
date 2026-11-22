"""Integration tests for the EduTrack browser dashboard (no pip installs)."""
import http.client
import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import main
import web_app


class DashboardValidationTests(unittest.TestCase):
    def test_normalises_roll_and_marks(self):
        raw = {"roll_no": "00106", "name": " Test Student ", "course": " CSE AI & ML ",
               "marks": {subject: "85" for subject in main.SUBJECTS}}
        student = web_app.normalise_student(raw)
        self.assertEqual(student["roll_no"], "106")
        self.assertEqual(student["name"], "Test Student")
        self.assertEqual(student["marks"]["Python"], 85)

    def test_rejects_missing_marks(self):
        with self.assertRaisesRegex(ValueError, "marks"):
            web_app.normalise_student({"roll_no": "1", "name": "Any Student",
                                       "course": "AI and ML", "marks": {}})

    def test_rejects_boolean_marks(self):
        with self.assertRaisesRegex(ValueError, "marks"):
            web_app.normalise_student({"roll_no": "1", "name": "Any Student",
                                       "course": "AI and ML", "marks": {s: True for s in main.SUBJECTS}})

    def test_pass_rule_in_stats(self):
        students = [{"roll_no": "1", "name": "First", "course": "AI",
                     "marks": {s: 95 for s in main.SUBJECTS}},
                    {"roll_no": "2", "name": "Second", "course": "AI",
                     "marks": {**{s: 89 for s in main.SUBJECTS}, "Chemistry": 20}}]
        result = web_app.get_stats(students)
        self.assertEqual(result["pass_rate"], 50.0)
        self.assertEqual(result["topper"]["name"], "First")


class DashboardHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.data_path = Path(cls.tmp.name) / "students.json"
        cls.csv_path = Path(cls.tmp.name) / "results.csv"
        cls.data_path.write_text("[]", encoding="utf-8")
        cls.data_patch = patch.object(main, "DATA_FILE", cls.data_path)
        cls.csv_patch = patch.object(web_app, "CSV_FILE", cls.csv_path)
        cls.data_patch.start()
        cls.csv_patch.start()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), web_app.DashboardHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)
        cls.csv_patch.stop()
        cls.data_patch.stop()
        cls.tmp.cleanup()

    def request(self, method, path, payload=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_address[1], timeout=5)
        headers = {}
        if payload is not None:
            payload = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        connection.request(method, path, body=payload, headers=headers)
        response = connection.getresponse()
        raw = response.read()
        status, content_type = response.status, response.getheader("Content-Type")
        connection.close()
        if "application/json" in content_type:
            return status, json.loads(raw.decode("utf-8"))
        return status, raw

    def test_01_frontend_assets_and_empty_state(self):
        for path, snippet in (("/", b"Student Dashboard"),
                              ("/styles.css", b".sidebar"),
                              ("/app.js", b"renderTable")):
            status, body = self.request("GET", path)
            self.assertEqual(status, 200)
            self.assertIn(snippet, body)
        status, body = self.request("GET", "/api/stats")
        self.assertEqual(status, 200)
        self.assertEqual(body["total"], 0)

    def test_02_create_duplicate_update_download_delete(self):
        new = {"roll_no": "206", "name": "Kiran Student", "course": "CSE AI & ML",
               "marks": {subject: 70 for subject in main.SUBJECTS}}
        status, response = self.request("POST", "/api/students", new)
        self.assertEqual(status, 201)
        self.assertEqual(response["student"]["grade"], "B+")
        self.assertEqual(self.request("POST", "/api/students", new)[0], 409)
        status, response = self.request("GET", "/api/students")
        self.assertEqual(status, 200)
        self.assertEqual(len(response["students"]), 1)
        new["marks"]["Chemistry"] = 25
        status, response = self.request("PUT", "/api/students/206", new)
        self.assertEqual(status, 200)
        self.assertEqual(response["student"]["status"], "FAIL")
        status, csv_content = self.request("GET", "/api/export")
        self.assertEqual(status, 200)
        self.assertIn(b"Kiran Student", csv_content)
        self.assertIn(b"FAIL", csv_content)
        self.assertTrue(self.csv_path.exists())
        status, response = self.request("DELETE", "/api/students/206")
        self.assertEqual(status, 200)
        self.assertEqual(self.request("DELETE", "/api/students/206")[0], 404)
        self.assertEqual(self.request("GET", "/api/stats")[1]["total"], 0)
        self.assertEqual(json.loads(self.data_path.read_text("utf-8")), [])

    def test_03_rejects_malformed_and_bad_paths(self):
        bad = {"roll_no": "4", "name": "Too", "course": "CSE",
               "marks": {subject: 101 for subject in main.SUBJECTS}}
        self.assertEqual(self.request("POST", "/api/students", bad)[0], 400)
        self.assertEqual(self.request("GET", "/../../secret")[0], 404)


if __name__ == "__main__":
    unittest.main()
