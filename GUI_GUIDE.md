# EduTrack — Student Marks Management Desktop GUI

## Start on Windows

1. Extract the ZIP file.
2. Open `student_marks_management`.
3. Double-click **`run_gui.bat`** (or open a terminal in the folder and run `py gui.py`).
4. No external Python packages are needed. Tkinter is bundled with most standard Windows Python installations.

## Features

- **Dashboard:** total students, passed students, average, pass rate, class topper, and recent records.
- **Students:** search by name, course, or roll number; add, edit, and delete student records. Double-click a row to edit.
- **Class insights:** subject-wise average charts and class statistics.
- **Export CSV:** choose where to save an Excel-compatible results file.
- **File persistence:** the GUI reads and writes the **same `students.json`** as `main.py`. Both interfaces share your records.

## Validation and calculations

- Roll number must be a positive integer and unique (e.g., `001` is the same roll as `1`).
- Name and course must not be empty.
- Five required subjects: Mathematics, Physics, Chemistry, Python, English; marks are whole numbers from 0 to 100.
- Students must score **35+ in each subject** to pass; grades use the existing `main.py` rules.
- The topper is the passed student with the highest percentage.

## Existing command-line interface

The original `main.py`, `run_project.bat`, automated tests, and data files remain available and unchanged. To use the terminal menu, run `run_project.bat`.

## Troubleshooting

- If double-clicking does not run, open Command Prompt in the extracted folder and run `py gui.py` to read the error.
- If you see `No module named tkinter`, reinstall Python from python.org with Tcl/Tk support enabled.
- If the app cannot save, move the project out of a read-only folder such as a protected ZIP preview and extract it first.
