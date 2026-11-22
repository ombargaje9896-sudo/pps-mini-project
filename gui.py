"""Modern desktop UI for the existing Student Marks Management project.
Run with: python gui.py. Requires only Python's standard library (Tkinter).
"""
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from main import (SUBJECTS, MAX_MARKS, load_students, save_students,
                  calculate_result, find_student)

BG = '#F4F7FB'
WHITE = '#FFFFFF'
INK = '#17233E'
MUTED = '#748198'
BLUE = '#4F63F5'
DARK = '#152342'
BORDER = '#E5EBF4'
GREEN = '#159B75'
RED = '#DC5266'


class StudentDialog(tk.Toplevel):
    def __init__(self, parent, student=None):
        super().__init__(parent)
        self.result = None
        self.student = student
        self.title('Edit student' if student else 'Add student')
        self.configure(bg=WHITE)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.geometry('540x650')
        self.update_idletasks()
        self.geometry(f'+{parent.winfo_rootx()+max(30, (parent.winfo_width()-540)//2)}+{parent.winfo_rooty()+45}')
        tk.Label(self, text='Edit student record' if student else 'Add a new student',
                 font=('Segoe UI', 19, 'bold'), bg=WHITE, fg=INK).pack(anchor='w', padx=32, pady=(25, 4))
        tk.Label(self, text='Enter student details and marks (0–100).',
                 font=('Segoe UI', 10), bg=WHITE, fg=MUTED).pack(anchor='w', padx=32, pady=(0, 15))
        body = tk.Frame(self, bg=WHITE)
        body.pack(fill='both', expand=True, padx=32)
        self.entries = {}
        for label, key in [('Roll number', 'roll_no'), ('Student name', 'name'), ('Course', 'course')]:
            self._entry(body, label, key, student[key] if student else '')
        tk.Label(body, text='SUBJECT MARKS', bg=WHITE, fg=BLUE,
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(16, 6))
        for subject in SUBJECTS:
            self._entry(body, subject, subject, str(student['marks'][subject]) if student else '')
        if student:
            self.entries['roll_no'].configure(state='disabled')
        footer = tk.Frame(self, bg=WHITE)
        footer.pack(fill='x', padx=32, pady=(12, 24))
        tk.Button(footer, text='Cancel', command=self.destroy, font=('Segoe UI', 10),
                  bg='#EDF1F7', fg=INK, relief='flat', padx=23, pady=11, cursor='hand2').pack(side='right', padx=(9, 0))
        tk.Button(footer, text='Save student', command=self.save, font=('Segoe UI', 10, 'bold'),
                  bg=BLUE, fg=WHITE, activebackground='#384CE4', relief='flat',
                  padx=23, pady=11, cursor='hand2').pack(side='right')
        self.bind('<Escape>', lambda _e: self.destroy())
        self.bind('<Return>', lambda _e: self.save())
        self.entries['name' if student else 'roll_no'].focus_set()

    def _entry(self, body, label, key, initial):
        tk.Label(body, text=label, bg=WHITE, fg=INK,
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(6, 3))
        entry = tk.Entry(body, font=('Segoe UI', 11), bg='#F8FAFD', fg=INK,
                         relief='solid', bd=1, highlightthickness=0)
        entry.pack(fill='x', ipady=6)
        entry.insert(0, initial)
        self.entries[key] = entry

    def save(self):
        roll = self.student['roll_no'] if self.student else self.entries['roll_no'].get().strip()
        name = self.entries['name'].get().strip()
        course = self.entries['course'].get().strip()
        if not roll.isdigit() or int(roll) <= 0:
            messagebox.showerror('Invalid roll number', 'Enter a positive whole number.', parent=self)
            return
        roll = str(int(roll))
        if not name or not course:
            messagebox.showerror('Missing details', 'Name and course are required.', parent=self)
            return
        marks = {}
        for subject in SUBJECTS:
            raw = self.entries[subject].get().strip()
            if not raw.isdigit() or not (0 <= int(raw) <= MAX_MARKS):
                messagebox.showerror('Invalid marks', f'{subject} must be a whole number from 0 to 100.', parent=self)
                self.entries[subject].focus_set()
                return
            marks[subject] = int(raw)
        self.result = {'roll_no': roll, 'name': name, 'course': course, 'marks': marks}
        self.destroy()


class MarksApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('EduTrack | Student Marks Management')
        self.geometry('1250x780')
        self.minsize(1000, 650)
        self.configure(bg=BG)
        try:
            self.students = load_students()
        except ValueError as exc:
            messagebox.showerror('Data file error', str(exc))
            self.destroy()
            return
        self.page = 'Dashboard'
        self.query = tk.StringVar()
        self.query.trace_add('write', lambda *_: self.render_table())
        self._setup_styles()
        self._layout()
        self.show_page('Dashboard')

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Records.Treeview', background=WHITE, fieldbackground=WHITE,
                        foreground=INK, rowheight=45, borderwidth=0,
                        font=('Segoe UI', 10))
        style.configure('Records.Treeview.Heading', background='#F5F7FC',
                        foreground=MUTED, font=('Segoe UI', 9, 'bold'),
                        relief='flat', padding=(12, 12))
        style.map('Records.Treeview', background=[('selected', '#E5EAFF')],
                  foreground=[('selected', INK)])
        style.map('Records.Treeview.Heading', background=[('active', '#EDF1FC')])

    def _layout(self):
        self.sidebar = tk.Frame(self, bg=DARK, width=236)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text='◈  EduTrack', bg=DARK, fg=WHITE,
                 font=('Segoe UI', 21, 'bold')).pack(anchor='w', padx=28, pady=(38, 3))
        tk.Label(self.sidebar, text='STUDENT MANAGEMENT', bg=DARK, fg='#93A4C5',
                 font=('Segoe UI', 8, 'bold')).pack(anchor='w', padx=31, pady=(0, 48))
        self.nav = {}
        for name, symbol in [('Dashboard', '▦'), ('Students', '☷'), ('Class insights', '◫')]:
            btn = tk.Button(self.sidebar, text=f'  {symbol}    {name}', anchor='w',
                            font=('Segoe UI', 11), bg=DARK, fg='#C6D2E9',
                            activebackground='#26375C', activeforeground=WHITE,
                            bd=0, relief='flat', padx=25, pady=16, cursor='hand2',
                            command=lambda n=name: self.show_page(n))
            btn.pack(fill='x', padx=10, pady=3)
            self.nav[name] = btn
        tk.Label(self.sidebar, text='PYTHON MINI PROJECT', bg=DARK, fg='#8697B8',
                 font=('Segoe UI', 9, 'bold')).pack(side='bottom', pady=(0, 29))
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side='left', fill='both', expand=True)
        self.header = tk.Frame(self.content, bg=BG)
        self.header.pack(fill='x', padx=35, pady=(30, 0))
        self.heading = tk.Label(self.header, bg=BG, fg=INK,
                                font=('Segoe UI', 24, 'bold'))
        self.heading.pack(side='left')
        tk.Button(self.header, text='+  Add student', bg=BLUE, fg=WHITE,
                  font=('Segoe UI', 10, 'bold'), bd=0, padx=20, pady=12,
                  cursor='hand2', command=self.add_student).pack(side='right')
        self.subtitle = tk.Label(self.content, bg=BG, fg=MUTED, font=('Segoe UI', 10))
        self.subtitle.pack(anchor='w', padx=37, pady=(3, 24))
        self.body = tk.Frame(self.content, bg=BG)
        self.body.pack(fill='both', expand=True, padx=35, pady=(0, 25))

    def _clear(self):
        for widget in self.body.winfo_children():
            widget.destroy()

    def show_page(self, page):
        self.page = page
        for name, btn in self.nav.items():
            btn.configure(bg='#34466E' if name == page else DARK,
                          fg=WHITE if name == page else '#C6D2E9')
        self.heading.config(text=page)
        self.subtitle.config(text={'Dashboard': 'Welcome back! Here is your class overview.',
                                  'Students': 'Manage records, grades, and student information.',
                                  'Class insights': 'Understand class results and subject performance.'}[page])
        self._clear()
        if page == 'Dashboard':
            self.render_dashboard()
        elif page == 'Students':
            self.render_students()
        else:
            self.render_insights()

    def _metric(self, parent, title, value, icon, accent):
        card = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(side='left', fill='both', expand=True, padx=(0, 12))
        tk.Label(card, text=icon, bg=WHITE, fg=accent,
                 font=('Segoe UI', 21, 'bold')).pack(anchor='w', padx=21, pady=(15, 0))
        tk.Label(card, text=str(value), bg=WHITE, fg=INK,
                 font=('Segoe UI', 23, 'bold')).pack(anchor='w', padx=21, pady=(2, 0))
        tk.Label(card, text=title, bg=WHITE, fg=MUTED,
                 font=('Segoe UI', 9)).pack(anchor='w', padx=21, pady=(1, 16))

    def _stats(self):
        results = [(s, calculate_result(s['marks'])) for s in self.students]
        passed = [(s, r) for s, r in results if r[3] == 'PASS']
        count = len(results)
        avg = sum(r[1] for _, r in results) / count if count else 0
        topper = max(passed, key=lambda x: x[1][1]) if passed else None
        return count, passed, avg, topper

    def render_dashboard(self):
        count, passed, avg, topper = self._stats()
        metrics = tk.Frame(self.body, bg=BG)
        metrics.pack(fill='x', pady=(0, 22))
        for name, value, symbol, color in [
            ('Total students', count, '♙', BLUE),
            ('Passed', len(passed), '✓', GREEN),
            ('Class average', f'{avg:.1f}%', '◉', '#D98C26'),
            ('Pass rate', f'{len(passed)/count*100:.1f}%' if count else '0%', '↗', '#9365DE')]:
            self._metric(metrics, name, value, symbol, color)
        section = tk.Frame(self.body, bg=BG)
        section.pack(fill='x', pady=(0, 18))
        left = tk.Frame(section, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        left.pack(side='left', fill='both', expand=True, padx=(0, 14))
        tk.Label(left, text='Class performance', bg=WHITE, fg=INK,
                 font=('Segoe UI', 13, 'bold')).pack(anchor='w', padx=22, pady=(18, 10))
        for label, value, color in [('Pass', len(passed), GREEN), ('Fail', count - len(passed), RED)]:
            line = tk.Frame(left, bg=WHITE)
            line.pack(fill='x', padx=22, pady=9)
            tk.Label(line, text=f'{label}  ·  {value}', bg=WHITE, fg=INK,
                     font=('Segoe UI', 10)).pack(anchor='w')
            bar = tk.Canvas(line, height=12, bg='#EEF2F8', highlightthickness=0)
            bar.pack(fill='x', pady=(7, 0))
            def draw_bar(_event, canvas=bar, v=value, total=count, fill=color):
                canvas.delete('all')
                if total:
                    canvas.create_rectangle(0, 0, canvas.winfo_width()*v/total, 12, fill=fill, outline='')
            bar.bind('<Configure>', draw_bar)
        right = tk.Frame(section, bg=WHITE, highlightbackground=BORDER, highlightthickness=1, width=280)
        right.pack(side='left', fill='both', expand=True)
        tk.Label(right, text='★', bg=WHITE, fg='#E7A643', font=('Segoe UI', 28)).pack(pady=(22, 5))
        tk.Label(right, text='Class topper', bg=WHITE, fg=MUTED,
                 font=('Segoe UI', 10)).pack()
        tk.Label(right, text=topper[0]['name'] if topper else 'No qualified topper',
                 bg=WHITE, fg=INK, font=('Segoe UI', 17, 'bold')).pack(pady=(6, 3))
        tk.Label(right, text=f'{topper[1][1]:.2f}%  ·  Roll {topper[0]["roll_no"]}' if topper else '—',
                 bg=WHITE, fg=BLUE, font=('Segoe UI', 11, 'bold')).pack(pady=(0, 22))
        self._table_section(self.body, 'Recent student records', limit=5)

    def render_students(self):
        self._table_section(self.body, 'All student records', search=True)

    def _table_section(self, parent, title, search=False, limit=None):
        card = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill='both', expand=True)
        toolbar = tk.Frame(card, bg=WHITE)
        toolbar.pack(fill='x', padx=20, pady=(18, 13))
        tk.Label(toolbar, text=title, bg=WHITE, fg=INK,
                 font=('Segoe UI', 13, 'bold')).pack(side='left')
        tk.Button(toolbar, text='↓ Export CSV', command=self.export_csv, bg='#EDF1FF', fg=BLUE,
                  bd=0, padx=13, pady=9, cursor='hand2', font=('Segoe UI', 9, 'bold')).pack(side='right')
        if search:
            tk.Entry(toolbar, textvariable=self.query, font=('Segoe UI', 10),
                     bg='#F4F7FC', fg=INK, bd=0, width=25, insertbackground=INK).pack(side='right', padx=12, ipady=10)
            tk.Label(toolbar, text='Search:', bg=WHITE, fg=MUTED).pack(side='right')
        columns = ('roll', 'name', 'course', 'total', 'percent', 'grade', 'status')
        frame = tk.Frame(card, bg=WHITE)
        frame.pack(fill='both', expand=True, padx=14, pady=(0, 8))
        self.table = ttk.Treeview(frame, columns=columns, show='headings',
                                  style='Records.Treeview', selectmode='browse')
        labels = {'roll':'ROLL NO', 'name':'STUDENT NAME', 'course':'COURSE',
                  'total':'TOTAL', 'percent':'PERCENTAGE', 'grade':'GRADE', 'status':'RESULT'}
        for col in columns:
            self.table.heading(col, text=labels[col])
            self.table.column(col, width=120 if col not in ('name', 'course') else 175,
                              minwidth=70, anchor='w' if col in ('name','course') else 'center')
        self.table.tag_configure('fail', foreground=RED)
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.table.pack(fill='both', expand=True)
        self.table.bind('<Double-1>', lambda _event: self.edit_student())
        self.table_limit = limit
        self.render_table()
        actions = tk.Frame(card, bg=WHITE)
        actions.pack(fill='x', padx=19, pady=(3, 16))
        tk.Label(actions, text='Select a student to edit or delete. Double-click to edit.',
                 bg=WHITE, fg=MUTED, font=('Segoe UI', 9)).pack(side='left')
        tk.Button(actions, text='Delete selected', command=self.delete_student, fg=RED,
                  bg='#FFF0F2', bd=0, padx=15, pady=9, cursor='hand2').pack(side='right', padx=(8, 0))
        tk.Button(actions, text='Edit selected', command=self.edit_student, fg=BLUE,
                  bg='#EDF1FF', bd=0, padx=15, pady=9, cursor='hand2').pack(side='right')

    def render_table(self):
        if not hasattr(self, 'table') or not self.table.winfo_exists():
            return
        self.table.delete(*self.table.get_children())
        query = self.query.get().strip().casefold() if self.page == 'Students' else ''
        records = sorted(self.students, key=lambda s: int(s['roll_no']))
        if query:
            records = [s for s in records if query in ' '.join((s['roll_no'], s['name'], s['course'])).casefold()]
        if self.table_limit is not None:
            records = records[:self.table_limit]
        for student in records:
            total, pct, grade, status = calculate_result(student['marks'])
            self.table.insert('', 'end', iid=student['roll_no'], values=(
                student['roll_no'], student['name'], student['course'],
                f'{total}/500', f'{pct:.2f}%', grade, status),
                tags=('fail',) if status == 'FAIL' else ())

    def render_insights(self):
        count, passed, avg, topper = self._stats()
        metrics = tk.Frame(self.body, bg=BG)
        metrics.pack(fill='x', pady=(0, 22))
        for name, val, symbol, color in [('Students', count, '♙', BLUE),
                                         ('Class average', f'{avg:.2f}%', '◉', '#D98C26'),
                                         ('Highest passed score', f'{topper[1][1]:.2f}%' if topper else '—', '★', GREEN)]:
            self._metric(metrics, name, val, symbol, color)
        card = tk.Frame(self.body, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill='both', expand=True)
        tk.Label(card, text='Subject-wise class average', bg=WHITE, fg=INK,
                 font=('Segoe UI', 15, 'bold')).pack(anchor='w', padx=30, pady=(28, 8))
        tk.Label(card, text='Average marks out of 100 for each subject', bg=WHITE, fg=MUTED,
                 font=('Segoe UI', 10)).pack(anchor='w', padx=30, pady=(0, 26))
        for subject in SUBJECTS:
            avg_mark = sum(s['marks'][subject] for s in self.students) / count if count else 0
            line = tk.Frame(card, bg=WHITE)
            line.pack(fill='x', padx=30, pady=13)
            top = tk.Frame(line, bg=WHITE)
            top.pack(fill='x')
            tk.Label(top, text=subject, bg=WHITE, fg=INK, font=('Segoe UI', 10, 'bold')).pack(side='left')
            tk.Label(top, text=f'{avg_mark:.1f} / 100', bg=WHITE, fg=MUTED,
                     font=('Segoe UI', 10)).pack(side='right')
            bar = tk.Canvas(line, bg='#EDF1F8', height=15, highlightthickness=0)
            bar.pack(fill='x', pady=(8, 0))
            bar.bind('<Configure>', lambda _event, canvas=bar, value=avg_mark: self.draw_chart_bar(canvas, value))
        tk.Label(card, text='Pass requirement: at least 35 marks in every subject.',
                 bg=WHITE, fg=MUTED, font=('Segoe UI', 9)).pack(anchor='w', padx=30, pady=22)

    @staticmethod
    def draw_chart_bar(canvas, value):
        canvas.delete('all')
        canvas.create_rectangle(0, 0, canvas.winfo_width() * value / 100, 15, fill=BLUE, outline='')

    def add_student(self):
        dialog = StudentDialog(self)
        self.wait_window(dialog)
        if dialog.result is None:
            return
        if find_student(self.students, dialog.result['roll_no']):
            messagebox.showerror('Duplicate roll number', 'A student with this roll number already exists.')
            return
        self.students.append(dialog.result)
        self._commit('Student added successfully.')

    def selected(self):
        if not hasattr(self, 'table') or not self.table.winfo_exists() or not self.table.selection():
            messagebox.showinfo('Select a student', 'Select a row in the student table first.')
            return None
        return find_student(self.students, self.table.selection()[0])

    def edit_student(self):
        student = self.selected()
        if student is None:
            return
        dialog = StudentDialog(self, student)
        self.wait_window(dialog)
        if dialog.result is None:
            return
        student.update(dialog.result)
        self._commit('Student updated successfully.')

    def delete_student(self):
        student = self.selected()
        if student is None:
            return
        if messagebox.askyesno('Delete student', f'Delete {student["name"]} (Roll {student["roll_no"]})?'):
            self.students.remove(student)
            self._commit('Student deleted successfully.')

    def _commit(self, success):
        try:
            save_students(self.students)
        except OSError as exc:
            messagebox.showerror('Save failed', str(exc))
            try:
                self.students = load_students()
            except ValueError:
                pass
        else:
            self.show_page(self.page)
            messagebox.showinfo('Success', success)

    def export_csv(self):
        if not self.students:
            messagebox.showinfo('No records', 'Add students before exporting.')
            return
        path = filedialog.asksaveasfilename(title='Export student results',
                                            defaultextension='.csv',
                                            initialfile='student_results.csv',
                                            filetypes=[('CSV files', '*.csv')])
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(['Roll No', 'Name', 'Course', *SUBJECTS,
                                 'Total', 'Percentage', 'Grade', 'Result'])
                for student in sorted(self.students, key=lambda s: int(s['roll_no'])):
                    total, pct, grade, status = calculate_result(student['marks'])
                    writer.writerow([student['roll_no'], student['name'], student['course'],
                                     *(student['marks'][s] for s in SUBJECTS),
                                     total, f'{pct:.2f}', grade, status])
            messagebox.showinfo('CSV exported', f'Results saved to:\n{path}')
        except OSError as exc:
            messagebox.showerror('Export failed', str(exc))


if __name__ == '__main__':
    app = MarksApp()
    if app.winfo_exists():
        app.mainloop()
