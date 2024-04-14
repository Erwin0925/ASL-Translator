import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk

class TranslatePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

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
                                command=lambda: controller.show_frame("TestPage"))
        quiz_button.pack(side='left', expand=True, fill='x')

        # Main content area (where the OpenCV feed will go)
        self.video_area = tk.Label(self, bg='#D3D3D3')  # light grey color
        self.video_area.pack(fill='both', expand=True)

        # Translate button at the bottom
        translate_button_bottom = tk.Button(self, text="Translate", bg='#00FA9A', fg='black', font=("Arial", 18))
        translate_button_bottom.pack(side='bottom', fill='x')

        # Initialize OpenCV video capture object
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Webcam Error", "Could not open webcam.")
            return

        # Update the video_area with video feed
        self.update_video_feed()

    def update_video_feed(self):
        # Capture frame-by-frame from camera
        ret, frame = self.cap.read()
        if ret:
            # Convert the image from OpenCV BGR format to PIL RGB format
            cv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv_img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_area.imgtk = imgtk
            self.video_area.configure(image=imgtk)
        else:
            messagebox.showerror("Webcam Error", "Failed to capture frame from webcam.")

        # Call this method again after 10 milliseconds
        self.after(10, self.update_video_feed)

    def destroy(self):
        # When you want to close the application, release the camera
        if self.cap.isOpened():
            self.cap.release()
        super().destroy()

-------

import tkinter as tk
from tkinter import messagebox
import cv2
import os
import numpy as np
from PIL import Image, ImageTk
import mediapipe as mp
from sign_detection import mediapipe_detection, draw_styled_landmarks, extract_keypoints
from tensorflow.keras.models import load_model 

# Load
mp_holistic = mp.solutions.holistic # Holistic model
mp_drawing = mp.solutions.drawing_utils # Drawing utilities

# Desired path for data
desired_path = "C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP"

# Creating a subfolder for MP_Data within the desired path
DATA_PATH = os.path.join(desired_path, 'ASL_Dataset') 

# Actions that we try to detect
actions = np.array(["Family", "Friends", "Work", "School", "Home", "Car", "Happy", "Sad", "Play", 
                    "Help", "Eat", "Drink", "Sleep", "Sorry", "Computer", "Money", "Phone", "Clothe", "Me", "Stop"])

# Thirty videos worth of data
no_sequences = 30

# Videos are going to be 30 frames in length
sequence_length = 30

# Folder start
start_folder = 1

LSTM_model=load_model("LSTM_Model.keras")

colors = [(245, 117, 16), (117, 245, 16), (16, 117, 245), 
    (245, 16, 117), (117, 16, 245), (16, 245, 117), 
    (128, 0, 0), (0, 128, 0), (0, 0, 128),
    (128, 128, 0), (128, 0, 128), (0, 128, 128),
    (64, 0, 0), (0, 64, 0), (0, 0, 64),
    (64, 64, 0), (64, 0, 64), (0, 64, 64),
    (192, 64, 64), (64, 192, 64)]

# List of actions
class TranslatePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

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
                                command=lambda: controller.show_frame("TestPage"))
        quiz_button.pack(side='left', expand=True, fill='x')

        # Main content area (where the OpenCV feed will go)
        self.video_area = tk.Label(self, bg='gray')  # Placeholder color
        self.video_area.pack(fill='both', expand=True)

        # Translate button at the bottom
        translate_button_bottom = tk.Button(self, text="Translate", command=self.start_translating)
        translate_button_bottom.pack(side='bottom', fill='x')

        # Initialize OpenCV video capture object
        self.cap = cv2.VideoCapture(0)

        # Initialize prediction and translation variables
        self.sequence = []
        self.sentence = []
        self.predictions = []
        self.res = [0] * len(actions)
        self.threshold = 0.5
        self.predicting = False
        self.start_translating = False
        self.frame_count = 0

    def start_video_stream(self):
        if not self.cap.isOpened():
            messagebox.showerror("Webcam Error", "Could not open webcam.")
            return
        # Initialize the holistic model
        self.holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.update_video_feed()

    def update_video_feed(self):
        ret, frame = self.cap.read()
        if ret:
            image, results = mediapipe_detection(frame, self.holistic)
            draw_styled_landmarks(image, results)

            if self.start_translating:
                if self.frame_count < 30:
                    keypoints = extract_keypoints(results)
                    self.sequence.append(keypoints)
                    self.sequence = self.sequence[-30:]

                    if len(self.sequence) == 30:
                        res = LSTM_model.predict(np.expand_dims(self.sequence, axis=0))[0]
                        self.predictions.append(np.argmax(res))
                        
                    self.frame_count += 1
                else:
                    # Determine the most frequent action after 30 frames
                    if self.predictions:
                        most_common = self.Counter(self.predictions).most_common(1)[0][0]
                        action = actions[most_common]
                        sentence.append(action)
                    
                    # Reset prediction mode
                    self.predicting = False
                    self.frame_count = 0

                    # Limit sentence length
                    if len(sentence) > 5:
                        sentence = sentence[-5:]
            
            cv_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv_img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_area.imgtk = imgtk
            self.video_area.configure(image=imgtk)

        # Call this method again after a short delay
        self.after(10, self.update_video_feed)

    def start_translating(self):
        self.start_translating = True
        self.predictions.clear()

    def destroy(self):
        if self.cap.isOpened():
            self.cap.release()
        self.holistic.close()
        super().destroy()




 


