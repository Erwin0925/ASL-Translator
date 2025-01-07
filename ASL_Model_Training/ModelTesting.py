import cv2
import numpy as np
import mediapipe as mp
from collections import Counter
import tensorflow as tf
import random

class ModelTesting:
    def __init__(self, model_path="C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP\\Models\\LSTM_Model.h5"):
        self.actions = np.array([
            "Family", "Friends", "Work", "School", "Home", "Car", "Happy", "Sad", "Play", 
            "Help", "Eat", "Drink", "Sleep", "Sorry", "Computer", "Money", "Phone", "Cloth", "Me", "Stop"
        ])
        self.model = tf.keras.models.load_model(model_path)
        self.mp_holistic = mp.solutions.holistic  # Holistic model
        self.mp_drawing = mp.solutions.drawing_utils  # Drawing utilities
        self.colors = [(245, 117, 16), (117, 245, 16), (16, 117, 245), 
                       (245, 16, 117), (117, 16, 245), (16, 245, 117), 
                       (128, 0, 0), (0, 128, 0), (0, 0, 128),
                       (128, 128, 0), (128, 0, 128), (0, 128, 128),
                       (64, 0, 0), (0, 64, 0), (0, 0, 64),
                       (64, 64, 0), (64, 0, 64), (0, 64, 64),
                       (192, 64, 64), (64, 192, 64)]

    def mediapipe_detection(self, image, model):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # COLOR CONVERSION BGR to RGB
        image.flags.writeable = False  # Image is no longer writeable
        results = model.process(image)  # Make prediction
        image.flags.writeable = True  # Image is now writeable 
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # COLOR COVERSION RGB to BGR
        return image, results

    def draw_styled_landmarks(self, image, results):
        # Draw face connections
        self.mp_drawing.draw_landmarks(image, results.face_landmarks, self.mp_holistic.FACEMESH_CONTOURS, 
                                       self.mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1), 
                                       self.mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1))
        # Draw pose connections
        self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_holistic.POSE_CONNECTIONS,
                                       self.mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4), 
                                       self.mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2))
        # Draw left hand connections
        self.mp_drawing.draw_landmarks(image, results.left_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS, 
                                       self.mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=2), 
                                       self.mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=1))
        # Draw right hand connections  
        self.mp_drawing.draw_landmarks(image, results.right_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS, 
                                       self.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2), 
                                       self.mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=1))

    def extract_keypoints(self, results):
        pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
        face = np.array([[res.x, res.y, res.z] for res in results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468*3)
        lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
        rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
        return np.concatenate([pose, face, lh, rh])

    def prob_viz(self, res, actions, input_frame, colors):
        output_frame = input_frame.copy()
        font_scale = 0.5
        line_thickness = 1
        space_per_action = 20