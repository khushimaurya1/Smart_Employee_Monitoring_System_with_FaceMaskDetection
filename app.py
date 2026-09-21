from __future__ import annotations

import subprocess
import sys
import os
import threading
import time
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from database import Database

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
db = Database()
monitoring_enabled = os.environ.get("ENABLE_LOCAL_MONITORING", "false").lower() == "true"
frame_processing_enabled = os.environ.get("ENABLE_FRAME_PROCESSING", "true").lower() == "true"
monitoring_components = None
monitoring_lock = threading.Lock()


def get_monitoring_components():
    global monitoring_components

    if monitoring_components is None:
        from detector import MaskDetector
        from recognizer import FaceRecognizer
        from tracker import EmployeeTracker

        monitoring_components = (
            MaskDetector(),
            FaceRecognizer(),
            EmployeeTracker(),
        )

    return monitoring_components


def point_is_inside_box(point_x, point_y, box):
    x1, y1, x2, y2 = box
    return x1 <= point_x <= x2 and y1 <= point_y <= y2


def reset_monitoring_components():
    global monitoring_components
    with monitoring_lock:
        monitoring_components = None


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/health")
def health():
    return jsonify(status="ok", service="smart-employee-monitoring")


@app.route("/process_frame", methods=["POST"])
def process_frame():
    if not frame_processing_enabled:
        return jsonify(error="Frame processing is disabled"), 503

    uploaded_frame = request.files.get("image")
    if uploaded_frame is None:
        return jsonify(error="No camera frame was uploaded"), 400

    try:
        import cv2
        import numpy as np
        from employee_data import HR
        from mail import email_configuration_error, send_email, send_hr_email
        from screenshot import save_screenshot

        frame_bytes = uploaded_frame.read()
        frame = cv2.imdecode(np.frombuffer(frame_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            return jsonify(error="The uploaded camera frame is invalid"), 400

        started_at = time.perf_counter()
        with monitoring_lock:
            detector, recognizer, tracker = get_monitoring_components()
            recognized_faces = recognizer.recognize(frame)
            detection_results = detector.detect(frame)
            detections = []
            attendance_marked = []
            violations_logged = []
            email_status = "not_needed"

            for result in detection_results:
                for box in result.boxes:
                    coordinates = tuple(map(int, box.xyxy[0]))
                    class_id = int(box.cls[0])
                    label = str(result.names[class_id]).lower()
                    person_name = "Unknown"

                    for face in recognized_faces:
                        face_box = face["bbox"]
                        center_x = (face_box[0] + face_box[2]) // 2
                        center_y = (face_box[1] + face_box[3]) // 2
                        if point_is_inside_box(center_x, center_y, coordinates):
                            person_name = face["name"]
                            break

                    if person_name not in ("Unknown", "Guest"):
                        if db.mark_attendance(person_name):
                            attendance_marked.append(person_name)
                        warning_triggered = tracker.update(person_name, label)

                        if warning_triggered:
                            employee = db.get_employee(person_name)
                            if employee is not None:
                                email_sent = send_email(employee["email"], person_name)
                                screenshot_path = save_screenshot(frame, person_name)
                                warning_count = tracker.get_warning_count(person_name)
                                db.add_violation(person_name, warning_count)
                                violations_logged.append(person_name)
                                email_status = "sent" if email_sent else "failed"

                                if email_sent:
                                    db.log_email(person_name, employee["email"])

                                if warning_count >= 3:
                                    send_hr_email(
                                        HR["email"],
                                        person_name,
                                        warning_count,
                                        screenshot_path,
                                    )

                    detections.append({
                        "name": person_name,
                        "status": label,
                        "confidence": round(float(box.conf[0]), 3),
                    })

            processing_time_ms = round((time.perf_counter() - started_at) * 1000)

        return jsonify(
            detections=detections,
            attendance_marked=attendance_marked,
            violations_logged=violations_logged,
            email_status=email_status,
            email_configuration_error=email_configuration_error(),
            processing_time_ms=processing_time_ms,
        )
    except Exception as error:
        app.logger.exception("Camera frame processing failed")
        return jsonify(error=f"Camera processing failed: {error}"), 503


@app.route("/employees")
def employees():
    employees_list = db.get_all_employees()
    return render_template("employees.html", employees=employees_list)


@app.route("/add_employee")
def add_employee():
    return render_template("add_employee.html")


@app.route("/save_employee", methods=["POST"])
def save_employee():
    employee_id = request.form.get("employee_id", "").strip()
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    department = request.form.get("department", "").strip()
    designation = request.form.get("designation", "").strip()

    if not employee_id or not name or not email:
        return redirect(url_for("add_employee"))

    photo_files = [
        photo for photo in request.files.getlist("photos")
        if photo and photo.filename
    ]
    if not photo_files:
        return render_template(
            "add_employee.html",
            error="Capture at least one clear employee photo before saving.",
        ), 400

    employee_folder = BASE_DIR / "modules" / "dataset" / "employees" / secure_filename(name)
    employee_folder.mkdir(parents=True, exist_ok=True)
    saved_photos = []
    for index, photo in enumerate(photo_files, start=1):
        filename = f"registration_{int(time.time())}_{index}.jpg"
        photo_path = employee_folder / filename
        photo.save(photo_path)
        saved_photos.append(photo_path)

    from register_faces import register_employee

    if not register_employee(name):
        for photo_path in saved_photos:
            photo_path.unlink(missing_ok=True)
        return render_template(
            "add_employee.html",
            error="No face was found in the captured photos. Please try again with good lighting.",
        ), 400

    db.add_employee(
        employee_id=employee_id,
        name=name,
        email=email,
        department=department,
        designation=designation,
    )

    reset_monitoring_components()

    return redirect(url_for("employees"))


@app.route("/attendance")
def attendance():
    attendance_list = db.get_attendance()
    return render_template("attendance.html", attendance=attendance_list)


@app.route("/violations")
def violations():
    violation_list = db.get_violations()
    return render_template("violations.html", violations=violation_list)


@app.route("/email_logs")
def email_logs():
    logs = db.get_email_logs()
    return render_template("email_logs.html", email_logs=logs)


@app.route("/camera")
def camera():
    return render_template(
        "camera.html",
        running=False,
        monitoring_enabled=monitoring_enabled,
    )


@app.route("/start_monitoring", methods=["POST"])
def start_monitoring():
    if monitoring_enabled:
        script_path = BASE_DIR / "main.py"
        if script_path.exists():
            subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(BASE_DIR),
                creationflags=0,
            )
    return redirect(url_for("camera"))


if __name__ == "__main__":
    app.run(
        debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
    )
