# Student Marks Management System — Demonstration & Viva Guide

## 1. Presentation introduction (30–45 seconds)

> Good morning. My mini-project is **Student Marks Management System**, developed using **Python**. The aim is to manage student information and marks, automatically calculate results, and permanently store records. This project uses **lists, tuples, dictionaries, functions, loops, conditional statements, file handling, and input validation**. It is menu-driven and runs in the terminal.

## 2. Live demonstration script (about 3–5 minutes)

Before starting, reset the sample records using the instructions in `README.md`, if you previously edited them.

1. **Start:** Open the folder in CMD and type `py main.py`. Point out the welcome message and menu.
2. **View (option 2):** Show five existing student records with totals, grades, and results. Explain that they load from `students.json`.
3. **Search (option 3):** Enter roll number `103`. Point out Chemistry `32`, which is below the pass mark of `35`; the result is **FAIL** even though the overall percentage is `65.00%`.
4. **Topper (option 6):** Point out the class topper **Isha Kulkarni (92.80%)** and class pass rate **80.00%**.
5. **Add (option 1):** Enter roll `106`, name `Demo Student`, course `CSE AI & ML`, and marks `80`, `75`, `85`, `90`, `70`. The total should be **400/500**, percentage **80.00%**, grade **A**, result **PASS**.
6. **Validation:** Try adding roll `106` again to show that a duplicate roll number is rejected. Optionally, while entering marks for a new student, try `120` first: the program asks again instead of accepting an invalid score.
7. **Update (option 4):** Search for roll `106`, press Enter to keep name and course, press Enter for every subject except Python, change Python to `95`. Total becomes **405/500**, percentage **81.00%**. (It remains grade A.)
8. **Export (option 7):** Open the generated `student_results.csv` file in Excel or Notepad to show exported records and calculated results.
9. **Persistence:** Exit using option `0`, restart with `py main.py`, then use option `2` or `3` to show roll `106` is still saved.
10. **Delete (option 5):** Enter roll `106`, type `YES` to confirm, then show that the student is no longer present. This keeps the original sample data unchanged for the next demonstration.

### Quick expected output (before making changes)

```text
Roll     Name                   Total     Percent    Grade   Result
----------------------------------------------------------------------
101      Aarav Patil            441/500    88.20%    A       PASS
102      Anaya Sharma           390/500    78.00%    B+      PASS
103      Rohan Deshmukh         325/500    65.00%    F       FAIL
104      Isha Kulkarni          464/500    92.80%    A+      PASS
105      Kabir Khan             306/500    61.20%    B       PASS
```

## 3. Important viva questions and short answers

**Q1. What is the objective of your project?**  
To store student records, manage their marks, calculate grades, and preserve the data in files.

**Q2. Why did you choose Python?**  
Python is readable, beginner-friendly, and provides built-in libraries for file processing.

**Q3. Where did you use a list?**  
`students` is a list that contains one dictionary for each student.

**Q4. Where did you use a tuple?**  
`SUBJECTS` is a tuple containing five fixed subject names.

**Q5. Where did you use a dictionary?**  
Each student is represented as a dictionary storing their roll number, name, course, and nested marks dictionary.

**Q6. Difference between list and tuple?**  
Lists are mutable (can be changed), while tuples are immutable (their contents cannot be reassigned).

**Q7. What is a nested dictionary?**  
A dictionary stored inside another dictionary; here, the `marks` key contains subject-score pairs.

**Q8. What is file handling?**  
Reading data from and writing data to files so records remain available after the program closes.

**Q9. Why did you use JSON?**  
It stores nested data like lists and dictionaries in a structured, human-readable format.

**Q10. Which functions read and write JSON?**  
`json.load()` reads a JSON file; `json.dump()` writes Python data to a JSON file.

**Q11. How is the percentage calculated?**  
`(sum of marks / 500) × 100` because there are five subjects of 100 marks each.

**Q12. What is the pass condition?**  
At least 35 marks in **each** subject; failing any subject results in an overall FAIL.

**Q13. How do you prevent duplicate records?**  
`find_student()` checks whether the roll number already exists before the new student is appended.

**Q14. What is input validation?**  
Checking the input before accepting it, e.g. only marks from 0 to 100 and positive numeric roll numbers.

**Q15. Which loop is used for the main menu?**  
A `while True` loop, which stops when the user selects option `0`.

