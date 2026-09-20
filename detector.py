from ultralytics import YOLO
from config import MODEL_PATH


class MaskDetector:

    def __init__(self):

        self.model = YOLO(MODEL_PATH)

    def detect(self, frame):

        results = self.model(
            frame,
            imgsz=416,
            conf=0.50,
            verbose=False
        )

        return results