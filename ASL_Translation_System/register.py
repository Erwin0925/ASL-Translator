import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk 
import pyodbc
import hashlib

def hash_password(password):
    """Return the SHA-256 hash of the password."""
    return hashlib.sha256(password.encode()).hexdigest()

class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='white')  # Set the background color for the entire frame
        self.setup_ui_components()

    def setup_ui_components(self):
        # Top Frame with Title
        top_frame = tk.Frame(self, bg='#03045E')
        top_frame.pack(fill='x', side='top', expand=False)
        title_label = tk.Label(top_frame, text="American Sign Language Translator", fg='white', bg='#03045E', font=("Roboto", 15))
        title_label.pack(pady=(20, 20))

        # Title "Register"
        register_label = tk.Label(self, text="Register", font=("Roboto", 15, "bold"), fg='#03045E', bg='white')
        register_label.pack(side="top", pady=(5, 10))

        # Fields Frame
        fields_frame = tk.Frame(self, bg='white')
        fields_frame.pack(pady=5, padx=20, fill="both", expand=False)

        # Username Entry
        username_label = tk.Label(fields_frame, text="Username", bg='white', font=("Roboto", 12), fg='#03045E')
        username_label.pack(pady=(5, 0), padx=(20), anchor="w")
        self.username_entry = tk.Entry(fields_frame, font=("Roboto", 12), fg='#03045E', highlightbackground='black', highlightthickness=1)
        self.username_entry.pack(fill="x", padx=20, pady=(0, 5))

        # Security Question Combobox
        question_label = tk.Label(fields_frame, text="Choose a Security Question", bg='white', font=("Roboto", 12), fg='#03045E')
        question_label.pack(pady=(5, 0), padx=(20), anchor="w")
        
        # List of security questions
        security_questions = ["Your first pet's name?", "The city you were born in?", "Your favorite book?"]
        
        # Create a StringVar for the combobox
        question_var = tk.StringVar()
        self.question_combobox = ttk.Combobox(fields_frame, textvariable=question_var, font=("Roboto", 12), state="readonly")  # 'readonly' makes it so users can't type their own question
        self.question_combobox['values'] = security_questions  # Set the list of options
        self.question_combobox.current(0)  # Set the default value to the first question
        self.question_combobox.pack(fill="x", padx=20, pady=(0, 5))

        # Security Answer Entry
        security_ans_label = tk.Label(fields_frame, text="Answer", bg='white', font=("Roboto", 12), fg='#03045E')
        security_ans_label.pack(pady=(5, 0), padx=(20), anchor="w")
        self.security_ans_entry = tk.Entry(fields_frame, font=("Roboto", 12), fg='#03045E', highlightbackground='black', highlightthickness=1)
        self.security_ans_entry.pack(fill="x", padx=20, pady=(0, 5))

        # Password Entry
        password_label = tk.Label(fields_frame, text="Password", bg='white', font=("Roboto", 12), fg='#03045E')
        password_label.pack(pady=(5, 0), padx=(20), anchor="w")
        self.password_entry = tk.Entry(fields_frame, show="*", font=("Roboto", 12), fg='#03045E', highlightbackground='black', highlightthickness=1)
        self.password_entry.pack(fill="x", padx=20, pady=(0, 5))

        # Repeat Password Entry
        repeat_password_label = tk.Label(fields_frame, text="Renter Password", bg='white', font=("Roboto", 12), fg='#03045E')
        repeat_password_label.pack(pady=(5, 0), padx=(20), anchor="w")
        self.repeat_password_entry = tk.Entry(fields_frame, show="*", font=("Roboto", 12), fg='#03045E', highlightbackground='black', highlightthickness=1)
        self.repeat_password_entry.pack(fill="x", padx=20, pady=(0, 5))

        # Show Password Checkbox
        self.show_password_var = tk.BooleanVar()
        show_password_checkbutton = tk.Checkbutton(fields_frame, text="Show", bg='white', variable=self.show_password_var, command=lambda: self.toggle_password([self.password_entry, self.repeat_password_entry], self.show_password_var))
        show_password_checkbutton.pack(anchor="w", padx=15)

        # Bottom Frame with Navigation Buttons
        nav_frame = tk.Frame(self, bg='#03045E')
        nav_frame.pack(fill='x', side='bottom', expand=False)
        
        # Back Button
        back_button = tk.Button(nav_frame, text="Back", bg='#CAF0F8', fg='#03045E', font=("Roboto", 14), 
                                borderwidth=0, height=2, width=2, command=lambda: self.controller.show_frame("LoginPage"))
        back_button.pack(side='left', fill='x', expand=True)

        # Register Button
        register_button = tk.Button(nav_frame, text="Register", bg='#5D8FB3', fg='#03045E', 
                                    font=("Roboto", 14), borderwidth=0, height=2, width=2,command=self.register)
        register_button.pack(side='left', fill='x', expand=True)

    def toggle_password(self, entries, var):
        for entry in entries:
            entry.config(show='' if var.get() else '*')

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        repeat_password = self.repeat_password_entry.get()
        security_question = self.question_combobox.get()
        security_answer = self.security_ans_entry.get()

        if password != repeat_password:
            tk.messagebox.showerror("Error", "Passwords do not match!")
            self.password_entry.delete(0, tk.END)
            self.repeat_password_entry.delete(0, tk.END)
            return

        # Insert data into the database
        self.insert_user_into_database(username, password, security_question, security_answer)
        self.clear_fields()
        self.controller.show_frame("LoginPage")

    def insert_user_into_database(self, username, password, security_question, security_answer):
        try:
            conn = pyodbc.connect('DRIVER={SQL Server};SERVER=Erwin-Legion;DATABASE=ASL_Translator;Trusted_Connection=yes')
            cursor = conn.cursor()
            # Add the 'badge' column to the INSERT statement
            cursor.execute("""
                INSERT INTO users (username, password, security_question, security_question_answer, badge)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password, security_question, security_answer, "empty"))  # 'empty' is hard-coded
            conn.commit()
            tk.messagebox.showinfo("Success", "Registration successful!")
        except pyodbc.Error as e:
            print(e)
            tk.messagebox.showerror("Database Error", "Failed to insert record into the database, try again later")
        finally:
            if conn:
                conn.close()


    def clear_fields(self):
        """Clears all text fields in the form."""
        self.username_entry.delete(0, tk.END)
        self.security_ans_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.repeat_password_entry.delete(0, tk.END)
        self.question_combobox.set('')
        # Reset checkbox
        self.show_password_var.set(False)
