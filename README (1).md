# EduTrack — Student Marks Management System

**B.Tech Python mini-project — Topic 1**: Student marks management using **lists, tuples, dictionaries and file processing**.

This upgraded project includes a **modern, responsive web frontend** (HTML + CSS + JavaScript), a **Python REST-style server**, and the **original Python console app**. All features use the **same `students.json` file**, so data is saved and remains available after reopening the program.

## Getting started on Windows 10 / 11

1. **Download** and extract `Student_Marks_Management_With_Frontend.zip`.
2. Open the extracted `student_marks_management` folder.
3. **Double-click `run_dashboard.bat`** (or `run_project.bat`). Keep the black Command Prompt window open.
4. Your default browser should open automatically at **http://127.0.0.1:8000**. If it doesn't, open Chrome/Edge and enter that address manually.
5. Start working with the five sample students. Click **Add Student** to create another one.
6. To stop the dashboard, return to Command Prompt and press **Ctrl+C**.

**Python required:** Install Python 3.9+ from https://www.python.org/downloads/ if it is not installed. `py --version` should report the installed version.

**No extra packages needed:** This project uses built-in Python modules (`json`, `csv`, `pathlib`, `http.server`) and plain HTML/CSS/JS. It runs **offline** after Python is installed.

### Run from VS Code or Command Prompt

Open the project folder in VS Code and choose **Terminal → New Terminal**, then run:

```powershell
py web_app.py
```

If `py` is not found, use `python web_app.py`. Open **http://127.0.0.1:8000** in Chrome/Edge if required. If port 8000 is busy, run `py web_app.py --port 8001` and open **http://127.0.0.1:8001**.

### Run the original console project

Double-click `run_console.bat`, or from a terminal run:

```powershell
py main.py
```

The old numbered menu still works. **For class demonstration, use the dashboard first.**

## Dashboard features

- Overview cards: total students, pass rate, class average, class topper.
- Full student directory with a live **search**, **pass/fail filter** and **sorting**.
- Add a student with roll number, name, course and marks in five subjects.
- Click a student row to view a **detailed mark sheet** and subject progress bars.
- Update a student's details and marks; delete students with confirmation.
- **Live subject-average chart** and **grade-distribution doughnut chart**, both built without third-party libraries.
- **Export CSV** compatible with Excel.
- Responsive interface for desktop, tablet and mobile browser.
- Automatic JSON saving and duplicate roll-number / invalid marks validation.

## File structure

```text
student_marks_management/
├── frontend/
│   ├── index.html            # Dashboard page, panels and forms
│   ├── styles.css            # Responsive UI and visual styles
│   └── app.js                # Search, forms, charts and API calls
├── web_app.py                # Python local web server and JSON endpoints
├── main.py                   # Original Python console application and logic
├── students.json             # Current student records; dashboard edits this
├── sample_students.json      # Original 5 sample records for reset
├── student_results.csv       # Example export; refreshed on CSV download
├── run_dashboard.bat         # Double-click browser dashboard launcher
├── run_console.bat           # Double-click original console launcher
├── run_project.bat           # Default launcher (opens dashboard)
├── test_project.py           # Tests for original Python logic
├── test_web_app.py           # Additional dashboard / API tests
├── DEMO_AND_VIVA.md          # Demo workflow and viva answers
└── README.md                 # This file
```

## Python concepts used

| Topic | Where it is used |
|---|---|
| List | `students` stores every record in a list |
| Tuple | `SUBJECTS` contains 5 fixed subject names |
| Dictionary | Each student has `roll_no`, `name`, `course`, `marks` |
| Nested dictionary | `student["marks"]["Python"]` |
| File handling | `json.load()` and `json.dump()` read/write `students.json` |
| Modules | `main.py` calculations are reused by `web_app.py` |
| Functions | `calculate_result()`, `load_students()`, `get_stats()` etc. |
| Validation and exceptions | Invalid roll numbers, marks, missing fields, damaged files |
| CSV | `csv.writer()` generates Excel-compatible results |
| Browser UI | HTML, CSS and JavaScript with `fetch()` requests |

