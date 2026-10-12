import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from datetime import datetime

DB_NAME = "student_database.db"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"


def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matric_no TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            department TEXT NOT NULL,
            level TEXT NOT NULL,
            gender TEXT,
            phone TEXT,
            email TEXT
        )
    """)
    return conn


class StudentDBApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Database Management System")
        self.root.geometry("1050x650")
        self.root.minsize(900, 560)
        self.conn = connect_db()
        self.selected_id = None
        self.show_login()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_window()
        self.root.configure(bg="#edf2f7")

        panel = tk.Frame(self.root, bg="white", padx=35, pady=30,
                         highlightbackground="#cbd5e0", highlightthickness=1)
        panel.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(panel, text="STUDENT DATABASE SYSTEM",
                 font=("Arial", 18, "bold"), bg="white",
                 fg="#17365d").pack(pady=(0, 8))
        tk.Label(panel, text="Sign in to continue",
                 font=("Arial", 10), bg="white", fg="#555").pack(pady=(0, 20))

        tk.Label(panel, text="Username", bg="white", anchor="w").pack(fill="x")
        self.username_entry = ttk.Entry(panel, width=34)
        self.username_entry.pack(pady=(5, 12), ipady=4)

        tk.Label(panel, text="Password", bg="white", anchor="w").pack(fill="x")
        self.password_entry = ttk.Entry(panel, width=34, show="*")
        self.password_entry.pack(pady=(5, 18), ipady=4)
        self.password_entry.bind("<Return>", lambda event: self.login())

        ttk.Button(panel, text="Login", command=self.login).pack(fill="x", ipady=4)
        tk.Label(panel, text="Demo login: admin / admin123",
                 bg="white", fg="#666", font=("Arial", 9)).pack(pady=(14, 0))
        self.username_entry.focus_set()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
            self.show_dashboard()
        else:
            messagebox.showerror("Login failed", "Incorrect username or password.")

    def show_dashboard(self):
        self.clear_window()
        self.root.configure(bg="#f4f6f8")

        header = tk.Frame(self.root, bg="#17365d", padx=18, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="Student Database Management System",
                 bg="#17365d", fg="white", font=("Arial", 17, "bold")).pack(side="left")
        ttk.Button(header, text="Logout", command=self.show_login).pack(side="right")

        body = tk.Frame(self.root, bg="#f4f6f8", padx=16, pady=14)
        body.pack(fill="both", expand=True)

        form = ttk.LabelFrame(body, text="Student Details", padding=12)
        form.pack(side="left", fill="y", padx=(0, 14))

        self.entries = {}
        fields = [
            ("Matric No.", "matric_no"),
            ("Full Name", "full_name"),
            ("Department", "department"),
            ("Level", "level"),
            ("Gender", "gender"),
            ("Phone", "phone"),
            ("Email", "email"),
        ]
        for row, (label, key) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=5)
            entry = ttk.Entry(form, width=27)
            entry.grid(row=row, column=1, pady=5, padx=(8, 0))
            self.entries[key] = entry

        buttons = tk.Frame(form)
        buttons.grid(row=len(fields), column=0, columnspan=2, sticky="ew", pady=(14, 4))
        ttk.Button(buttons, text="Add Student", command=self.add_student).pack(fill="x", pady=3)
        ttk.Button(buttons, text="Update Selected", command=self.update_student).pack(fill="x", pady=3)
        ttk.Button(buttons, text="Delete Selected", command=self.delete_student).pack(fill="x", pady=3)
        ttk.Button(buttons, text="Clear Form", command=self.clear_form).pack(fill="x", pady=3)
        ttk.Button(buttons, text="Export Report (CSV)", command=self.export_report).pack(fill="x", pady=3)

        right = tk.Frame(body, bg="#f4f6f8")
        right.pack(side="left", fill="both", expand=True)

        search_bar = ttk.LabelFrame(right, text="Search Students", padding=10)
        search_bar.pack(fill="x", pady=(0, 10))
        self.search_entry = ttk.Entry(search_bar)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.search_entry.bind("<Return>", lambda event: self.search_students())
        ttk.Button(search_bar, text="Search", command=self.search_students).pack(side="left", padx=3)
        ttk.Button(search_bar, text="Show All", command=self.load_students).pack(side="left", padx=3)

        report_bar = ttk.Frame(right)
        report_bar.pack(fill="x", pady=(0, 8))
        self.report_label = ttk.Label(report_bar, text="Total students: 0")
        self.report_label.pack(side="left")

        table_frame = ttk.Frame(right)
        table_frame.pack(fill="both", expand=True)
        columns = ("id", "matric_no", "full_name", "department", "level", "gender", "phone", "email")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        headings = {
            "id": "ID", "matric_no": "Matric No.", "full_name": "Full Name",
            "department": "Department", "level": "Level", "gender": "Gender",
            "phone": "Phone", "email": "Email"
        }
        widths = {"id": 45, "matric_no": 105, "full_name": 150, "department": 120,
                  "level": 65, "gender": 65, "phone": 100, "email": 160}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], minwidth=45, anchor="w")
        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.load_students()

    def get_form_data(self):
        return {key: entry.get().strip() for key, entry in self.entries.items()}

    def validate(self, data):
        if not data["matric_no"] or not data["full_name"] or not data["department"] or not data["level"]:
            messagebox.showwarning("Missing information",
                                   "Matric No., Full Name, Department, and Level are required.")
            return False
        return True

    def add_student(self):
        data = self.get_form_data()
        if not self.validate(data):
            return
        try:
            self.conn.execute("""
                INSERT INTO students (matric_no, full_name, department, level, gender, phone, email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, tuple(data[k] for k in
                       ("matric_no", "full_name", "department", "level", "gender", "phone", "email")))
            self.conn.commit()
            messagebox.showinfo("Success", "Student added successfully.")
            self.clear_form()
            self.load_students()
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate matric number",
                                 "That matriculation number already exists.")

    def search_students(self):
        term = self.search_entry.get().strip()
        pattern = f"%{term}%"
        rows = self.conn.execute("""
            SELECT id, matric_no, full_name, department, level, gender, phone, email
            FROM students
            WHERE matric_no LIKE ? OR full_name LIKE ? OR department LIKE ?
            ORDER BY full_name
        """, (pattern, pattern, pattern)).fetchall()
        self.display_rows(rows)

    def load_students(self):
        rows = self.conn.execute("""
            SELECT id, matric_no, full_name, department, level, gender, phone, email
            FROM students ORDER BY id DESC
        """).fetchall()
        self.display_rows(rows)

    def display_rows(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=row)
        total = self.conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        self.report_label.config(text=f"Showing {len(rows)} record(s) | Total students: {total}")

    def on_select(self, event=None):
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        self.selected_id = values[0]
        keys = ("matric_no", "full_name", "department", "level", "gender", "phone", "email")
        for key, value in zip(keys, values[1:]):
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, value)

    def update_student(self):
        if not self.selected_id:
            messagebox.showwarning("Select a student", "Select a record from the table first.")
            return
        data = self.get_form_data()
        if not self.validate(data):
            return
        try:
            self.conn.execute("""
                UPDATE students
                SET matric_no=?, full_name=?, department=?, level=?, gender=?, phone=?, email=?
                WHERE id=?
            """, tuple(data[k] for k in
                       ("matric_no", "full_name", "department", "level", "gender", "phone", "email"))
                 + (self.selected_id,))
            self.conn.commit()
            messagebox.showinfo("Success", "Student record updated.")
            self.clear_form()
            self.load_students()
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate matric number",
                                 "Another student already uses that matriculation number.")

    def delete_student(self):
        if not self.selected_id:
            messagebox.showwarning("Select a student", "Select a record from the table first.")
            return
        if not messagebox.askyesno("Confirm deletion",
                                   "Are you sure you want to delete this student record?"):
            return
        self.conn.execute("DELETE FROM students WHERE id=?", (self.selected_id,))
        self.conn.commit()
        self.clear_form()
        self.load_students()
        messagebox.showinfo("Deleted", "Student record deleted.")

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.selected_id = None
        if hasattr(self, "tree"):
            for item in self.tree.selection():
                self.tree.selection_remove(item)

    def export_report(self):
        rows = self.conn.execute("""
            SELECT id, matric_no, full_name, department, level, gender, phone, email
            FROM students ORDER BY department, full_name
        """).fetchall()
        if not rows:
            messagebox.showinfo("No data", "There are no student records to export.")
            return
        filename = filedialog.asksaveasfilename(
            title="Save student report",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"student_report_{datetime.now():%Y%m%d}.csv"
        )
        if not filename:
            return
        headers = ["ID", "Matric No.", "Full Name", "Department", "Level",
                   "Gender", "Phone", "Email"]
        try:
            with open(filename, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(rows)
            messagebox.showinfo("Report generated", f"Report saved successfully:\n{filename}")
        except OSError as error:
            messagebox.showerror("Export error", f"Could not save report:\n{error}")

    def close(self):
        self.conn.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentDBApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
