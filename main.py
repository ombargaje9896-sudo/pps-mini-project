"""Student Marks Management System

Mini-project topic 1: Python lists, tuples, dictionaries and file processing.
No third-party libraries are required.
"""

import csv
import json
from pathlib import Path

# TUPLE: fixed list of subjects
SUBJECTS = ("Mathematics", "Physics", "Chemistry", "Python", "English")
PASS_MARK = 35
MAX_MARKS = 100

PROJECT_FOLDER = Path(__file__).resolve().parent
DATA_FILE = PROJECT_FOLDER / "students.json"
CSV_FILE = PROJECT_FOLDER / "student_results.csv"


def load_students():
    """Load a LIST of student DICTIONARIES from a JSON file."""
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            students = json.load(file)
        if not isinstance(students, list):
            raise ValueError("The data file must contain a list of students.")
        return students
    except (json.JSONDecodeError, OSError, ValueError) as error:
        raise ValueError(
            f"Cannot read {DATA_FILE.name}: {error}. "
            "Please restore it from sample_students.json."
        ) from error


def save_students(students):
    """Save the entire student list; replace the file safely."""
    temp_file = DATA_FILE.with_suffix(".tmp")
    with temp_file.open("w", encoding="utf-8") as file:
        json.dump(students, file, indent=4, ensure_ascii=False)
    temp_file.replace(DATA_FILE)


def calculate_result(marks):
    """Return total, percentage, grade and status for one student."""
    total = sum(marks[subject] for subject in SUBJECTS)
    percentage = round(total / (len(SUBJECTS) * MAX_MARKS) * 100, 2)
    passed = all(marks[subject] >= PASS_MARK for subject in SUBJECTS)

    if not passed:
        grade = "F"
        status = "FAIL"
    else:
        status = "PASS"
        if percentage >= 90:
            grade = "A+"
        elif percentage >= 80:
            grade = "A"
        elif percentage >= 70:
            grade = "B+"
        elif percentage >= 60:
            grade = "B"
        elif percentage >= 50:
            grade = "C"
        else:
            grade = "D"

    return total, percentage, grade, status


def find_student(students, roll_no):
    for student in students:
        if student["roll_no"] == roll_no:
            return student
    return None


def ask_roll_no():
    while True:
        value = input("Enter roll number (digits only): ").strip()
        if value.isdigit() and int(value) > 0:
            return str(int(value))  # "001" and "1" refer to the same student
        print("Invalid roll number. Enter a positive number, e.g., 101.")


