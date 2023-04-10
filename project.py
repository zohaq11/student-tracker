from tkinter import *
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
from tkinter import colorchooser
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
import os


class Course:
    def __init__(self, name, code, color):
        self.name = name
        self.code = code
        self.color = color
        self.assessments = []

    def add_assessment(self, name, grade, weight):
        self.assessments.append((name, grade, weight))

    def get_average(self):
        total_weighted_grade = 0
        total_weight = 0
        for assessment in self.assessments:
            total_weighted_grade += assessment[1] * assessment[2]
            total_weight += assessment[2]
        if total_weight == 0:
            return 0
        return round(total_weighted_grade / total_weight, 2)

    def save_to_csv(self, writer):
        for assessment in self.assessments:
            writer.writerow([self.name, self.code, self.color, assessment.name, assessment.grade, assessment.weight])


class StudentTracker:
    def __init__(self):
        self.courses = []

        self.load_data("data.csv")

        self.root = tk.Tk()
        self.root.title("Grade Tracker")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.course_frame = tk.Frame(self.root)
        self.course_frame.pack(side="left", fill="y")

        self.add_course_button = tk.Button(self.course_frame, text="Add Course", command=self.show_add_course_window)
        self.add_course_button.pack(pady=10)

        self.root.mainloop()

    def load_data(self, file_name):
        if os.path.exists("data.csv"):
            with open(file_name, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    name, code, color, *assessments = row
                    course = self.find_course(name, code, color)
                    if not course:
                        course = Course(name, code, color)
                        self.courses.append(course)
                    for i in range(0, len(assessments), 3):
                        assessment_name = assessments[i]
                        assessment_grade = float(assessments[i+1])
                        assessment_weight = int(assessments[i+2])
                        course.add_assessment(assessment_name, assessment_grade, assessment_weight)

    def save_to_csv(self, file_name):
        with open(file_name, 'w', newline='') as f:
            writer = csv.writer(f)
            for course in self.courses:
                row = [course.name, course.code, course.color]
                for assessment in course.assessments:
                    row += [assessment.name, assessment.grade, assessment.weight]
                writer.writerow(row)

    def add_course(self, name, code, color):
        course = self.find_course(name, code, color)
        if not course:
            course = Course(name, code, color)
            self.courses.append(course)
            self.add_course_button = tk.Button(self.course_frame, text=name, bg=color, command=lambda c=course: self.show_course(c))
            self.add_course_button.pack(pady=5, padx=10, fill="x")
            #top.destroy() # close the add_course window

    def find_course(self, name, code, color):
        for course in self.courses:
            if course.name == name and course.code == code and course.color == color:
                return course
        return None

    def show_add_course_window(self):
        top = tk.Toplevel()
        top.title("Add Course")

        name_label = tk.Label(top, text="Name:")
        name_label.pack()
        name_entry = tk.Entry(top)
        name_entry.pack()

        code_label = tk.Label(top, text="Code:")
        code_label.pack()
        code_entry = tk.Entry(top)
        code_entry.pack()

        color_label = tk.Label(top, text="Color:")
        color_label.pack()
        color_button = tk.Button(top, text="Choose Color", command=lambda: color_entry.insert(0, colorchooser.askcolor()[1]))
        color_button.pack()
        color_entry = tk.Entry(top)
        color_entry.pack()

        add_button = tk.Button(top, text="Add", command=lambda: self.add_course(name_entry.get(), code_entry.get(), color_entry.get()))
        add_button.pack()

        return top  # return the top window

    def show_course(self, course):
        top = tk.Toplevel()
        top.title(course.name)

        # create the bar graph
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        assessments = [a[0] for a in course.assessments]
        grades = [a[1] for a in course.assessments]
        colors = [course.color for _ in course.assessments]
        ax.bar(assessments, grades, color=colors)
        ax.set_xlabel("Assessment Name")
        ax.set_ylabel("Grade")
        ax.set_ylim(0, 100)
        ax.set_title("Course Assessments and Grades")

        # display the graph in the course window
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        average_label = tk.Label(top, text=f"Current course average: {course.get_average():.2f}")
        average_label.pack()
        add_grade_button = tk.Button(top, text="Enter Grade", command=lambda: self.show_add_grade_window(course))
        add_grade_button.pack()

        remove_button = tk.Button(top, text="Remove Course", command=lambda: self.remove_course(course, top))
        remove_button.pack()

    def remove_course(self, course, top):
        self.courses.remove(course)
        for child in self.course_frame.winfo_children():
            if isinstance(child, tk.Button) and child["text"] == course.name and child["bg"] == course.color:
                child.destroy()

    def add_grade(self, course, name, grade, weight):
        try:
            grade = float(grade)
            weight = int(weight)
            if not (0 <= grade <= 100 and 0 <= weight <= 100):
                raise ValueError
            #top.destroy()
        except ValueError:
            tkinter.messagebox.showerror("Error", "Invalid grade or weight entered.")
            return

        course.add_assessment(name, grade, weight)

        # Update the course window with new assessment
        self.show_course(course)

    def show_add_grade_window(self, course):
        top = tk.Toplevel()
        top.title("Add Grade")

        name_label = tk.Label(top, text="assessment Name:")
        name_label.pack()
        name_entry = tk.Entry(top)
        name_entry.pack()

        grade_label = tk.Label(top, text="Grade:")
        grade_label.pack()
        grade_entry = tk.Entry(top)
        grade_entry.pack()

        weight_label = tk.Label(top, text="Weight (%):")
        weight_label.pack()
        weight_entry = tk.Entry(top)
        weight_entry.pack()

        add_button = tk.Button(top, text="Add", command=lambda: self.add_grade(course, name_entry.get(), grade_entry.get(), weight_entry.get()))
        add_button.pack()


if __name__ == '__main__':
    app = StudentTracker()
