import os
import pickle

import cv2
import numpy as np

from insightface.app import FaceAnalysis

from config import FACE_DISTANCE_THRESHOLD

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "embeddings", "faces.pkl")


class FaceRecognizer:

    def __init__(self):

        self.app = FaceAnalysis(name="buffalo_l")

        self.app.prepare(
            ctx_id=-1,
            det_size=(640, 640)
        )

        with open(EMBEDDINGS_PATH, "rb") as file:

            self.database = pickle.load(file)

    def _detect_faces(self, frame):
        faces = self.app.get(frame, max_num=0)
        if faces:
            return faces

        height, width = frame.shape[:2]
        for scale in (0.75, 1.0, 1.25):
            if scale == 1.0:
                continue
            resized = cv2.resize(frame, (int(width * scale), int(height * scale)))
            resized_faces = self.app.get(resized, max_num=0)
            if resized_faces:
                return resized_faces

        return []

    def recognize(self, frame):

        if frame is None or frame.size == 0:
            return []

        if not self.database:
            return []

        faces = self._detect_faces(frame)

        results = []

        for face in faces:

            embedding = np.asarray(face.embedding, dtype=np.float32).reshape(-1)

            best_name = "Unknown"

            best_distance = float("inf")

            for name, db_embedding in self.database.items():

                db_embedding = np.asarray(db_embedding, dtype=np.float32).reshape(-1)

                distance = np.linalg.norm(
                    embedding - db_embedding
                )

                if distance < best_distance:

                    best_distance = float(distance)
                    best_name = name

            if best_distance > FACE_DISTANCE_THRESHOLD:
                best_name = "Unknown"

            x1, y1, x2, y2 = map(int, face.bbox)

            if best_name != "Unknown":
                results.append({
                    "name": best_name,
                    "bbox": (x1, y1, x2, y2),
                    "distance": best_distance
                })

        return results