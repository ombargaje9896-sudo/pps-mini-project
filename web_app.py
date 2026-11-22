"""EduTrack browser dashboard for the Student Marks Management project.

Uses only the Python standard library. Serves a local website and JSON API.
The existing console application and students.json remain unchanged.
"""

import argparse
import csv
import io
import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from main import (
    CSV_FILE, MAX_MARKS, SUBJECTS, calculate_result,
    find_student, load_students, save_students,
)

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "frontend"
DATA_LOCK = threading.RLock()
MAX_BODY_BYTES = 64 * 1024


def normalise_student(payload, roll_no=None):
    """Validate form values and return a properly typed student dictionary."""
    if not isinstance(payload, dict):
        raise ValueError("Enter valid student details.")

    roll = str(roll_no if roll_no is not None else payload.get("roll_no", "")).strip()
    if not roll.isascii() or not roll.isdecimal() or int(roll) < 1 or len(roll) > 8:
        raise ValueError("Roll number must contain 1–8 digits and be greater than zero.")
    roll = str(int(roll))  # 001 and 1 are the same roll number

    name = payload.get("name")
    course = payload.get("course")
    if not isinstance(name, str) or not 2 <= len(name.strip()) <= 80:
        raise ValueError("Student name must contain 2–80 characters.")
    if not isinstance(course, str) or not 2 <= len(course.strip()) <= 80:
        raise ValueError("Course must contain 2–80 characters.")

    raw_marks = payload.get("marks")
    if not isinstance(raw_marks, dict):
        raise ValueError("Please enter marks for every subject.")

    marks = {}
    for subject in SUBJECTS:
        value = raw_marks.get(subject)
        if isinstance(value, bool):
            raise ValueError(f"{subject} marks must be a whole number from 0 to 100.")
        if isinstance(value, int):
            score = value
        elif isinstance(value, str) and value.isascii() and value.strip().isdigit():
            score = int(value.strip())
        else:
            raise ValueError(f"{subject} marks must be a whole number from 0 to 100.")
        if not 0 <= score <= MAX_MARKS:
            raise ValueError(f"{subject} marks must be between 0 and 100.")
        marks[subject] = score

    return {"roll_no": roll, "name": name.strip(), "course": course.strip(), "marks": marks}


def enriched(student):
    total, percentage, grade, status = calculate_result(student["marks"])
    return {**student, "total": total, "percentage": percentage,
            "grade": grade, "status": status}


def get_stats(students):
    enriched_students = [enriched(student) for student in students]
    count = len(enriched_students)
    passed = [s for s in enriched_students if s["status"] == "PASS"]
    topper = max(passed, key=lambda s: s["percentage"], default=None)
    grades = {grade: 0 for grade in ("A+", "A", "B+", "B", "C", "D", "F")}
    for student in enriched_students:
        grades[student["grade"]] += 1
    return {
        "total": count,
        "passed": len(passed),
        "failed": count - len(passed),
        "pass_rate": round(len(passed) / count * 100, 2) if count else 0,
        "average": round(sum(s["percentage"] for s in enriched_students) / count, 2) if count else 0,
        "topper": {"name": topper["name"], "roll_no": topper["roll_no"],
                   "percentage": topper["percentage"]} if topper else None,
        "subject_averages": {
            subject: round(sum(s["marks"][subject] for s in enriched_students) / count, 2)
            if count else 0 for subject in SUBJECTS
        },
        "grades": grades,
    }


def make_csv(students):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["Roll No", "Name", "Course", *SUBJECTS,
                     "Total", "Percentage", "Grade", "Result"])
    for student in sorted(students, key=lambda record: int(record["roll_no"])):
        result = enriched(student)
        writer.writerow([
            result["roll_no"], result["name"], result["course"],
            *(result["marks"][subject] for subject in SUBJECTS),
            result["total"], f'{result["percentage"]:.2f}',
            result["grade"], result["status"],
        ])
    return ("\ufeff" + output.getvalue()).encode("utf-8")