**Q16. What are functions and why use them?**  
Reusable blocks of code. They make the project easier to read, test and maintain.

**Q17. What is exception handling?**  
Handling errors without unexpectedly crashing, e.g. `try`/`except` for invalid marks or a corrupted data file.

**Q18. Why export CSV?**  
CSV is easy to read in spreadsheet programs such as Microsoft Excel.

**Q19. Is this a database project?**  
No. It uses file-based storage (`students.json`), not a database server.

**Q20. What enhancements can you make later?**  
A graphical interface, flexible subjects, database support, login, report cards and charts.

## 4. What to explain in the actual code

- `SUBJECTS = (...)` shows the **tuple**.
- `load_students()` shows **JSON file reading**.
- `student = {...}` inside `add_student()` shows a **dictionary**.
- `students.append(student)` shows modifying a **list**.
- `calculate_result()` demonstrates `sum()`, `all()`, `if/elif`, and return values.
- `ask_marks()` demonstrates **validation**, loops and `try/except`.
- `save_students()` shows **writing to JSON**.
- `export_csv()` shows **CSV file processing**.
- `main()` shows **menu-driven program structure**.

## 5. Common troubleshooting

- **`py` not found:** Install Python or run `python main.py` instead.
- **Double-click closes immediately:** Use Command Prompt or `run_project.bat`.
- **Data changed after a practice run:** Restore `students.json` from `sample_students.json`.
- **Corrupted JSON:** Restore the sample data rather than trying to edit broken JSON during the presentation.
- **Where is the output file?** The `student_results.csv` is created in the same folder as `main.py` after option 7.

---

# Added Frontend — Web Dashboard Viva and Demonstration

The upgraded project now has a browser-based GUI. **Start it with `run_dashboard.bat` or `py web_app.py` and visit `http://127.0.0.1:8000`.** The old `main.py` console application remains available.

## Suggested 3–5 minute web demo

1. Show the landing dashboard and explain the KPI cards: total, pass rate, average, topper.
2. Click **Students**, search by name or roll number and change the **Passed / Failed** filter.
3. Click any student row and explain the subject marks, total, percentage and grade.
4. Click **Add Student**, enter valid details and all five marks, then save; point out that the charts update automatically.
5. Edit the newly added student, change one subject mark and save; show the new results.
6. Use **Export CSV** and open the file in Excel. Then delete the demo student and show the confirmation.
7. Open `students.json` in VS Code, explain **list**, **dictionary**, **file handling**, and `calculate_result()` in `main.py`.

## Additional viva questions

**Q1. What is a frontend?**
The part users see and interact with, here the HTML page styled using CSS and operated by JavaScript.

**Q2. What is a backend?**
The Python code in `web_app.py` that handles requests, checks data, calculates results, and saves records.

**Q3. How does the frontend connect to Python?**
JavaScript `fetch()` calls local routes such as `GET /api/students` and `POST /api/students`. The Python server returns JSON.

**Q4. What is JSON?**
JavaScript Object Notation is a text format for structured data, such as a list containing student dictionaries.

**Q5. What is an API?**
An Application Programming Interface defines how different parts of software communicate. Our web app exposes local HTTP endpoints for records and statistics.

**Q6. What do GET, POST, PUT and DELETE do?**
GET reads data, POST creates it, PUT updates it, and DELETE removes it.

**Q7. Which programming concepts satisfy Topic 1?**
Lists for the students collection, a tuple for fixed subjects, nested dictionaries for marks and records, and JSON/CSV files for persistence and export.

**Q8. Are the results stored after closing the website?**
Yes. The Python server saves student records in `students.json` when adding, updating or deleting data.

**Q9. Is the dashboard available publicly on the internet?**
No. It runs on the user's computer using `127.0.0.1` and is intended for local demonstration.

**Q10. Why does a student with 65% sometimes fail?**
The project requires at least 35 marks in **every** subject. A student scoring 32 in Chemistry fails despite a 65% overall score.

**Q11. Which libraries or frameworks were used?**
The backend uses only built-in Python modules. The frontend is vanilla HTML, CSS and JavaScript, without React or third-party packages.

**Q12. How is the topper chosen?**
`get_stats()` uses the passing students and selects the student with the highest calculated percentage. If no students pass, no topper is shown.
