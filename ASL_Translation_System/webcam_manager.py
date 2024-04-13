import cv2

class WebcamManager:
    def __init__(self):
        self.cap = None
        self.is_opened = False

    def open_webcam(self):
        if not self.is_opened:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open webcam")
            self.is_opened = True

    def get_frame(self):
        if self.is_opened:
            ret, frame = self.cap.read()
            if ret:
                return frame
            else:
                raise Exception("Failed to capture frame from webcam.")
        else:
            raise Exception("Webcam is not opened")

    def release_webcam(self):
        if self.is_opened:
            self.cap.release()
            self.is_opened = False