class DashboardHandler(BaseHTTPRequestHandler):
    server_version = "EduTrack/1.0"

    def log_message(self, format_string, *args):
        print(f"[EduTrack] {self.address_string()} - {format_string % args}")

    def send_bytes(self, content, status=200, content_type="application/json; charset=utf-8", extra=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        for name, value in (extra or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, obj, status=200):
        self.send_bytes(json.dumps(obj, ensure_ascii=False).encode("utf-8"), status)

    def error_json(self, message, status=400):
        self.send_json({"error": message}, status)

    def read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "-1"))
        except ValueError as exc:
            raise ValueError("Invalid request length.") from exc
        if not 0 <= length <= MAX_BODY_BYTES:
            raise ValueError("Request exceeds the size limit.")
        if self.headers.get("Content-Type", "").split(";", 1)[0].strip() != "application/json":
            raise ValueError("Send JSON data.")
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Invalid JSON data.") from exc

    def route(self):
        return unquote(urlsplit(self.path).path)

    def do_GET(self):
        path = self.route()
        if path in ("/", "/index.html", "/styles.css", "/app.js"):
            name = "index.html" if path == "/" else path.lstrip("/")
            mime = {"index.html": "text/html; charset=utf-8",
                    "styles.css": "text/css; charset=utf-8",
                    "app.js": "text/javascript; charset=utf-8"}[name]
            self.send_bytes((STATIC / name).read_bytes(), content_type=mime)
            return
        if path not in ("/api/students", "/api/stats", "/api/export", "/api/health"):
            self.error_json("Page not found.", 404)
            return
        if path == "/api/health":
            self.send_json({"ok": True})
            return
        try:
            with DATA_LOCK:
                students = load_students()
                if path == "/api/students":
                    self.send_json({"students": [enriched(s) for s in students],
                                    "subjects": list(SUBJECTS)})
                elif path == "/api/stats":
                    self.send_json(get_stats(students))
                else:
                    payload = make_csv(students)
                    CSV_FILE.write_bytes(payload)
                    self.send_bytes(payload, content_type="text/csv; charset=utf-8",
                                    extra={"Content-Disposition": 'attachment; filename="student_results.csv"'})
        except (ValueError, OSError, KeyError, TypeError) as error:
            self.error_json(f"Could not load student data: {error}", 500)

    def do_POST(self):
        if self.route() != "/api/students":
            self.error_json("Page not found.", 404)
            return
        try:
            payload = self.read_json()
            student = normalise_student(payload)
            with DATA_LOCK:
                students = load_students()
                if find_student(students, student["roll_no"]):
                    self.error_json("This roll number already exists.", 409)
                    return
                students.append(student)
                save_students(students)
            self.send_json({"message": "Student added successfully.", "student": enriched(student)}, 201)
        except ValueError as error:
            self.error_json(str(error), 400)
        except (OSError, KeyError, TypeError) as error:
            self.error_json(f"Unable to save student: {error}", 500)

    def do_PUT(self):
        prefix = "/api/students/"
        path = self.route()
        if not path.startswith(prefix) or len(path) <= len(prefix) or "/" in path[len(prefix):]:
            self.error_json("Page not found.", 404)
            return
        roll = path[len(prefix):]
        try:
            student = normalise_student(self.read_json(), roll_no=roll)
            with DATA_LOCK:
                students = load_students()
                old = find_student(students, student["roll_no"])
                if old is None:
                    self.error_json("Student not found.", 404)
                    return
                old.update(student)
                save_students(students)
            self.send_json({"message": "Student updated successfully.", "student": enriched(student)})
        except ValueError as error:
            self.error_json(str(error), 400)
        except (OSError, KeyError, TypeError) as error:
            self.error_json(f"Unable to update student: {error}", 500)

    def do_DELETE(self):
        prefix = "/api/students/"
        path = self.route()
        if not path.startswith(prefix) or len(path) <= len(prefix) or "/" in path[len(prefix):]:
            self.error_json("Page not found.", 404)
            return
        roll = path[len(prefix):]
        if not roll.isascii() or not roll.isdecimal() or len(roll) > 8 or int(roll) < 1:
            self.error_json("Invalid roll number.", 400)
            return
        roll = str(int(roll))
        try:
            with DATA_LOCK:
                students = load_students()
                student = find_student(students, roll)
                if student is None:
                    self.error_json("Student not found.", 404)
                    return
                students.remove(student)
                save_students(students)
            self.send_json({"message": "Student deleted successfully."})
        except (ValueError, OSError, KeyError, TypeError) as error:
            self.error_json(f"Unable to delete student: {error}", 500)


def main():
    parser = argparse.ArgumentParser(description="Run the EduTrack local web dashboard")
    parser.add_argument("--port", type=int, default=8000, help="Local port (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser automatically")
    args = parser.parse_args()
    address = f"http://127.0.0.1:{args.port}"
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), DashboardHandler)
    except OSError as exc:
        print(f"Cannot start EduTrack: {exc}\nTry: py web_app.py --port 8001")
        return
    print("\n  EduTrack  |  Student Marks Management")
    print(f"  Open in browser: {address}")
    print("  Press Ctrl+C in this window to stop.\n")
    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(address)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEduTrack stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
