"""
CodeCraftHub - a beginner-friendly Flask REST API for tracking learning courses.

Data is stored in courses.json beside this file. This is a learning/demo project:
it does not include authentication and is not intended for production deployment.
"""
from datetime import datetime, date
import json
import os
import tempfile
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = (
        "GET, POST, PUT, DELETE, OPTIONS"
    )
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

DATA_FILE = Path(__file__).resolve().parent / "courses.json"
VALID_STATUSES = {"Not Started", "In Progress", "Completed"}
REQUIRED_FIELDS = {"name", "description", "target_date", "status"}


class DataFileError(Exception):
    """Raised when the course JSON file cannot be read or written."""


def ensure_data_file():
    """Create an empty JSON data file if it does not exist."""
    if not DATA_FILE.exists():
        try:
            DATA_FILE.write_text("[]\n", encoding="utf-8")
        except OSError as exc:
            raise DataFileError("Could not create courses.json.") from exc


def load_courses():
    """Read courses from JSON, returning an empty list for a new file."""
    ensure_data_file()
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise DataFileError("Could not read courses.json. Check that it contains valid JSON.") from exc
    if not isinstance(data, list):
        raise DataFileError("courses.json must contain a JSON array.")
    return data


def save_courses(courses):
    """Write JSON atomically to reduce the chance of a partially written file."""
    ensure_data_file()
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=DATA_FILE.parent, delete=False
        ) as temp_file:
            json.dump(courses, temp_file, indent=2, ensure_ascii=False)
            temp_file.write("\n")
            temp_name = temp_file.name
        os.replace(temp_name, DATA_FILE)
    except OSError as exc:
        if temp_name and os.path.exists(temp_name):
            try:
                os.remove(temp_name)
            except OSError:
                pass
        raise DataFileError("Could not write courses.json. Check folder permissions.") from exc


def validate_course_payload(payload, partial=False):
    """Return a list of validation errors. PUT accepts partial updates."""
    if not isinstance(payload, dict):
        return ["Request body must be a JSON object."]

    errors = []
    fields_to_check = set(payload) if partial else REQUIRED_FIELDS
    if not partial:
        missing = sorted(REQUIRED_FIELDS - set(payload))
        if missing:
            errors.append("Missing required field(s): " + ", ".join(missing) + ".")

    allowed_fields = REQUIRED_FIELDS
    unknown = sorted(set(payload) - allowed_fields)
    if unknown:
        errors.append("Unknown field(s): " + ", ".join(unknown) + ".")

    for field in fields_to_check:
        if field not in REQUIRED_FIELDS or field not in payload:
            continue
        value = payload[field]
        if not isinstance(value, str) or not value.strip():
            errors.append(f"'{field}' must be a non-empty string.")

    if "target_date" in payload and isinstance(payload["target_date"], str):
        try:
            date.fromisoformat(payload["target_date"])
            if len(payload["target_date"]) != 10:
                raise ValueError
        except ValueError:
            errors.append("'target_date' must use YYYY-MM-DD format.")

    if "status" in payload and payload["status"] not in VALID_STATUSES:
        errors.append("'status' must be one of: Not Started, In Progress, Completed.")

    return errors


def next_course_id(courses):
    """Return the next available positive integer ID."""
    ids = [course.get("id", 0) for course in courses if isinstance(course.get("id"), int)]
    return max(ids, default=0) + 1


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Endpoint not found."}), 404


@app.get("/")
def home():
    return jsonify({
        "message": "Welcome to CodeCraftHub API",
        "docs": "See README.md for endpoint documentation.",
        "endpoints": {
            "list_or_create": "/api/courses",
            "get_update_delete": "/api/courses/<id>"
        }
    })


@app.get("/api/courses")
def get_courses():
    """Return every saved course."""
    try:
        return jsonify(load_courses()), 200
    except DataFileError as exc:
        app.logger.exception("Course data read failed")
        return jsonify({"error": str(exc)}), 500


@app.post("/api/courses")
def create_course():
    """Create a course and assign its ID and creation timestamp."""
    payload = request.get_json(silent=True)
    errors = validate_course_payload(payload)
    if errors:
        return jsonify({"error": "Validation failed.", "details": errors}), 400

    try:
        courses = load_courses()
        course = {
            "id": next_course_id(courses),
            "name": payload["name"].strip(),
            "description": payload["description"].strip(),
            "target_date": payload["target_date"],
            "status": payload["status"],
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
        courses.append(course)
        save_courses(courses)
        return jsonify(course), 201
    except DataFileError as exc:
        app.logger.exception("Course creation failed")
        return jsonify({"error": str(exc)}), 500


@app.get("/api/courses/<int:course_id>")
def get_course(course_id):
    """Return one course by ID."""
    try:
        courses = load_courses()
        course = next((item for item in courses if item.get("id") == course_id), None)
        if course is None:
            return jsonify({"error": f"Course with id {course_id} was not found."}), 404
        return jsonify(course), 200
    except DataFileError as exc:
        app.logger.exception("Course lookup failed")
        return jsonify({"error": str(exc)}), 500


@app.put("/api/courses/<int:course_id>")
def update_course(course_id):
    """Update one or more fields on an existing course."""
    payload = request.get_json(silent=True)
    errors = validate_course_payload(payload, partial=True)
    if errors:
        return jsonify({"error": "Validation failed.", "details": errors}), 400
    if not payload:
        return jsonify({"error": "Provide at least one field to update."}), 400

    try:
        courses = load_courses()
        course = next((item for item in courses if item.get("id") == course_id), None)
        if course is None:
            return jsonify({"error": f"Course with id {course_id} was not found."}), 404
        for field in REQUIRED_FIELDS:
            if field in payload:
                value = payload[field]
                course[field] = value.strip() if isinstance(value, str) and field in {"name", "description"} else value
        save_courses(courses)
        return jsonify(course), 200
    except DataFileError as exc:
        app.logger.exception("Course update failed")
        return jsonify({"error": str(exc)}), 500


@app.delete("/api/courses/<int:course_id>")
def delete_course(course_id):
    """Delete one course by ID."""
    try:
        courses = load_courses()
        course = next((item for item in courses if item.get("id") == course_id), None)
        if course is None:
            return jsonify({"error": f"Course with id {course_id} was not found."}), 404
        courses = [item for item in courses if item.get("id") != course_id]
        save_courses(courses)
        return jsonify({"message": f"Course {course_id} deleted successfully."}), 200
    except DataFileError as exc:
        app.logger.exception("Course deletion failed")
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    ensure_data_file()
    print("CodeCraftHub API is starting...")
    print(f"Data will be stored in: {DATA_FILE}")
    print("API will be available at: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
