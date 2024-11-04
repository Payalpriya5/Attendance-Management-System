import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from mysql.connector import Error
from datetime import date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Parthsam@5",
    "database": "attendance"
}

# Database Operations Class
class Database:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            self.create_tables()
        except Error as e:
            messagebox.showerror("Database Error", f"Error connecting to database: {e}")

    def create_tables(self):
        # Create tables if they don't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id INT AUTO_INCREMENT PRIMARY KEY,
                student_name VARCHAR(255) NOT NULL,
                gender ENUM('M', 'F') NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                attendance_date DATE,
                status ENUM('Present', 'Absent'),
                FOREIGN KEY(student_id) REFERENCES students(student_id)
            )
        ''')
        self.conn.commit()

    def add_student(self, student_name, gender):
        self.cursor.execute("INSERT INTO students (student_name, gender) VALUES (%s, %s)", (student_name, gender))
        self.conn.commit()

    def get_total_students(self):
        self.cursor.execute("SELECT COUNT(*) FROM students")
        total_students = self.cursor.fetchone()[0]
        return total_students

    def fetch_all_students(self):
        self.cursor.execute("SELECT student_id, student_name, gender FROM students")
        return self.cursor.fetchall()

    def mark_attendance(self, student_id, status):
        attendance_date = str(date.today())
        self.cursor.execute(
            "INSERT INTO attendance (student_id, attendance_date, status) VALUES (%s, %s, %s)",
            (student_id, attendance_date, status)
        )
        self.conn.commit()

    def fetch_attendance_summary(self):
        self.cursor.execute('''
            SELECT status, COUNT(*), students.gender 
            FROM attendance 
            JOIN students ON attendance.student_id = students.student_id 
            WHERE attendance_date = %s 
            GROUP BY status, students.gender
        ''', (str(date.today()),))
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()

# Main Application Class
class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.db = Database()
        
        self.root.title("Attendance Management System")
        self.root.geometry("900x800")
        self.root.config(bg="#f5f5f5")
        
        # Frames
        self.frames = {}
        self.create_frames()
        
        # Load the main frame
        self.show_frame("Main")

    def create_frames(self):
        # Create Main Frame
        main_frame = tk.Frame(self.root, bg="#f5f5f5")
        self.frames["Main"] = main_frame
        main_frame.pack(fill="both", expand=True)

        title_label = tk.Label(main_frame, text="Student Attendance System", font=("Helvetica", 18, "bold"), bg="#f5f5f5", fg="#333")
        title_label.pack(pady=20)

        # Total Students
        self.total_students_label = tk.Label(main_frame, text=f"Total Students: {self.db.get_total_students()}", font=("Helvetica", 12), bg="#f5f5f5")
        self.total_students_label.pack(pady=5)

        # Student Entry Frame
        entry_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief="groove")
        entry_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(entry_frame, text="Student Name:", bg="#ffffff", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        self.entry_student = tk.Entry(entry_frame, font=("Helvetica", 12), width=30)
        self.entry_student.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(entry_frame, text="Gender (M/F):", bg="#ffffff", font=("Helvetica", 12)).grid(row=0, column=2, padx=10, pady=10, sticky='w')
        
        self.entry_gender = tk.Entry(entry_frame, font=("Helvetica", 12), width=5)
        self.entry_gender.grid(row=0, column=3, padx=10, pady=10)
        
        tk.Button(entry_frame, text="Add Student", command=self.add_student, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold")).grid(row=0, column=4, padx=10, pady=10)

        # Student List Section
        student_list_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief="groove")
        student_list_frame.pack(pady=10, padx=20, fill="both", expand=True)

        tk.Label(student_list_frame, text="Student List", bg="#ffffff", font=("Helvetica", 12, "bold")).pack(pady=5)
        
        # Treeview to display student list
        self.student_tree = ttk.Treeview(student_list_frame, columns=("ID", "Name", "Gender"), show="headings")
        self.student_tree.heading("ID", text="ID")
        self.student_tree.heading("Name", text="Name")
        self.student_tree.heading("Gender", text="Gender")
        self.student_tree.pack(fill="both", expand=True)

        # Attendance Section
        attendance_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief="groove")
        attendance_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(attendance_frame, text="Mark Attendance:", bg="#ffffff", font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=3, pady=5)

        self.attendance_status = tk.StringVar(value="Present")
        tk.Radiobutton(attendance_frame, text="Present", variable=self.attendance_status, value="Present", font=("Helvetica", 12), bg="#ffffff").grid(row=1, column=0, pady=5)
        tk.Radiobutton(attendance_frame, text="Absent", variable=self.attendance_status, value="Absent", font=("Helvetica", 12), bg="#ffffff").grid(row=1, column=1, pady=5)

        # Centering Buttons
        button_frame = tk.Frame(attendance_frame, bg="#ffffff")
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        tk.Button(button_frame, text="Mark Attendance", command=self.mark_selected_student_attendance, bg="#0073e6", fg="white", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="View Attendance Summary", command=self.show_summary_frame, bg="#FFA500", fg="white", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT, padx=10)

        self.load_student_data()

        # Create Attendance Summary Frame
        self.create_summary_frame()

    def create_summary_frame(self):
        summary_frame = tk.Frame(self.root, bg="#f5f5f5")
        self.frames["Summary"] = summary_frame
        
        self.fig_attendance = plt.Figure(figsize=(8, 6))
        self.ax_pie = self.fig_attendance.add_subplot(111)
        self.canvas_attendance = FigureCanvasTkAgg(self.fig_attendance, master=summary_frame)
        self.canvas_attendance.get_tk_widget().pack(pady=10)
        
        self.explanation_frame = tk.Frame(summary_frame, bg="#f5f5f5")
        self.explanation_frame.pack(pady=10)
        
        tk.Button(summary_frame, text="Back to Main", command=lambda: self.show_frame("Main"), bg="#FF5733", fg="white", font=("Helvetica", 12, "bold")).pack(pady=10)

    def show_frame(self, frame_name):
        for frame in self.frames.values():
            frame.pack_forget()  # Hide all frames
        self.frames[frame_name].pack(fill="both", expand=True)  # Show the selected frame

        if frame_name == "Summary":
            self.update_summary_charts()

    def show_summary_frame(self):
        self.show_frame("Summary")

    def load_student_data(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        for student in self.db.fetch_all_students():
            self.student_tree.insert("", "end", values=student)

    def add_student(self):
        student_name = self.entry_student.get()
        gender = self.entry_gender.get().upper()
        if student_name and gender in ['M', 'F']:
            self.db.add_student(student_name, gender)
            messagebox.showinfo("Success", f"Added student '{student_name}'.")
            self.entry_student.delete(0, tk.END)
            self.entry_gender.delete(0, tk.END)
            self.load_student_data()
            self.total_students_label.config(text=f"Total Students: {self.db.get_total_students()}")
        else:
            messagebox.showwarning("Input Error", "Please enter a valid student name and gender (M/F).")

    def mark_selected_student_attendance(self):
        selected_item = self.student_tree.selection()
        if selected_item:
            student_id = self.student_tree.item(selected_item)["values"][0]
            status = self.attendance_status.get()
            self.db.mark_attendance(student_id, status)
            messagebox.showinfo("Success", f"Marked '{status}' for selected student.")
        else:
            messagebox.showwarning("Selection Error", "Please select a student to mark attendance.")

    def update_summary_charts(self):
        attendance_summary = self.db.fetch_attendance_summary()

        present_boys = next((count for status, count, gender in attendance_summary if status == 'Present' and gender == 'M'), 0)
        present_girls = next((count for status, count, gender in attendance_summary if status == 'Present' and gender == 'F'), 0)
        absent_boys = next((count for status, count, gender in attendance_summary if status == 'Absent' and gender == 'M'), 0)
        absent_girls = next((count for status, count, gender in attendance_summary if status == 'Absent' and gender == 'F'), 0)

        # Update Pie Chart
        self.ax_pie.clear()
        pie_labels = ['Present Boys', 'Present Girls', 'Absent Boys', 'Absent Girls']
        pie_counts = [present_boys, present_girls, absent_boys, absent_girls]
        
        self.ax_pie.pie(pie_counts, labels=pie_labels, autopct='%1.1f%%', startangle=90, colors=['#4CAF50', '#FFCC00', '#FF5722', '#9C27B0'])
        self.ax_pie.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
        self.ax_pie.set_title("Attendance Distribution", fontsize=14)

        self.canvas_attendance.draw()

        for widget in self.explanation_frame.winfo_children():
            widget.destroy()
        
        explanation_text = f"""
        Attendance Summary:
        Present Boys: {present_boys}   Present Girls: {present_girls}
        Absent Boys: {absent_boys}    Absent Girls: {absent_girls}
        """
        
        explanation_label = tk.Label(self.explanation_frame, text=explanation_text, bg="#f5f5f5", font=("Helvetica", 10), fg="#333")
        explanation_label.pack()

    def on_closing(self):
        self.db.close()
        self.root.destroy()

# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
