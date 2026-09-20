import os
import cv2
import pickle
import numpy as np
from insightface.app import FaceAnalysis

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -----------------------------
# Face Recognition Model
# -----------------------------
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=-1, det_size=(640, 640))

EMBEDDINGS_PATH = os.path.join(BASE_DIR, "embeddings", "faces.pkl")


def register_employee(employee_name):

    dataset_path = os.path.join(
        BASE_DIR,
        "modules",
        "dataset",
        "employees",
        employee_name
    )

    if not os.path.exists(dataset_path):

        print("Employee Folder Not Found")
        return

    embeddings = []

    for image_name in os.listdir(dataset_path):

        image_path = os.path.join(
            dataset_path,
            image_name
        )

        image = cv2.imread(image_path)

        if image is None:
            continue

        faces = app.get(image)

        if len(faces) == 0:
            continue

        embeddings.append(
            faces[0].embedding
        )

    if len(embeddings) == 0:

        print("No Face Found")

        return False

    os.makedirs("embeddings", exist_ok=True)

    if os.path.exists(EMBEDDINGS_PATH):
        with open(EMBEDDINGS_PATH, "rb") as file:
            database = pickle.load(file)
    else:
        database = {}

    database[employee_name] = np.mean(embeddings, axis=0)

    with open(EMBEDDINGS_PATH, "wb") as file:
        pickle.dump(database, file)

    print(f"Embedding Saved : {employee_name}")
    return True


def rebuild_database():

    dataset_path = os.path.join(BASE_DIR, "modules", "dataset", "employees")

    if not os.path.exists(dataset_path):
        print("Dataset folder not found")
        return

    database = {}

    for person_name in os.listdir(dataset_path):

        person_folder = os.path.join(dataset_path, person_name)

        if not os.path.isdir(person_folder):
            continue

        embeddings = []

        for image_name in os.listdir(person_folder):

            image = cv2.imread(os.path.join(person_folder, image_name))

            if image is None:
                continue

            faces = app.get(image)

            if len(faces) > 0:
                embeddings.append(faces[0].embedding)

        if embeddings:
            database[person_name] = np.mean(embeddings, axis=0)

    os.makedirs(os.path.join(BASE_DIR, "embeddings"), exist_ok=True)

    with open(EMBEDDINGS_PATH, "wb") as file:
        pickle.dump(database, file)

    print("Face Database Created Successfully")


if __name__ == "__main__":
    rebuild_database()