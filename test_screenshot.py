import cv2
from screenshot import save_screenshot

camera = cv2.VideoCapture(0)

success, frame = camera.read()

if success:

    path = save_screenshot(

        frame,

        "Khushi"

    )

    print(path)

camera.release()