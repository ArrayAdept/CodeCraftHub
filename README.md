# CodeCraftHub Learning Management System

A beginner-friendly REST API built with Python and Flask. CodeCraftHub lets developers maintain a list of courses they want to learn, including a description, target completion date, and current status. Course records are stored in a local JSON file; no database or authentication is required.

## Features

- Create, list, retrieve, update, and delete courses (CRUD).
- JSON-file storage in `courses.json`, created automatically when missing.
- Automatically assigned numeric IDs and creation timestamps.
- Validation for required fields, date format, status values, and unknown fields.
- Useful JSON error responses and HTTP status codes.
- Automated tests using Python's built-in `unittest` framework.

## Requirements

- Python 3.10 or newer
- pip
- Optional: curl for testing from a terminal

## Project structure

```text
codecrafthub/
├── app.py              # Flask API and validation logic
├── courses.json        # Local course data (starts empty)
├── requirements.txt    # Python dependency
├── README.md           # Project documentation
├── .gitignore          # Files Git should ignore
└── tests/
    └── test_app.py     # Automated API tests
```

## Setup and run

Open a terminal in the `codecrafthub` folder.

### 1. Create and activate a virtual environment (recommended)

**Windows PowerShell:**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Git Bash:**
```bash
python -m venv .venv
source .venv/Scripts/activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Start the API

```bash
python app.py
```

The API runs at `http://127.0.0.1:5000`. Keep this terminal open while testing. Stop the server with `Ctrl+C`.

## API reference

All request and response bodies use JSON. The allowed status values are exactly `Not Started`, `In Progress`, and `Completed`.

| Method | Endpoint | Purpose | Success |
|---|---|---|---|
| GET | `/` | API welcome and endpoint overview | 200 |
| POST | `/api/courses` | Create a course | 201 |
| GET | `/api/courses` | List all courses | 200 |
| GET | `/api/courses/<id>` | Retrieve one course | 200 |
| PUT | `/api/courses/<id>` | Update one or more fields | 200 |
| DELETE | `/api/courses/<id>` | Delete a course | 200 |

### Course fields

- `id`: generated integer, starting at 1 when the list is empty.
- `name`: required non-empty string.
- `description`: required non-empty string.
- `target_date`: required date in `YYYY-MM-DD` format.
- `status`: required; one of the three allowed status values.
- `created_at`: generated ISO 8601 timestamp.

### Create a course

**curl (Git Bash, macOS, Linux):**
```bash
curl -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name":"Python Basics","description":"Learn Python fundamentals","target_date":"2027-12-31","status":"Not Started"}'
```

Expected result: HTTP `201 Created`, with the course object including `id` and `created_at`.

### List all courses

```bash
curl http://127.0.0.1:5000/api/courses
```

### Retrieve one course

```bash
curl http://127.0.0.1:5000/api/courses/1
```

### Update a course

`PUT` supports partial updates; only supplied fields are changed.

```bash
curl -X PUT http://127.0.0.1:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -d '{"status":"In Progress"}'
```

### Delete a course

```bash
curl -X DELETE http://127.0.0.1:5000/api/courses/1
```

### Error examples

Missing fields, invalid status/date, empty updates, and unknown fields return HTTP `400` with JSON details. Requesting a course ID that does not exist returns HTTP `404`. Data-file read/write failures return HTTP `500`.

Try invalid status:
```bash
curl -i -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name":"Example","description":"Testing validation","target_date":"2027-12-31","status":"Maybe"}'
```

## Run automated tests

Stop the server if desired, then run from the project root:

```bash
python -m unittest discover -s tests -v
```

The tests use a temporary JSON file and do not modify your actual `courses.json`.

## Troubleshooting

- **`python` is not recognized:** try `py` on Windows or `python3` on macOS/Linux.
- **`ModuleNotFoundError: No module named flask`:** activate the virtual environment and run `python -m pip install -r requirements.txt`.
- **Port 5000 is already in use:** stop the other process using port 5000, or change the port in the final `app.run(...)` line in `app.py`.
- **curl cannot connect:** confirm `python app.py` is still running and use `http://127.0.0.1:5000`.
- **JSON file errors:** ensure `courses.json` contains valid JSON (an array, such as `[]`) and that the project folder is writable.

## Notes

This project is designed for learning REST API fundamentals. It intentionally has no authentication and uses a local JSON file instead of a database. Do not expose it to the public internet or use it for sensitive data without adding appropriate security and persistence controls.
=======
# CodeCraftHub
>>>>>>> 14271f43f3ef6c8d75dd3fee59c806df0304f210
