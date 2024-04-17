import tkinter as tk
from tkinter import PhotoImage
import pyodbc
from tkinter import Canvas

class BadgePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='white')  # Set the background color for the entire frame
        self.user_badge = self.fetch_user_badge()

        self.setup_ui_components()

    def setup_ui_components(self):
        # Top Frame
        top_frame = tk.Frame(self, bg='#03045E')
        top_frame.pack(fill='x', side='top', expand=False)
        # Title "American Sign Language Translator"
        title_label = tk.Label(top_frame, text="American Sign Language Translator", fg='white', bg='#03045E', font=("Roboto", 15))
        title_label.pack(pady=(20, 20))

        # Subtitle "Test Result"
        badge_label = tk.Label(self, text="Test Result", font=("Roboto", 15, "bold"), fg='#03045E', bg='white')
        badge_label.pack(side="top", fill="x", pady=(10, 0))

        # Fetch the test results from the database
        test_correct, test_wrong = self.fetch_test_results()

        # Add a Canvas widget for the donut chart
        chart_canvas = Canvas(self, width=200, height=200, bg='white', highlightthickness=0)
        chart_canvas.pack(pady=(0, 0))

        # Draw the donut chart with the test result percentages
        self.draw_donut_chart(chart_canvas, test_correct, test_wrong)

        # Subtitle "Badge"
        badge_label = tk.Label(self, text="Badges", font=("Roboto", 15, "bold"), fg='#03045E', bg='white')
        badge_label.pack(side="top", fill="x", pady=(5, 0))
                
        # Badges Frame
        badges_frame = tk.Frame(self, bg='#E0EBF3', width=250, height=250)
        badges_frame.pack(expand=True, fill='both', padx=40, pady=(10,20))
        badges_frame.pack_propagate(False)  # Prevent the frame from resizing

        # Configure the grid columns and rows to center the badges
        badges_frame.columnconfigure(0, weight=1)
        badges_frame.columnconfigure(1, weight=1)
        badges_frame.columnconfigure(2, weight=1)
        badges_frame.rowconfigure(0, weight=1)
        badges_frame.rowconfigure(1, weight=1)

        # Load badge images
        # Load badge images based on badge level
        badge_paths = {
            "beginner": ["C:/Users/erwin/Desktop/ASL_Translation_FYP/ASL_Translation_System/Badge_Icon/success_1.png"],
            "Intermediate": [
                "C:/Users/erwin/Desktop/ASL_Translation_FYP/ASL_Translation_System/Badge_Icon/success_1.png",
                "C:/Users/erwin/Desktop/ASL_Translation_FYP/ASL_Translation_System/Badge_Icon/success_2.png"
            ],
            "advanced": [
                "C:/Users/erwin/Desktop/ASL_Translation_FYP/ASL_Translation_System/Badge_Icon/success_1.png",
                "C:/Users/erwin/Desktop/ASL_Translation_FYP/ASL_Translation_System/Badge_Icon/success_2.png",
                "C:/Users/erwin/Desktop/ASL_Translation_FYP/ASL_Translation_System/Badge_Icon/success_3.png"
            ],
            "legend": [
                "C:/Users/erwin/Desktop/ASL_Translation_FYP/ASL_Translation_System/Badge_Icon/success_1.png",
                "C:/Users/erwin/Desktop/ASL_Translation_FYP/ASL_Translation_System/Badge_Icon/success_2.png",
                "C:/Users/erwin/Desktop/ASL_Translation_FYP/ASL_Translation_System/Badge_Icon/success_3.png",
                "C:/Users/erwin/Desktop/ASL_Translation_FYP/ASL_Translation_System/Badge_Icon/success_4.png"
            ]
        }
        badge_images = [PhotoImage(file=path) for path in badge_paths.get(self.user_badge, [])]  # Load images based on badge level


        # Display images
        badge_labels = []
        for i in range(2):
            for j in range(2):
                index = i * 2 + j
                if index < len(badge_images):  # Only display as many images as the badge level allows
                    badge_label = tk.Label(badges_frame, image=badge_images[index], bg='#E0EBF3')
                    badge_label.image = badge_images[index]  # Keep a reference to the image object
                    badge_label.grid(row=i, column=j + 1, sticky='nsew', padx=10, pady=10)
                    badge_labels.append(badge_label)
                

        # Back button
        nav_bar = tk.Frame(self, bg='#03045E')
        nav_bar.pack(fill='x', side='bottom', expand=False)
        
        back_button = tk.Button(nav_bar, text="Back", bg='#CAF0F8', fg='#03045E', font=("Roboto", 14), height=2, width=2,borderwidth=0, 
                                  command=lambda: self.controller.show_frame("TranslatePage"))
        back_button.pack(expand=True, fill='x')

    def fetch_user_badge(self):
        try:
            conn = pyodbc.connect('DRIVER={SQL Server};SERVER=Erwin-Legion;DATABASE=ASL_Translator;Trusted_Connection=yes')
            cursor = conn.cursor()
            cursor.execute("SELECT badge FROM users WHERE username=?", (self.controller.username,))
            result = cursor.fetchone()  # Store the result of fetchone in a variable
            badge = result[0] if result else "No badge"  # Check if result is not None
            conn.close()
            return badge
        except pyodbc.Error as e:
            print("Database error:", e)
            return None
        
    def fetch_test_results(self):
        try:
            conn = pyodbc.connect('DRIVER={SQL Server};SERVER=Erwin-Legion;DATABASE=ASL_Translator;Trusted_Connection=yes')
            cursor = conn.cursor()
            cursor.execute("SELECT test_correct, test_wrong FROM users WHERE username=?", (self.controller.username,))
            result = cursor.fetchone()
            conn.close()
            if result:
                return result
            else:
                return 0, 0
        except pyodbc.Error as e:
            print("Database error:", e)
            return 0, 0

    def draw_donut_chart(self, canvas, correct, wrong):
        # Calculate total attempts and percentage of correct answers
        total = correct + wrong
        percentage = (correct / total * 100) if total > 0 else 0
        x, y, r = 100, 100, 80  # Coordinates and radius for the chart

        # Determine chart color
        if total == 0:
            fill_color = "#D9D9D9"  # Grey if no attempts
        elif wrong == 0:
            fill_color = "#4CAF50"  # Green if all correct
        elif correct == 0:
            fill_color = "#F44336"  # Red if all wrong
        else:
            fill_color = "#4CAF50"  # Green and red will be shown proportionally

        # Draw the background circle
        canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill_color, outline="")
        # Draw the percentage arc if there are correct answers
        if correct > 0:
            canvas.create_arc(x-r, y-r, x+r, y+r, start=90, extent=-percentage*3.6, fill="#4CAF50", outline="")
        # Draw the grey arc if there are wrong answers
        if wrong > 0:
            canvas.create_arc(x-r, y-r, x+r, y+r, start=90-percentage*3.6, extent=-(100-percentage)*3.6, fill="#F44336", outline="")
        
        # Draw the inner circle to create a donut shape
        canvas.create_oval(x-r/2, y-r/2, x+r/2, y+r/2, fill="white", outline="")
        
        # Put the percentage text in the middle
        text_color = "black" if total > 0 else "#D9D9D9"  # Grey text if no attempts
        canvas.create_text(x, y, text=f"{int(percentage)}%" if total > 0 else "No Test", fill=text_color, font=("Roboto", 14))

    
        

