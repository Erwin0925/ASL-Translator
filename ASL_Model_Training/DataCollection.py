import cv2
import numpy as np
import os
import time
import mediapipe as mp

class DataCollection:
    def __init__(self, desired_path="C:\\Users\\erwin\\Desktop", dataset_name="ASL_Dataset2"):
        self.desired_path = desired_path
        self.dataset_name = dataset_name
        self.DATA_PATH = os.path.join(desired_path, dataset_name)
        self.actions = np.array([
            "Family", "Friends", "Work", "School", "Home", "Car", "Happy", "Sad", "Play", 
            "Help", "Eat", "Drink", "Sleep", "Sorry", "Computer", "Money", "Phone", "Cloth", "Me", "Stop"
        ])
        self.no_sequences = 40
        self.sequence_length = 30
        self.start_folder = 1

        self.mp_holistic = mp.solutions.holistic  # Holistic model
        self.mp_drawing = mp.solutions.drawing_utils  # Drawing utilities

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

    def setup_folders(self):
        for action in self.actions:
            action_path = os.path.join(self.DATA_PATH, action)
            if not os.path.exists(action_path):
                os.makedirs(action_path)
                dirmax = 0
                dir_list = []  # Initialize dir_list to ensure it's defined
            else:
                # List directories that are numeric and find the max
                dir_list = [int(dir_name) for dir_name in os.listdir(action_path) if dir_name.isdigit()]
                if dir_list:  # If the directory is not empty and has numeric folders
                    dirmax = max(dir_list)
                else:
                    dirmax = 0

            # Calculate how many new directories need to be created to reach a total of 40
            existing_dirs_count = len(dir_list)
            new_dirs_to_create = self.no_sequences - existing_dirs_count

            # Create directories if fewer than 40 exist
            if new_dirs_to_create > 0:
                for sequence in range(1, new_dirs_to_create + 1):
                    new_dir_path = os.path.join(action_path, str(dirmax + sequence))
                    os.makedirs(new_dir_path, exist_ok=True)
            else:
                print(f"No new directories needed for '{action}'. Already has {existing_dirs_count} directories.")

    def collect_data(self):
        action = input(f"Choose an action to record {self.actions}: ")

        if action not in self.actions:
            print("Invalid action selected.")
            return

        cap = cv2.VideoCapture(0)
        with self.mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            stop = False  # Global flag to stop recording
            for sequence in range(1, self.no_sequences + 1):
                if stop:
                    break
                
                ret, frame = cap.read()
                if not ret:
                    print("Failed to grab frame.")
                    break

                image, results = self.mediapipe_detection(frame, holistic)
                self.draw_styled_landmarks(image, results)

                initial_text = f'Start Collection for {action} - Video {sequence}'
                cv2.putText(image, initial_text, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)
                cv2.imshow('OpenCV Feed', image)
                cv2.waitKey(2000)

                for frame_num in range(self.sequence_length):
                    ret, frame = cap.read()
                    if not ret:
                        print("Failed to grab frame.")
                        break

                    image, results = self.mediapipe_detection(frame, holistic)
                    self.draw_styled_landmarks(image, results)

                    display_text = f'Collecting frames for {action} - Video {sequence}'
                    cv2.putText(image, display_text, (15,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
                    cv2.imshow('OpenCV Feed', image)

                    keypoints = self.extract_keypoints(results)
                    npy_path = os.path.join(self.DATA_PATH, action, str(sequence), str(frame_num))
                    np.save(npy_path, keypoints)

                    if cv2.waitKey(10) & 0xFF == ord('q'):
                        stop = True
                        break

                if stop:
                    print("Recording stopped by user.")
                    break

        cap.release()
        cv2.destroyAllWindows()