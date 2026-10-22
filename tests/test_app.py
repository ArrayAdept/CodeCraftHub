"""Automated tests for the CodeCraftHub REST API."""
import json
import tempfile
import unittest
from pathlib import Path

import app as app_module


class CodeCraftHubAPITests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        app_module.DATA_FILE = Path(self.temp_dir.name) / "courses.json"
        app_module.DATA_FILE.write_text("[]\n", encoding="utf-8")
        app_module.app.config.update(TESTING=True)
        self.client = app_module.app.test_client()
        self.course_payload = {
            "name": "Python Basics",
            "description": "Learn Python fundamentals",
            "target_date": "2027-12-31",
            "status": "Not Started",
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_home_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("CodeCraftHub", response.get_json()["message"])

    def test_create_course(self):
        response = self.client.post("/api/courses", json=self.course_payload)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["id"], 1)
        self.assertIn("created_at", data)
        self.assertEqual(data["name"], "Python Basics")

    def test_list_courses(self):
        self.client.post("/api/courses", json=self.course_payload)
        response = self.client.get("/api/courses")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 1)

    def test_get_one_course(self):
        self.client.post("/api/courses", json=self.course_payload)
        response = self.client.get("/api/courses/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id"], 1)

    def test_update_course(self):
        self.client.post("/api/courses", json=self.course_payload)
        response = self.client.put("/api/courses/1", json={"status": "In Progress"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "In Progress")

    def test_delete_course(self):
        self.client.post("/api/courses", json=self.course_payload)
        response = self.client.delete("/api/courses/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/courses").get_json(), [])

    def test_missing_required_fields(self):
        response = self.client.post("/api/courses", json={"name": "Only a name"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("details", response.get_json())

    def test_invalid_status(self):
        payload = dict(self.course_payload, status="Maybe Later")
        response = self.client.post("/api/courses", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_invalid_date(self):
        payload = dict(self.course_payload, target_date="31-12-2027")
        response = self.client.post("/api/courses", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_course_not_found(self):
        self.assertEqual(self.client.get("/api/courses/999").status_code, 404)
        self.assertEqual(self.client.put("/api/courses/999", json={"status": "Completed"}).status_code, 404)
        self.assertEqual(self.client.delete("/api/courses/999").status_code, 404)

    def test_empty_update(self):
        self.client.post("/api/courses", json=self.course_payload)
        response = self.client.put("/api/courses/1", json={})
        self.assertEqual(response.status_code, 400)

    def test_unknown_field(self):
        payload = dict(self.course_payload, unexpected="value")
        self.assertEqual(self.client.post("/api/courses", json=payload).status_code, 400)

    def test_id_increments_after_deletion(self):
        first = self.client.post("/api/courses", json=self.course_payload).get_json()
        self.client.delete(f"/api/courses/{first['id']}")
        second = self.client.post("/api/courses", json=self.course_payload).get_json()
        self.assertEqual(second["id"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
