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

# Load MediaPipe holistic model and drawing utilities
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

# Load CNN model and set actions and colors
actions = np.array(["Family", "Friends", "Work", "School", "Home", "Car", "Happy", "Sad", "Play", 
                    "Help", "Eat", "Drink", "Sleep", "Sorry", "Computer", "Money", "Phone", "Clothe", "Me", "Stop"])

CNN_model = tf.keras.models.load_model("CNN_Model.h5")

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
        self.testing = False  
        self.start_translating = False
        self.test_sign = False
        self.wait_frames = 0
        self.frame_count = 0
        self.selected_word = None
        self.mode = None
        self.display_word = ""
        self.result_display = ""

        # Initialize OpenCV video capture object
        self.initialize_video_capture()


    def setup_ui_components(self):
        # Top bar with title
        top_bar = tk.Frame(self, bg='#03045E', height=80)  
        top_bar.pack(fill='x', side='top', expand=False)
        title_label = tk.Label(top_bar, text="American Sign Language Translator", bg='#03045E', fg='white', font=("Roboto", 24))
        title_label.pack(pady=20)

        # Navigation buttons
        self.test_word_label = tk.Label(self, text=" ", bg='white', fg='#03045E', font=("Roboto", 20))
        self.test_word_label.pack(pady=(15, 10))  # Adjust padding as necessary
        
        self.video_area = tk.Label(self, bg='white')  # Create a Label widget
        self.video_area.pack(fill='both', expand=True)

        self.translated_word_label = tk.Label(self, text=" ", bg='white', fg='#03045E', font=("Roboto", 20))
        self.translated_word_label.pack(pady=(10, 15))  # Adjust padding as necessary

        nav_bar = tk.Frame(self)  
        nav_bar.pack(fill='x', side='bottom', expand=False)

        translate_button = tk.Button(nav_bar, text="Translate", bg='#CAF0F8', fg='#03045E', font=("Roboto", 14), height=2, borderwidth=0, command=self.start_translating)
        translate_button.pack(side='left', expand=True, fill='x')

        test_button = tk.Button(nav_bar, text="Test", bg='#5D8FB3', fg='#03045E', font=("Roboto", 14), height=2, borderwidth=0, command=self.test_sign)
        test_button.pack(side='left', expand=True, fill='x')
    
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

    def display_translated_word(self, translated_word):
        self.translated_word_label.config(text=translated_word)
    
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
                        print(average_confidence)
                        # Check against the threshold - Only display or use the action if its confidence exceeds the threshold
                        if average_confidence > 2:
                            action = actions[most_common_prediction]
                            self.display_translated_word(action)
                        else:
                            self.display_translated_word("Confidence below threshold, action not displayed.")

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

    def destroy(self):
        # Release resources when closing the application
        if self.cap.isOpened():
            self.cap.release()
        self.holistic.close()
        super().destroy()