import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np
import mediapipe as mp
from sign_detection import mediapipe_detection, draw_styled_landmarks, extract_keypoints
import tensorflow as tf
from collections import Counter
from webcam_manager import WebcamManager

# Load MediaPipe holistic model and drawing utilities
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

# Load LSTM model and set actions and colors
actions = np.array(["Family", "Friends", "Work", "School", "Home", "Car", "Happy", "Sad", "Play", 
                    "Help", "Eat", "Drink", "Sleep", "Sorry", "Computer", "Money", "Phone", "Clothe", "Me", "Stop"])

LSTM_model = tf.keras.models.load_model("LSTM_Model.h5")

class TestPage(tk.Frame):
    def __init__(self, parent, controller, webcam_manager):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.webcam_manager = webcam_manager

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
        

        # # Initialize OpenCV video capture object
        # self.initialize_video_capture()

        # Initialize OpenCV video capture object
        self.start_video_stream()

    def start_video_stream(self):
        try:
            self.webcam_manager.open_webcam()
            self.update_video_feed()
        except Exception as e:
            messagebox.showerror("Webcam Error", str(e))

    def setup_ui_components(self):
        # Top bar with title
        top_bar = tk.Frame(self, bg='white', height=80)  
        top_bar.pack(fill='x', side='top', expand=False)
        title_label = tk.Label(top_bar, text="American Sign Language Translator", bg='white', fg='#03045E', font=("Roboto", 24))
        title_label.pack(pady=20)

        # Navigation buttons
        nav_bar = tk.Frame(self)  
        nav_bar.pack(fill='x', side='top', expand=False)

        translate_button = tk.Button(nav_bar, text="Translate", bg='#CAF0F8', fg='#03045E', font=("Roboto", 14), height=2, borderwidth=0,
                                     command=lambda: self.controller.show_frame("TranslatePage"))
        translate_button.pack(side='left', expand=True, fill='x')

        test_button = tk.Button(nav_bar, text="Test", bg='#5D8FB3', fg='#03045E', font=("Roboto", 14), height=2, borderwidth=0)
        test_button.pack(side='left', expand=True, fill='x')

        self.video_area = tk.Label(self, bg='white')  # Create a Label widget
        self.video_area.pack(fill='both', expand=True)

        self.translated_word_label = tk.Label(self, text=" ", bg='white', fg='#03045E', font=("Roboto", 20))
        self.translated_word_label.pack(pady=(10, 15))  # Adjust padding as necessary

        # Translate button at the bottom
        translate_button_bottom = tk.Button(self, text="Translate", bg='#03045E', fg='white', font=("Roboto", 20), borderwidth=0)
        translate_button_bottom.pack(side='bottom', fill='x')
    
    def update_video_feed(self):
        print("Updating video feed")  # Debug statement
        try:
            frame = self.webcam_manager.get_frame()
            if frame is not None:
                print("Frame received")  # Debug statement
                image, results = mediapipe_detection(frame, mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5))
                draw_styled_landmarks(image, results)
                cv_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv_img)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_area.imgtk = imgtk  # Keep reference to avoid garbage collection
                self.video_area.configure(image=imgtk)
            else:
                print("No frame received")  # Debug statement
        except Exception as e:
            print("Error in update_video_feed:", str(e))  # Print error
            messagebox.showerror("Webcam Error", str(e))

        self.after(10, self.update_video_feed)  # Schedule next update


    def destroy(self):
        # Release the webcam using the webcam manager
        self.webcam_manager.release_webcam()
        super().destroy()