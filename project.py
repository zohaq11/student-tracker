from tkinter import *
import tkinter.messagebox
from tkinter import colorchooser
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
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


class StudentTracker:
    def __init__(self):
        self.courses = []
        self.course_windows = {}

        self.root = Tk()
        self.root.title("Grade Tracker")
        self.root.geometry("400x600")

        # Create a new frame for the title
        self.title_frame = Frame(self.root)
        self.title_frame.pack(side="top", fill="x")

        # Create a label with the title text
        title_label = Label(self.title_frame, text="Welcome to the Student Grade Tracker", font=("Trebuchet MS", 20), bg="lightblue")

        # Add the label to the title frame and center it
        title_label.pack(side="top", anchor="center")

        # Create a new frame for the buttons
        self.button_frame = Frame(self.root)
        self.button_frame.pack(side="top", fill="x")

        self.course_frame = Frame(self.button_frame)  # Change parent to self.button_frame
        self.course_frame.pack(side="left", fill="y", expand=True)  # Add expand=True to center-align the buttons

        self.add_course_button = Button(self.course_frame, text="Add Course", bg ="lightblue", fg="black", font=("Trebuchet MS", 12), padx=20, pady=10,
                                        command=self.show_add_course_window)
        self.add_course_button.pack(pady=10, padx=10, anchor="center")  # Add anchor="center" to center-align the button

        # Add a Save button to the main window
        self.save_button = Button(self.course_frame, text="Save",bg ="lightblue", fg="black", font=("Trebuchet MS", 12), padx=20, pady=10,
                                  command=self.save_to_csv)
        self.save_button.pack(pady=10, padx=10, side="bottom",
                              anchor="center")  # Add anchor="center" to center-align the button
        self.load_data()
        self.root.mainloop()

    def load_data(self):
        if not os.path.isfile("data.csv"):
            # create the file and write a header row
            with open("data.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Course Name', 'Course Code', 'Course Color', 'Assessment Name', 'Grade', 'Weight'])
        else:
            # read the data from the file
            with open("data.csv", 'r') as f:
                reader = csv.reader(f)
                header = next(reader)

                course_dict = {}

                for row in reader:
                    name, code, color, *assessments = row + [''] * (6 - len(row))

                    if (name, code, color) not in course_dict:
                        course = Course(name, code, color)
                        self.courses.append(course)
                        course_dict[(name, code, color)] = course
                        self.add_course_button = Button(self.course_frame, text=name, bg=color,
                                                        command=lambda c=course: self.show_course(c))
                        self.add_course_button.pack(pady=5, padx=10, fill="x")
                    else:
                        course = course_dict[(name, code, color)]

                    if assessments[0] != "":
                        assessment_name = assessments[0]
                        assessment_grade = float(assessments[1])
                        assessment_weight = int(assessments[2])
                        course.add_assessment(assessment_name, assessment_grade, assessment_weight)

    def save_to_csv(self):
        with open("data.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Course Name', 'Course Code', 'Course Color', 'Assessment Name', 'Grade', 'Weight'])

            for course in self.courses:
                if not course.assessments:
                    writer.writerow([course.name, course.code, course.color])
                else:
                    for assessment in course.assessments:
                        writer.writerow([course.name, course.code, course.color, assessment[0], assessment[1], assessment[2]])

    def add_course(self, name, code, color, top=None):
        if not name or not code or not color:
            tkinter.messagebox.showerror("Error", "Please provide input for Name, Code, and Color.")
            return

        try:
            int(color[1:], 16)  # Check if the color input is a valid hexadecimal color code
        except ValueError:
            tkinter.messagebox.showerror("Error", "Invalid color input. Please enter a valid hexadecimal color code.")
            return

        course = self.find_course(name, code, color)
        if not course:
            course = Course(name, code, color)
            self.courses.append(course)
            self.add_course_button = Button(self.course_frame, text=name, bg=color,
                                            command=lambda c=course: self.show_course(c))
            self.add_course_button.pack(pady=5, padx=10, fill="x")
            top.destroy()  # close the add_course window

    def find_course(self, name, code, color):
        for course in self.courses:
            if course.name == name and course.code == code and course.color == color:
                return course
        return None

    def show_add_course_window(self):
        top = Toplevel()
        top.title("Add Course")

        name_label = Label(top, text="Name:")
        name_label.pack()
        name_entry = Entry(top)
        name_entry.pack()

        code_label = Label(top, text="Code:")
        code_label.pack()
        code_entry = Entry(top)
        code_entry.pack()

        color_label = Label(top, text="Color:")
        color_label.pack()
        color_button = Button(top, text="Choose Color", command=lambda: color_entry.insert(0, colorchooser.askcolor()[1]))
        color_button.pack()
        color_entry = Entry(top)
        color_entry.pack()

        add_button = Button(top, text="Add", command=lambda: self.add_course(name_entry.get(), code_entry.get(), color_entry.get(), top))
        add_button.pack()

        return top  # return the top window

    def show_course(self, course, top=None):
        if top:
            # update the existing course window
            top.destroy()
        if course in self.course_windows:
            # close the previous course window if it's open
            self.course_windows[course].destroy()

        top = Toplevel()
        top.title(course.name)
        # store the reference to the course window
        self.course_windows[course] = top

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
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        average_label = Label(top, text=f"Current course average: {course.get_average()}")
        average_label.pack()

        add_assessment_button = Button(top, text="Add Assessment", command=lambda: self.show_add_assessment_window(course))
        add_assessment_button.pack(pady=10)

        remove_button = Button(top, text="Remove Course", command=lambda: self.remove_course(course))
        remove_button.pack(pady=10)
        return top

    def remove_course(self, course):
        # remove the course from the list of courses
        self.courses.remove(course)

        # remove the button from the GUI
        for button in self.course_frame.pack_slaves():
            if button.cget('text') == course.name:
                button.destroy()

        # close the course window if it's open
        for window in self.root.winfo_children():
            if isinstance(window, Toplevel) and window.title() == course.name:
                window.destroy()
                # close the course window if it's open
        if course in self.course_windows:
            self.course_windows[course].destroy()
            del self.course_windows[course]

    def add_assessment(self, course, name, grade, weight, top):
        try:
            grade = float(grade)
            weight = int(weight)
            if not (0 <= grade <= 100 and 0 <= weight <= 100):
                raise ValueError

        except ValueError:
            tkinter.messagebox.showerror("Error", "Invalid grade or weight entered.")
            return

        course.add_assessment(name, grade, weight)
        top.destroy()

        # Update the course window with new assessment
        self.show_course(course)

    def show_add_assessment_window(self, course):
        top = Toplevel()
        top.title("Add Assessment")

        name_label = Label(top, text="Assessment Name:")
        name_label.pack()
        name_entry = Entry(top)
        name_entry.pack()

        grade_label = Label(top, text="Grade:")
        grade_label.pack()
        grade_entry = Entry(top)
        grade_entry.pack()

        weight_label = Label(top, text="Weight (%):")
        weight_label.pack()
        weight_entry = Entry(top)
        weight_entry.pack()

        add_button = Button(top, text="Add", command=lambda: self.add_assessment(course, name_entry.get(), grade_entry.get(), weight_entry.get(), top))
        add_button.pack()

        return top


if __name__ == '__main__':
    app = StudentTracker()
