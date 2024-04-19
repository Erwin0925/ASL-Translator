import tkinter as tk
from tkinter import ttk 
import pyodbc
from tkinter import messagebox

class ResetPasswordPage(tk.Frame):
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

        # Title "Reset Password"
        reset_password_label = tk.Label(self, text="Reset Password", font=("Roboto", 15, "bold"), fg='#03045E', bg='white')
        reset_password_label.pack(side="top", pady=(5, 10))

        # Fields Frame
        fields_frame = tk.Frame(self, bg='white')
        fields_frame.pack(pady=5, padx=20, fill="both", expand=False)

        # Username Entry
        username_label = tk.Label(fields_frame, text="Username :", bg='white', font=("Roboto", 12), fg='#03045E')
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
        password_label = tk.Label(fields_frame, text="New Password", bg='white', font=("Roboto", 12), fg='#03045E')
        password_label.pack(pady=(5, 0), padx=(20), anchor="w")
        self.password_entry = tk.Entry(fields_frame, show="*", font=("Roboto", 12), fg='#03045E', highlightbackground='black', highlightthickness=1)
        self.password_entry.pack(fill="x", padx=20, pady=(0, 5))

        # Repeat Password Entry
        repeat_password_label = tk.Label(fields_frame, text="Renter New Password", bg='white', font=("Roboto", 12), fg='#03045E')
        repeat_password_label.pack(pady=(5, 0), padx=(20), anchor="w")
        self.repeat_password_entry = tk.Entry(fields_frame, show="*", font=("Roboto", 12), fg='#03045E', highlightbackground='black', highlightthickness=1)
        self.repeat_password_entry.pack(fill="x", padx=20, pady=(0, 5))

        # Show Password Checkbox
        self.show_password_var = tk.BooleanVar()
        self.show_password_checkbutton = tk.Checkbutton(fields_frame, text="Show", bg='white', variable=self.show_password_var, command=lambda: self.toggle_password([self.password_entry, self.repeat_password_entry], self.show_password_var))
        self.show_password_checkbutton.pack(anchor="w", padx=15)

        # Bottom Frame with Navigation Buttons
        nav_frame = tk.Frame(self, bg='#03045E')
        nav_frame.pack(fill='x', side='bottom', expand=False)

        # Back Button
        back_button = tk.Button(nav_frame, text="Back", bg='#CAF0F8', fg='#03045E', font=("Roboto", 14), 
                                borderwidth=0, height=2, width=2, command=lambda: self.controller.show_frame("LoginPage"))
        back_button.pack(side='left', fill='x', expand=True)

        # Reset Password Button
        reset_password_button = tk.Button(nav_frame, text="Reset Password", bg='#5D8FB3', fg='#03045E', 
                                          font=("Roboto", 14), borderwidth=0, height=2, width=2, command=self.reset_password)
        reset_password_button.pack(side='left', fill='x', expand=True)

    def toggle_password(self, entries, var):
        for entry in entries:
            entry.config(show='' if var.get() else '*')

    def reset_password(self):
        username = self.username_entry.get()
        security_question = self.question_combobox.get()
        security_answer = self.security_ans_entry.get()
        new_password = self.password_entry.get()
        confirm_password = self.repeat_password_entry.get()

        if new_password != confirm_password:
            messagebox.showerror("Error", "New passwords do not match!")
            self.password_entry.delete(0, tk.END)
            self.repeat_password_entry.delete(0, tk.END)
            return

        # Check the security question and answer
        if self.validate_security_info(username, security_question, security_answer):
            # Update the password in the database
            if self.update_password(username, new_password):
                messagebox.showinfo("Success", "Password has been reset successfully!")
                self.clear_fields()
                self.controller.show_frame("LoginPage")
            else:
                messagebox.showerror("Error", "Failed to reset password.")
        else:
            messagebox.showerror("Error", "Invalid username or security answer.")
            self.clear_fields()

    def validate_security_info(self, username, security_question, security_answer):
        if not self.controller.db_connection:
            messagebox.showerror("Database Error", "No active database connection.")
            return False

        try:
            cursor = self.controller.db_connection.cursor()
            cursor.execute("""
                SELECT security_question, security_question_answer FROM users 
                WHERE username=?
            """, (username,))
            row = cursor.fetchone()
            if row and row[0] == security_question and row[1] == security_answer:
                return True
            return False
        except pyodbc.Error as e:
            print("Database error:", e)
            messagebox.showerror("Database Error", "An error occurred while querying the database.")
            return False
        
    def update_password(self, username, new_password):
        if not self.controller.db_connection:
            messagebox.showerror("Database Error", "No active database connection.")
            return False

        try:
            cursor = self.controller.db_connection.cursor()
            cursor.execute("""
                UPDATE users SET password=? WHERE username=?
            """, (new_password, username))
            self.controller.db_connection.commit()
            return True
        except pyodbc.Error as e:
            print("Database error:", e)
            return False
    
    def clear_fields(self):
        """Clears all text fields in the form."""
        self.username_entry.delete(0, tk.END)
        self.security_ans_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.repeat_password_entry.delete(0, tk.END)
        self.question_combobox.set('')
        # Reset checkbox
        self.show_password_var.set(False)

