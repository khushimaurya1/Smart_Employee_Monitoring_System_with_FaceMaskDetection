import cv2
import os
import time
from register_faces import register_employee

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def capture_faces(employee_name, total_images=10):

    # -----------------------------
    # Folder Path
    # -----------------------------

    folder_path = os.path.join(
        BASE_DIR,
        "modules",
        "dataset",
        "employees",
        employee_name
    )

    os.makedirs(folder_path, exist_ok=True)

    # -----------------------------
    # Camera
    # -----------------------------

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("Camera Not Found")

        return False

    print("=" * 50)
    print(f"Capturing Images For : {employee_name}")
    print("Look Straight Towards Camera")
    print("=" * 50)

    image_count = 0

    last_capture = time.time()

    while True:

        success, frame = camera.read()

        if not success:
            break

        cv2.putText(
            frame,
            f"Images : {image_count}/{total_images}",
            (20,40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

        cv2.imshow(
            "Capture Faces",
            frame
        )

        current_time = time.time()

        # Every 1 second capture image

        if current_time - last_capture >= 1:

            image_path = os.path.join(
                folder_path,
                f"{image_count+1}.jpg"
            )

            cv2.imwrite(
                image_path,
                frame
            )

            print(f"Saved : {image_path}")

            image_count += 1

            last_capture = current_time

        if image_count >= total_images:

            break

        if cv2.waitKey(1) & 0xFF == 27:

            break

    camera.release()

    cv2.destroyAllWindows()

    print("=" * 50)
    print("Face Capture Completed")
    print("=" * 50)

    print("\nGenerating Face Embeddings...")

    registered = register_employee(employee_name)

    if registered:
        print("\nEmployee Registration Completed Successfully.")

    return registered

if __name__ == "__main__":

    name = input("Employee Name : ")

    capture_faces(name)