## Grade calculation

There are 5 subjects: **Mathematics, Physics, Chemistry, Python, English**. Each is out of 100 (total 500).

```text
Total = Sum of five marks
Percentage = (Total / 500) × 100
PASS only if every subject mark >= 35
```

For **passing** students: 90+ = A+, 80–below 90 = A, 70–below 80 = B+, 60–below 70 = B, 50–below 60 = C, 35–below 50 = D. If any subject is below 35, overall result is **FAIL** and grade is **F**, even if the aggregate percentage is high. These are simplified mini-project rules, not an official college grading policy.

## Original sample records

| Roll | Name | Marks / 500 | Percentage | Grade | Status |
|---|---|---:|---:|---|---|
| 101 | Aarav Patil | 441 | 88.20% | A | PASS |
| 102 | Anaya Sharma | 390 | 78.00% | B+ | PASS |
| 103 | Rohan Deshmukh | 325 | 65.00% | F | FAIL (Chemistry 32) |
| 104 | Isha Kulkarni | 464 | 92.80% | A+ | PASS |
| 105 | Kabir Khan | 306 | 61.20% | B | PASS |

**Topper**: Isha Kulkarni (92.80%). **Pass rate**: 80%.

## How the frontend communicates with Python

The Python server serves the website at `localhost` and handles these routes:

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/students` | GET | View saved records with calculated results |
| `/api/students` | POST | Add a new student |
| `/api/students/<roll>` | PUT | Update an existing student |
| `/api/students/<roll>` | DELETE | Delete an existing student |
| `/api/stats` | GET | Class average, topper, pass rate and grade statistics |
| `/api/export` | GET | Download latest Excel-compatible CSV |

The UI communicates through JavaScript `fetch()`. `web_app.py` validates data, loads/saves `students.json`, and calls `calculate_result()` from the existing `main.py` so the console and dashboard have the same grading rules. For safety, the app listens **only on your own computer** (`127.0.0.1`). It is a single-user college project, **not** a hosted system with accounts and permissions.

## Demonstration flow

1. Launch `run_dashboard.bat` and show the overview and charts.
2. Show the 5 sample students and explain the topper and failing Chemistry mark.
3. Search `Isha` and click the row for the full mark breakdown.
4. Add roll `106`, name `Priya Joshi`, course `CSE AI & ML`, marks `90, 88, 84, 95, 89`.
5. Show updated class statistics and grade charts.
6. Edit roll 106 and modify Python marks, then save.
7. Filter **Passed** and **Failed**; export CSV.
8. Delete roll 106 after showing the confirmation.
9. Show how `students.json` stores data and reopen the app to demonstrate persistence.

See [DEMO_AND_VIVA.md](DEMO_AND_VIVA.md) for an extended explanation and viva Q&A.

## Tests

From the project folder:

```powershell
py -m unittest -v test_project.py test_web_app.py
```

These tests cover calculations, grade / pass rules, HTTP routes, adding, updating, deleting, exporting, validation and sample data. Tests use a temporary data file to avoid changing your project records.

## Reset sample data

Close both the console and dashboard. Delete or rename `students.json`, then copy `sample_students.json` and rename the copy to `students.json`. Restart the dashboard.

## Troubleshooting

- **Python not found?** Install Python and restart Command Prompt; use `python` instead of `py` if needed.
- **Website not loading?** Check the black window is still open and read any error message. Enter `http://127.0.0.1:8000` manually.
- **Port already in use?** Run `py web_app.py --port 8001`.
- **Data not appearing?** Verify `students.json` is in the same folder as `web_app.py`.
- **Double-click closes window?** Open the folder in a terminal and run `py web_app.py` to see the error text.
