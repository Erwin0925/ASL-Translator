import tkinter as tk
from tkinter import messagebox
import pyodbc

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='white')  # Set the background color for the entire frame
        self.setup_ui_components()

    def setup_ui_components(self):
        # Top Frame
        top_frame = tk.Frame(self, bg='#03045E')
        top_frame.pack(fill='x', side='top', expand=False)
        # Title "American Sign Language Translator"
        title_label = tk.Label(top_frame, text="American Sign Language Translator", fg='white', bg='#03045E', font=("Roboto", 15))
        title_label.pack(pady=(20, 20))

        # Title Frame
        title_frame = tk.Frame(self, bg='white')
        title_frame.pack(side="top", fill="x")

        # Subtitle "Login"
        login_label = tk.Label(title_frame, text="Login", font=("Roboto", 15, "bold"), fg='#03045E', bg='white')
        login_label.pack(pady=(5, 0))
        
        # Frame for Login Fields
        fields_frame = tk.Frame(self, bg='white')
        fields_frame.pack(pady=(20, 25), padx=20, fill="both", expand=False)
        
        # Username Entry
        username_label = tk.Label(fields_frame, text="Username", bg='white', font=("Roboto", 12), fg='#03045E')
        username_label.pack(pady=(5, 0), padx=(20), anchor="w")
        self.username_entry = tk.Entry(fields_frame, font=("Roboto", 12), fg='#03045E', highlightbackground='black', highlightthickness=1)
        self.username_entry.pack(fill="x", padx=(20, 20), pady=(0, 5))
        
        # Password Entry
        password_label = tk.Label(fields_frame, text="Password", bg='white', font=("Roboto", 12), fg='#03045E')
        password_label.pack(pady=(5, 0), padx=(20), anchor="w")
        self.password_entry = tk.Entry(fields_frame, show="*", font=("Roboto", 12), fg='#03045E', highlightbackground='black', highlightthickness=1)
        self.password_entry.pack(fill="x", padx=(20, 20), pady=(0, 5))
        
        # Show Password Checkbox
        self.show_password_var = tk.BooleanVar()
        show_password_checkbutton = tk.Checkbutton(fields_frame, text="Show", bg='white', variable=self.show_password_var, command=lambda: self.toggle_password(self.password_entry, self.show_password_var))
        show_password_checkbutton.pack(side="left", padx=(15, 0))
        
        # Forgot Password Button
        forgot_password_button = tk.Button(fields_frame, text="forgot password", bg='white', fg='red', relief='flat', font=("Roboto", 10, "italic"), command=lambda: self.controller.show_frame("ResetPasswordPage"))
        forgot_password_button.pack(side="right", padx=(0, 20))
        
        # Navigation Bar
        nav_bar = tk.Frame(self, bg='#03045E')
        nav_bar.pack(fill='x', side='bottom', expand=False)
        
        # Register Button
        signup_button = tk.Button(nav_bar, text="Sign Up", bg='#CAF0F8', fg='#03045E', font=("Roboto", 14), height=2, width=2,borderwidth=0, 
                                  command=lambda: self.controller.show_frame("RegisterPage"))
        signup_button.pack(side='left', expand=True, fill='x')
        
        # Login Button
        login_button = tk.Button(nav_bar, text="Login", bg='#5D8FB3', fg='#03045E', font=("Roboto", 14), height=2, width=2, borderwidth=0, 
                                 command=self.login)
        login_button.pack(side='left', expand=True, fill='x')

    def toggle_password(self, entry, var):
        entry.config(show='' if var.get() else '*')

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.validate_credentials(username, password):
            self.controller.set_username(username)
            self.clear_fields()
            # self.controller.show_frame("TranslatePage")
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password")

    def validate_credentials(self, username, password):
        if not self.controller.db_connection:
            messagebox.showerror("Database Error", "No active database connection.")
            return False

        try:
            cursor = self.controller.db_connection.cursor()
            cursor.execute("SELECT password FROM users WHERE username=?", (username,))
            result = cursor.fetchone()
            if result and result[0] == password:  # Plain text comparison, replace with hashed password comparison in production
                return True
            else:
                return False
        except pyodbc.Error as e:
            print("Failed to query the database", e)
            messagebox.showerror("Database Error", "An error occurred while querying the database.")
            return False

    def clear_fields(self):
        """Clears all text fields in the form."""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        # Reset checkbox
        self.show_password_var.set(False)