def ask_required_text(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def ask_marks(old_marks=None):
    """Get marks for each subject, optionally retaining existing marks."""
    marks = {}
    for subject in SUBJECTS:
        while True:
            if old_marks is None:
                raw = input(f"Enter {subject} marks (0-100): ").strip()
            else:
                raw = input(
                    f"Enter {subject} marks (0-100) [{old_marks[subject]}], "
                    "or press Enter to keep: "
                ).strip()
                if raw == "":
                    marks[subject] = old_marks[subject]
                    break
            try:
                score = int(raw)
                if 0 <= score <= MAX_MARKS:
                    marks[subject] = score
                    break
            except ValueError:
                pass
            print("Invalid marks. Enter a whole number from 0 to 100.")
    return marks


def print_student(student):
    total, percentage, grade, status = calculate_result(student["marks"])
    print("\n" + "-" * 45)
    print(f"Roll Number : {student['roll_no']}")
    print(f"Name        : {student['name']}")
    print(f"Course      : {student['course']}")
    print("Marks:")
    for subject in SUBJECTS:
        print(f"  {subject:<13}: {student['marks'][subject]}/100")
    print(f"Total       : {total}/{len(SUBJECTS) * MAX_MARKS}")
    print(f"Percentage  : {percentage:.2f}%")
    print(f"Grade       : {grade}")
    print(f"Result      : {status}")
    print("-" * 45)


def add_student(students):
    print("\n--- Add Student ---")
    roll_no = ask_roll_no()
    if find_student(students, roll_no):
        print("A student with this roll number already exists.")
        return

    name = ask_required_text("Enter student name: ")
    course = ask_required_text("Enter course (e.g., CSE AI & ML): ")
    marks = ask_marks()

    student = {"roll_no": roll_no, "name": name, "course": course, "marks": marks}
    students.append(student)
    save_students(students)
    print("Student added and saved successfully!")
    print_student(student)


def view_students(students):
    print("\n--- All Student Records ---")
    if not students:
        print("No student records found.")
        return

    print(f"{'Roll':<8} {'Name':<22} {'Total':<9} {'Percent':<10} {'Grade':<7} {'Result'}")
    print("-" * 70)
    for student in sorted(students, key=lambda record: int(record["roll_no"])):
        total, percentage, grade, status = calculate_result(student["marks"])
        name = student["name"][:21]
        print(f"{student['roll_no']:<8} {name:<22} {str(total) + '/500':<9} "
              f"{percentage:>6.2f}%    {grade:<7} {status}")
    print(f"Total students: {len(students)}")


def search_student(students):
    print("\n--- Search Student ---")
    student = find_student(students, ask_roll_no())
    if student:
        print_student(student)
    else:
        print("Student not found.")


def update_student(students):
    print("\n--- Update Student ---")
    student = find_student(students, ask_roll_no())
    if student is None:
        print("Student not found.")
        return

    print("Press Enter to keep existing details and marks.")
    name = input(f"Name [{student['name']}]: ").strip()
    course = input(f"Course [{student['course']}]: ").strip()
    updated_marks = ask_marks(student["marks"])
    if name:
        student["name"] = name
    if course:
        student["course"] = course
    student["marks"] = updated_marks
    save_students(students)
    print("Student record updated and saved!")
    print_student(student)


def delete_student(students):
    print("\n--- Delete Student ---")
    student = find_student(students, ask_roll_no())
    if student is None:
        print("Student not found.")
        return

    confirm = input(f"Delete {student['name']}? Type YES to confirm: ").strip()
    if confirm.upper() == "YES":
        students.remove(student)
        save_students(students)
        print("Student deleted successfully!")
    else:
        print("Delete cancelled.")


def show_statistics(students):
    print("\n--- Class Statistics ---")
    if not students:
        print("No records available for statistics.")
        return

    results = [(student, calculate_result(student["marks"])) for student in students]
    passed = [(student, result) for student, result in results if result[3] == "PASS"]
    average = sum(result[1] for _, result in results) / len(results)
    print(f"Total students      : {len(students)}")
    print(f"Passed students     : {len(passed)}")
    print(f"Failed students     : {len(students) - len(passed)}")
    print(f"Class average       : {average:.2f}%")
    print(f"Class pass rate     : {len(passed) / len(students) * 100:.2f}%")
    if passed:
        topper, result = max(passed, key=lambda pair: pair[1][1])
        print(f"Topper (passed)     : {topper['name']} (Roll {topper['roll_no']})")
        print(f"Topper percentage   : {result[1]:.2f}%")
    else:
        print("Topper              : None (no students passed)")


def export_csv(students):
    print("\n--- Export Results to CSV ---")
    if not students:
        print("No records available to export.")
        return

    headings = ["Roll No", "Name", "Course", *SUBJECTS,
                "Total", "Percentage", "Grade", "Result"]
    with CSV_FILE.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headings)
        for student in sorted(students, key=lambda record: int(record["roll_no"])):
            total, percentage, grade, status = calculate_result(student["marks"])
            writer.writerow([
                student["roll_no"], student["name"], student["course"],
                *(student["marks"][subject] for subject in SUBJECTS),
                total, f"{percentage:.2f}", grade, status
            ])
    print(f"Results exported successfully to: {CSV_FILE}")
    print("You can open this CSV file in Excel.")


def main():
    try:
        students = load_students()
    except ValueError as error:
        print(error)
        return

    print("Welcome to the Student Marks Management System!")
    print(f"Loaded {len(students)} student record(s).")

    while True:
        print("\n========== MAIN MENU ==========")
        print("1. Add a student")
        print("2. View all students")
        print("3. Search a student")
        print("4. Update a student")
        print("5. Delete a student")
        print("6. Class statistics and topper")
        print("7. Export results to CSV")
        print("0. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_student(students)
        elif choice == "2":
            view_students(students)
        elif choice == "3":
            search_student(students)
        elif choice == "4":
            update_student(students)
        elif choice == "5":
            delete_student(students)
        elif choice == "6":
            show_statistics(students)
        elif choice == "7":
            export_csv(students)
        elif choice == "0":
            print("Thank you for using Student Marks Management System!")
            break
        else:
            print("Invalid menu choice. Enter a number from 0 to 7.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram closed.")
