import cv2
from recognizer import FaceRecognizer

camera = cv2.VideoCapture(0)

recognizer = FaceRecognizer()

while True:

    success, frame = camera.read()

    if not success:
        break

    faces = recognizer.recognize(frame)

    for face in faces:

        x1, y1, x2, y2 = face["bbox"]

        name = face["name"]

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

        cv2.putText(
            frame,
            name,
            (x1, y1-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0,255,0),
            2
        )

    cv2.imshow("Face Recognition Test", frame)

    if cv2.waitKey(1) == 27:
        break

camera.release()
cv2.destroyAllWindows()