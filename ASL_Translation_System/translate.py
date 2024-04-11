import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np
import mediapipe as mp
from sign_detection import mediapipe_detection, draw_styled_landmarks, extract_keypoints
import tensorflow as tf
from collections import Counter

# Load MediaPipe holistic model and drawing utilities
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

# Load LSTM model and set actions and colors
actions = np.array(["Family", "Friends", "Work", "School", "Home", "Car", "Happy", "Sad", "Play", 
                    "Help", "Eat", "Drink", "Sleep", "Sorry", "Computer", "Money", "Phone", "Clothe", "Me", "Stop"])

LSTM_model = tf.keras.models.load_model("LSTM_Model.h5")

class TranslatePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='white')
        self.controller = controller

        # Setup top bar, navigation buttons, etc.
        self.setup_ui_components()

        self.sequence = []
        self.predictions = []
        self.res = [0] * len(actions)
        self.threshold = 0.5
        self.predicting = False
        self.start_translating = False
        self.wait_frames = 0
        self.frame_count = 0

        # Initialize OpenCV video capture object
        self.initialize_video_capture()


    def setup_ui_components(self):
        # Top bar with title
        top_bar = tk.Frame(self, bg='#00B2EE', height=100)  # light blue color
        top_bar.pack(fill='x', side='top', expand=False)
        title_label = tk.Label(top_bar, text="American Sign Language Translator", bg='#00B2EE', fg='white', font=("Arial", 24))
        title_label.pack(pady=20)

        # Navigation buttons
        nav_bar = tk.Frame(self, bg='#3CB371')  # green color
        nav_bar.pack(fill='x', side='top', expand=False)

        translate_button = tk.Button(nav_bar, text="Translate", bg='#3CB371', fg='white', font=("Arial", 14))
        translate_button.pack(side='left', expand=True, fill='x')

        quiz_button = tk.Button(nav_bar, text="Quiz", bg='#3CB371', fg='white', font=("Arial", 14),
                                command=lambda: self.controller.show_frame("TestPage"))
        quiz_button.pack(side='left', expand=True, fill='x')

        self.video_area = tk.Label(self, bg='gray')  # Create a Label widget
        self.video_area.pack(fill='both', expand=True)

        self.translated_word_label = tk.Label(self, text="-", bg='white', font=("Arial", 20))
        self.translated_word_label.pack(pady=(10, 10))  # Adjust padding as necessary

        # Translate button at the bottom
        translate_button_bottom = tk.Button(self, text="Translate", bg='#00FA9A', fg='black', font=("Arial", 18), command=self.start_translating)
        translate_button_bottom.pack(side='bottom', fill='x')

    def display_translated_word(self, translated_word):
        self.translated_word_label.config(text=translated_word)
    
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
        self.predictions.clear()

    def update_video_feed(self):
        ret, frame = self.cap.read()
        if ret:
            # Process the frame (mediapipe detection, drawing landmarks, etc.)
            image, results = mediapipe_detection(frame, self.holistic)
            draw_styled_landmarks(image, results)

            if self.start_translating:
                self.frame_count = 0
                self.wait_frames = 30  # Adjust this value as needed
                self.start_translating = False
                self.predicting = True

            # Display the "Start Translating" text for the duration of self.wait_frames
            if self.wait_frames > 0:
                cv2.putText(image, "Start Translation", (190, 270),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                self.wait_frames -= 1

            if self.predicting and self.wait_frames <= 0:
                if self.frame_count < 30:
                    keypoints = extract_keypoints(results)
                    self.sequence.append(keypoints)
                    self.sequence = self.sequence[-30:]

                    if len(self.sequence) == 30:
                        res = LSTM_model.predict(np.expand_dims(self.sequence, axis=0), verbose=0)[0]
                        # res = LSTM_model.predict(np.expand_dims(self.sequence, axis=0))[0]
                        self.predictions.append(np.argmax(res))
                        
                    self.frame_count += 1
                else:
                    # Determine the most frequent action after 30 frames
                    if self.predictions:
                        most_common = Counter(self.predictions).most_common(1)[0][0]
                        action = actions[most_common]
                        self.display_translated_word(action)

                    # Reset prediction mode
                    self.predicting = False
                    self.start_translating = False
                    self.frame_count = 0
            
            cv_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv_img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_area.imgtk = imgtk  # Keep reference to avoid garbage collection
            self.video_area.configure(image=imgtk)

        self.after(10, self.update_video_feed)  # Continue updating the feed

    def destroy(self):
        # Release resources when closing the application
        if self.cap.isOpened():
            self.cap.release()
        self.holistic.close()
        super().destroy()




 


