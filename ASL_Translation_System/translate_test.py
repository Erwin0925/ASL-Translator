import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np
import mediapipe as mp
from sign_detection import mediapipe_detection, draw_styled_landmarks, extract_keypoints
import tensorflow as tf
from collections import Counter
import random
from PIL import Image, ImageTk
import pyodbc
import pyttsx3
import time
import threading

# Load MediaPipe holistic model and drawing utilities
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

# Load CNN model and set actions and colors
actions = np.array(["Family", "Friends", "Work", "School", "Home", "Car", "Happy", "Sad", "Play", 
                    "Help", "Eat", "Drink", "Sleep", "Sorry", "Computer", "Money", "Phone", "Cloth", "Me", "Stop"])

CNN_model = tf.keras.models.load_model("C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\Models\\CNN_Model.h5")

class TranslatePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='white')
        self.controller = controller

        self.consecutive_correct = 0  # to track consecutive correct predictions
        self.user_badge = self.fetch_user_badge()  # Assume function to fetch user badge from DB

        # Setup top bar, navigation buttons, etc.
        self.setup_ui_components()

        self.engine = pyttsx3.init()
        rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', rate - 50)

        self.sequence = []
        self.predictions = []
        self.res = [0] * len(actions)
        self.threshold = 0.7
        self.predicting = False
        self.testing = False  
        self.start_translating = False
        self.test_sign = False
        self.wait_frames = 0
        self.frame_count = 0
        self.selected_word = None
        self.mode = None
        self.display_word = ""
        self.result_display = ""

        # Badge hierarchy: higher numbers represent higher ranks
        self.badge_hierarchy = {
            "Beginner": 1,
            "Intermediate": 2,
            "Advanced": 3,
            "Legend": 4
        }

        # Initialize OpenCV video capture object
        self.initialize_video_capture()


    def setup_ui_components(self):
        # Top bar with title
        top_bar = tk.Frame(self, bg='#03045E', height=60)  
        top_bar.pack(fill='x', side='top', expand=False)

        # Define desired icon size
        logout_icon_size = (30, 30)  # width, height in pixels
        badge_icon_size = (40, 40)  # width, height in pixels

        # Load button images
        logout_icon_path = "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\Icon\\logout.png"
        badge_icon_path = "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\ASL_Translation_System\\Icon\\result.png"
        logout_image_original = Image.open(logout_icon_path)
        badge_image_original = Image.open(badge_icon_path)

        # Resize images to the defined icon_size
        logout_image_resized = logout_image_original.resize(logout_icon_size, Image.Resampling.LANCZOS)
        badge_image_resized = badge_image_original.resize(badge_icon_size, Image.Resampling.LANCZOS)

        # Convert to PhotoImage
        logout_image = ImageTk.PhotoImage(logout_image_resized)
        badge_image = ImageTk.PhotoImage(badge_image_resized)

        self.logout_button = tk.Button(top_bar, image=logout_image, borderwidth=0, bg='#03045E', activebackground='#03045E', command=self.logout)
        self.logout_button.image = logout_image  # keep a reference to the image object
        self.logout_button.pack(side='left', fill="y", expand=False, padx=10)

        self.badge_button = tk.Button(top_bar, image=badge_image, borderwidth=0, bg='#03045E', activebackground='#03045E', 
                                 command=lambda: self.controller.show_frame("BadgePage"))
        self.badge_button.image = badge_image  # keep a reference to the image object
        self.badge_button.pack(side='right', fill="y", expand=False, padx=10)

        title_label = tk.Label(top_bar, text="American Sign Language Translator", bg='#03045E', fg='white', font=("Roboto", 24))
        title_label.pack(pady=20)

        # Navigation buttons
        self.test_word_label = tk.Label(self, text=" ", bg='white', fg='#03045E', font=("Roboto", 20))
        self.test_word_label.pack(pady=(15, 10))  # Adjust padding as necessary
        
        self.video_area = tk.Label(self, bg='white')  # Create a Label widget
        self.video_area.pack(fill='both', expand=True)

        self.translated_word_label = tk.Label(self, text=" ", bg='white', fg='#03045E', font=("Roboto", 20))
        self.translated_word_label.pack(pady=(10, 15))  # Adjust padding as necessary
     
        self.dictionary_button = tk.Button(self, text="Dictionary", bg='#336081', fg='#03045E', font=("Roboto", 14), 
                                      borderwidth=0, padx=10, pady=10, command=lambda: self.controller.show_frame("DictionaryPage"))  # Increase font size or add padx and pady for bigger buttons
        self.dictionary_button.pack(side='bottom', fill='x', expand=True, padx=0, pady=0)

        # Container frame for Translate and Test buttons, set a fixed height if needed
        nav_bar = tk.Frame(self, height=80)  # You can adjust the height as needed
        nav_bar.pack_propagate(False)  # Prevent the frame from shrinking to fit its children
        nav_bar.pack(side='bottom', fill='x', expand=True)

        # Configure the Translate button
        self.translate_button = tk.Button(nav_bar, text="Translate", bg='#CAF0F8', fg='#03045E', font=("Roboto", 14), borderwidth=0, command=self.start_translating)  # Increase font size or add padx and pady for bigger buttons
        self.translate_button.pack(side='left', fill='both', expand=True, padx=0, pady=0)  # Set padx and pady to 0 to remove space between buttons

        # Configure the Test button
        self.test_button = tk.Button(nav_bar, text="Test", bg='#5D8FB3', fg='#03045E', font=("Roboto", 14), borderwidth=0, command=self.test_sign)  # Increase font size or add padx and pady for bigger buttons
        self.test_button.pack(side='left', fill='both', expand=True, padx=0, pady=0)  # Set padx and pady to 0 to remove space between buttons

    def initialize_video_capture(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Webcam Error", "Could not open webcam.")
            return
        self.start_video_stream()

    def start_video_stream(self):
        self.holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.update_video_feed()

    def start_translating(self):
        self.start_translating = True
        self.test_word_label.config(text="")
        self.translated_word_label.config(text="")
        self.mode = "translate"
        self.test_sign = False
        self.predictions.clear()
        self.disable_buttons()


    def display_translated_word(self, translated_word):
        self.translated_word_label.config(text=translated_word)
        threading.Thread(target=self.delayed_speech, args=(translated_word,)).start()
        self.enable_buttons()
    
    def delayed_speech(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def test_sign(self):
        self.mode = "test"
        self.translated_word_label.config(text="")
        self.test_word_label.config(text="")
        self.test_sign = True
        self.start_translating = False  
        self.predicting = False
        self.selected_word = random.choice(actions)
        self.display_word = f"Sign this word: {self.selected_word}"
        self.display_test_word(self.display_word)
        self.predictions.clear()
        self.user_badge = self.fetch_user_badge()
        self.disable_buttons()

    def display_test_word(self, test_word_result):
        words=test_word_result
        if words == 'Correct':
            self.test_word_label.config(fg='#00FF00')
            self.test_word_label.config(text=words)
        elif words == 'Wrong':
            self.test_word_label.config(fg='red')
            self.test_word_label.config(text=words)
        else:
            self.test_word_label.config(fg='#03045E')
            self.test_word_label.config(text=words)
    
    def update_translation_status(self, image):
        if self.start_translating:
            self.frame_count = 0
            self.wait_frames = 30  # Adjust this value as needed
            self.start_translating = False
            self.predicting = True

    def update_test_status(self, image):
        if self.test_sign:
            self.frame_count = 0
            self.wait_frames = 30  # Adjust this value as needed
            self.test_sign = False
            self.testing = True

    def update_video_feed(self):
        ret, frame = self.cap.read()
        if ret:
            # Process the frame (mediapipe detection, drawing landmarks, etc.)
            image, results = mediapipe_detection(frame, self.holistic)
            draw_styled_landmarks(image, results)

            if self.mode == "translate":
                self.update_translation_status(image)
            elif self.mode == "test":
                self.update_test_status(image)

            # Display the "Start Translating" text for the duration of self.wait_frames
            if self.wait_frames > 0:
                cv2.putText(image, "Start Action", (230, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (94, 4, 3), 2, cv2.LINE_AA)
                self.wait_frames -= 1

            if self.predicting and self.wait_frames <= 0:
                if self.frame_count < 30:
                    keypoints = extract_keypoints(results)
                    self.sequence.append(keypoints)
                    self.sequence = self.sequence[-30:]

                    if len(self.sequence) == 30:
                        res = CNN_model.predict(np.expand_dims(self.sequence, axis=0), verbose=0)[0]
                        # Store both the prediction and its confidence
                        prediction_index = np.argmax(res)
                        prediction_confidence = res[prediction_index]
                        self.predictions.append((prediction_index, prediction_confidence))

                    self.frame_count += 1

                else:
                    # Determine the most frequent action after 30 frames
                    if self.predictions:
                        # Calculate the most common prediction and its average confidence
                        prediction_counter = Counter([pred[0] for pred in self.predictions])
                        most_common_prediction, _ = prediction_counter.most_common(1)[0]
                        average_confidence = np.mean([pred[1] for pred in self.predictions if pred[0] == most_common_prediction])
                        # Check against the threshold - Only display or use the action if its confidence exceeds the threshold
                        if average_confidence > self.threshold:
                            action = actions[most_common_prediction]
                            self.display_translated_word(action)
                        else:
                            self.display_translated_word("Confidence below threshold, action is not translated")

                    # Reset prediction mode
                    self.predicting = False
                    self.start_translating = False
                    self.frame_count = 0

            elif self.testing and self.wait_frames <= 0:
                if self.frame_count < 30:
                    keypoints = extract_keypoints(results)
                    self.sequence.append(keypoints)
                    self.sequence = self.sequence[-30:]

                    if len(self.sequence) == 30:
                        res = CNN_model.predict(np.expand_dims(self.sequence, axis=0), verbose=0)[0]
                        # res = CNN_model.predict(np.expand_dims(self.sequence, axis=0))[0]
                        self.predictions.append(np.argmax(res))
                    self.frame_count += 1
                else:
                    # Compare the prediction result with the selected word
                    if self.predictions:
                        most_common = Counter(self.predictions).most_common(1)[0][0]
                        predicted_action = actions[most_common]
                        
                        correct = predicted_action == self.selected_word

                        # Call the update_test_results method with the result
                        self.update_test_results(correct)

                        if predicted_action == self.selected_word:
                            self.consecutive_correct += 1
                        else:
                            self.consecutive_correct = 0

                        self.update_user_badge()

                        self.result_display = "Correct" if predicted_action == self.selected_word else "Wrong"
                        self.display_test_word(self.result_display)

                    # Reset
                    self.testing = False
                    self.selected_word = None
                    self.display_word = ""

            cv_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv_img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_area.imgtk = imgtk  # Keep reference to avoid garbage collection
            self.video_area.configure(image=imgtk)

        self.after(10, self.update_video_feed)  # Continue updating the feed


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
        
    def update_user_badge(self):
        if self.user_badge == "Legend":
            return  # No need to update if already a Legend

        new_badge = None
        if self.consecutive_correct >= 10:
            new_badge = "legend"
        elif self.consecutive_correct >= 7:
            new_badge = "advanced"
        elif self.consecutive_correct >= 5:
            new_badge = "intermediate"
        elif self.consecutive_correct >= 3:
            new_badge = "beginner"

        # Only update the badge if it's an upgrade
        if new_badge and (self.badge_hierarchy[new_badge] > self.badge_hierarchy.get(self.user_badge, 0)):
            self.update_badge_in_database(new_badge)

    def update_badge_in_database(self, new_badge):
        try:
            conn = pyodbc.connect('DRIVER={SQL Server};SERVER=Erwin-Legion;DATABASE=ASL_Translator;Trusted_Connection=yes')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET badge=? WHERE username=?", (new_badge, self.controller.username))
            conn.commit()
            conn.close()
            self.user_badge = new_badge  # Update local badge state
            tk.messagebox.showinfo("Badge updated to {new_badge}")
        except pyodbc.Error as e:
            print("Failed to update badge:", e)

    def update_test_results(self, correct):
        try:
            # Establish the database connection
            conn = pyodbc.connect('DRIVER={SQL Server};SERVER=Erwin-Legion;DATABASE=ASL_Translator;Trusted_Connection=yes')
            cursor = conn.cursor()

            # Build the SQL query based on the result
            if correct:
                update_query = "UPDATE users SET test_correct = test_correct + 1 WHERE username = ?"
            else:
                update_query = "UPDATE users SET test_wrong = test_wrong + 1 WHERE username = ?"

            # Execute the query
            cursor.execute(update_query, (self.controller.username,))
            conn.commit()  # Commit the changes to the database

        except pyodbc.Error as e:
            print("Database error:", e)
        finally:
            # Always close the connection
            if conn:
                conn.close()
        self.enable_buttons()
    
    def disable_buttons(self):
        # Disable all buttons during translation or testing
        self.translate_button.config(state='disabled')
        self.test_button.config(state='disabled')
        self.logout_button.config(state='disabled')
        self.badge_button.config(state='disabled')
        self.dictionary_button.config(state='disabled')

    def enable_buttons(self):
        # Re-enable all buttons once the process is completed
        self.translate_button.config(state='normal')
        self.test_button.config(state='normal')
        self.logout_button.config(state='normal')
        self.badge_button.config(state='normal')
        self.dictionary_button.config(state='normal')
    
    def destroy(self):
        # Release resources when closing the application
        if self.cap.isOpened():
            self.cap.release()
        self.holistic.close()
        super().destroy()       
    
    def logout(self):
        # Ask the user for confirmation before logging out
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.translated_word_label.config(text="")
            self.test_word_label.config(text="")
            self.controller.show_frame("LoginPage")
