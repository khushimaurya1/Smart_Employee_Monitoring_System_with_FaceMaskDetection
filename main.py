import os

import cv2

from detector import MaskDetector
from recognizer import FaceRecognizer
from tracker import EmployeeTracker

from mail import send_email, send_hr_email

from employee_data import HR

from database import Database
from screenshot import save_screenshot

from config import *


# =====================================================
# CAMERA
# =====================================================

camera_backend = cv2.CAP_DSHOW if CAMERA_ID == 0 and os.name == "nt" else 0
camera = cv2.VideoCapture(CAMERA_ID, camera_backend)

if not camera.isOpened():
    camera = cv2.VideoCapture(CAMERA_ID)

camera.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    FRAME_WIDTH
)

camera.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    FRAME_HEIGHT
)


# =====================================================
# LOAD MODELS
# =====================================================

detector = MaskDetector()

recognizer = FaceRecognizer()

tracker = EmployeeTracker()

db = Database()


# =====================================================
# VARIABLES
# =====================================================

frame_count = 0

recognized_faces = []


# =====================================================
# MAIN LOOP
# =====================================================

while True:

    success, frame = camera.read()

    if not success:
        print("❌ Camera frame not received")
        break

    frame_count += 1


    # =================================================
    # FACE RECOGNITION
    # =================================================

    if frame_count % RECOGNITION_INTERVAL == 0:

        recognized_faces = recognizer.recognize(frame)
        print(f"📷 Recognized Faces: {len(recognized_faces)}")


    # =================================================
    # MASK DETECTION
    # =================================================

    results = detector.detect(frame)


    # =================================================
    # PROCESS DETECTIONS
    # =================================================

    for result in results:

        for box in result.boxes:

            # -----------------------------------------
            # Bounding Box
            # -----------------------------------------

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )


            # -----------------------------------------
            # Confidence
            # -----------------------------------------

            confidence = float(
                box.conf[0]
            )


            # -----------------------------------------
            # Class
            # -----------------------------------------

            class_id = int(
                box.cls[0]
            )


            label = result.names[class_id]


            # =================================================
            # BOX COLOR
            # =================================================

            if label == "mask":

                color = (0, 255, 0)

            else:

                color = (0, 0, 255)


            # =================================================
            # FIND PERSON NAME
            # =================================================

            person_name = "Unknown"


            for face in recognized_faces:

                fx1, fy1, fx2, fy2 = face["bbox"]


                # Face center

                cx = (fx1 + fx2) // 2

                cy = (fy1 + fy2) // 2


                # Check face inside detected box

                if (
                    x1 <= cx <= x2
                    and
                    y1 <= cy <= y2
                ):

                    person_name = face["name"]

                    break


            # =================================================
            # EMAIL / ATTENDANCE / VIOLATION LOGIC
            # =================================================

            if person_name not in ("Unknown", "Guest"):

                # -----------------------------------------
                # Attendance
                # -----------------------------------------

                db.mark_attendance(
                    person_name
                )


                # -----------------------------------------
                # Tracker
                # -----------------------------------------

                send = tracker.update(
                    person_name,
                    label
                )


                # -----------------------------------------
                # Warning Required
                # -----------------------------------------

                if send:

                    # -------------------------------------
                    # Get Employee From Database
                    # -------------------------------------

                    employee = db.get_employee(
                        person_name
                    )


                    if employee is not None:

                        # ---------------------------------
                        # Send Employee Email
                        # ---------------------------------

                        email_sent = send_email(
                            employee["email"],
                            person_name
                        )


                        if email_sent:

                            print(
                                f"✅ Warning Email Sent To "
                                f"{person_name}"
                            )


                            # -----------------------------
                            # Save Screenshot
                            # -----------------------------

                            screenshot_path = save_screenshot(
                                frame,
                                person_name
                            )


                            # -----------------------------
                            # Warning Count
                            # -----------------------------

                            warning_count = (
                                tracker.get_warning_count(
                                    person_name
                                )
                            )


                            # -----------------------------
                            # Save Violation
                            # -----------------------------

                            db.add_violation(
                                person_name,
                                warning_count
                            )


                            # -----------------------------
                            # Save Email Log
                            # -----------------------------

                            db.log_email(
                                person_name,
                                employee["email"]
                            )


                            # -----------------------------
                            # HR Email After 3 Warnings
                            # -----------------------------

                            if warning_count >= 3:

                                send_hr_email(
                                    HR["email"],
                                    person_name,
                                    warning_count,
                                    screenshot_path
                                )


                                print(
                                    "📧 HR Email Sent"
                                )


                    else:

                        print(
                            f"❌ {person_name} "
                            f"not found in database."
                        )


            # =================================================
            # DRAW RECTANGLE
            # =================================================

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                color,
                2
            )


            # =================================================
            # DRAW PERSON NAME
            # =================================================

            cv2.putText(
                frame,
                person_name,
                (x1, y1 - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )


            # =================================================
            # DRAW MASK STATUS
            # =================================================

            cv2.putText(
                frame,
                f"{label} {confidence:.2f}",
                (x1, y1 - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2
            )


    # =================================================
    # SHOW CAMERA
    # =================================================

    cv2.imshow(
        "Employee Mask Monitoring",
        frame
    )


    # =================================================
    # ESC TO EXIT
    # =================================================

    if cv2.waitKey(1) & 0xFF == 27:

        break


# =====================================================
# RELEASE CAMERA
# =====================================================

camera.release()

cv2.destroyAllWindows()