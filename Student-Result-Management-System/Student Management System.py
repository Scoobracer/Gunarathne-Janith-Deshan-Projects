import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import os

DB_NAME = "student_system.db"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    return sqlite3.connect(DB_NAME)

# Set up database
def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS students (
        student_id TEXT,
        student_name TEXT,
        subject TEXT,
        marks INTEGER)""")
    
    # Add default admin if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", ("admin", hash_password("admin123"), "admin"))
    
    conn.commit()
    conn.close()

class StudentResultSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Result Management System")
        self.root.geometry("800x600")
        self.root.config(bg="#f0f8ff")
        self.subjects = ["Math", "Science", "English", "History", "ICT", "Art","Chemestiry","Biology","Physics","Business Studies","Music"]
        self.main_menu()

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def main_menu(self):
        self.clear_root()
        tk.Label(self.root, text="Welcome to Student Result System", font=("Segoe UI", 20, "bold"), bg="#f0f8ff").pack(pady=30)

        ttk.Button(self.root, text="Admin Login", command=self.login_screen).pack(pady=10, ipadx=10, ipady=5)
        ttk.Button(self.root, text="View Result", command=self.student_result_screen).pack(pady=10, ipadx=10, ipady=5)

    def login_screen(self):
        self.clear_root()
        frame = tk.Frame(self.root, bg="#f7f7f7", padx=20, pady=20)
        frame.place(relx=0.5, rely=0.4, anchor="center")

        tk.Label(frame, text="Admin Login", font=("Segoe UI", 18, "bold"), bg="#f7f7f7").grid(row=0, columnspan=2, pady=10)
        tk.Label(frame, text="Username:", bg="#f7f7f7").grid(row=1, column=0, sticky="e")
        self.username_entry = tk.Entry(frame)
        self.username_entry.grid(row=1, column=1)

        tk.Label(frame, text="Password:", bg="#f7f7f7").grid(row=2, column=0, sticky="e")
        self.password_entry = tk.Entry(frame, show="*")
        self.password_entry.grid(row=2, column=1)

        ttk.Button(frame, text="Login", command=self.login_user).grid(row=3, columnspan=2, pady=10)
        ttk.Button(frame, text="Back", command=self.main_menu).grid(row=4, columnspan=2)

    def login_user(self):
        uname = self.username_entry.get().strip()
        pwd = self.password_entry.get().strip()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (uname, hash_password(pwd)))
        result = cursor.fetchone()
        conn.close()

        if result and result[0] == "admin":
            self.admin_dashboard()
        else:
            messagebox.showerror("Login Failed", "Incorrect admin credentials.")

    def admin_dashboard(self):
        self.clear_root()
        tk.Label(self.root, text=" Admin Dashboard ", font=("Segoe UI", 18, "bold"), bg="#f0f8ff").pack(pady=10)

        form = tk.Frame(self.root, bg="#f0f8ff")
        form.pack(pady=10)

        tk.Label(form, text="Student ID", bg="#f0f8ff").grid(row=0, column=0)
        self.sid_entry = tk.Entry(form)
        self.sid_entry.grid(row=0, column=1)

        tk.Label(form, text="Name", bg="#f0f8ff").grid(row=1, column=0)
        self.name_entry = tk.Entry(form)
        self.name_entry.grid(row=1, column=1)

        tk.Label(form, text="Subject", bg="#f0f8ff").grid(row=2, column=0)
        self.subject_cb = ttk.Combobox(form, values=self.subjects, state="readonly")
        self.subject_cb.grid(row=2, column=1)
        self.subject_cb.current(0)

        tk.Label(form, text="Marks", bg="#f0f8ff").grid(row=3, column=0)
        self.marks_entry = tk.Entry(form)
        self.marks_entry.grid(row=3, column=1)

        ttk.Button(self.root, text=" Add Result", command=self.add_student).pack(pady=5)
        ttk.Button(self.root, text=" View All Results", command=self.show_all_results).pack(pady=5)
        ttk.Button(self.root, text=" Logout", command=self.main_menu).pack(pady=10)

    def add_student(self):
        sid = self.sid_entry.get().strip()
        name = self.name_entry.get().strip()
        subject = self.subject_cb.get()
        marks = self.marks_entry.get().strip()

        if not sid or not name or not subject or not marks:
            messagebox.showwarning("Input Error", "All fields are required.")
            return
        if not marks.isdigit() or not (0 <= int(marks) <= 100):
            messagebox.showerror("Invalid Marks", "Enter marks between 0 and 100.")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students VALUES (?, ?, ?, ?)", (sid, name, subject, int(marks)))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success","Student Result Added Successfully!")

        self.sid_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.marks_entry.delete(0, tk.END)

    def show_all_results(self):
        win = tk.Toplevel(self.root)
        win.title("All Student Results")
        tree = ttk.Treeview(win, columns=("ID", "Name", "Subject", "Marks"), show="headings")
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill='both', expand=True)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        for row in cursor.fetchall():
            tree.insert('', tk.END, values=row)
        conn.close()

    def student_result_screen(self):
        self.clear_root()
        tk.Label(self.root, text=" Student Result Viewer", font=("Segoe UI", 18, "bold"), bg="#f0f8ff").pack(pady=20)

        tk.Label(self.root, text="Enter Your Student ID:", bg="#f0f8ff").pack()
        self.search_id_entry = tk.Entry(self.root)
        self.search_id_entry.pack(pady=5)

        ttk.Button(self.root, text=" View Result", command=self.search_student_result).pack(pady=10)
        ttk.Button(self.root, text=" Back to Main Menu", command=self.main_menu).pack(pady=5)

        self.result_area = tk.Text(self.root, height=12, width=70)
        self.result_area.pack(pady=10)

    def search_student_result(self):
        sid = self.search_id_entry.get().strip()
        self.result_area.delete("1.0", tk.END)

        if not sid:
            self.result_area.insert(tk.END, "! Please enter your student ID.")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT student_name, subject, marks FROM students WHERE student_id = ?", (sid,))
        results = cursor.fetchall()
        conn.close()

        if results:
            self.result_area.insert(tk.END, f"Results for Student ID: {sid}\n\n")
            for name, subject, marks in results:
                status = "Pass" if marks >= 50 else "Fail"
                self.result_area.insert(tk.END,f" Name: {name}|")
                self.result_area.insert(tk.END, f" Subject: {subject} | Marks: {marks} ({status})\n")
        else:
            self.result_area.insert(tk.END, "No records found for this ID.")

if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = StudentResultSystem(root)
    root.mainloop()
