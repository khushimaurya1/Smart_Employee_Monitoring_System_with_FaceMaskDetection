# Smart Employee Mask Monitoring System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=for-the-badge" alt="OpenCV" />
  <img src="https://img.shields.io/badge/Flask-Web%20UI-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/YOLOv8-Detection-FF6B35?style=for-the-badge" alt="YOLOv8" />
</p>

A smart AI-powered monitoring system designed to detect whether employees are wearing face masks, recognize them using facial recognition, track attendance, and send automated warning emails for non-compliance.

## ✨ Highlights

- Real-time mask detection using YOLOv8
- Employee face recognition from webcam input
- Attendance logging for detected employees
- Violation tracking with warning counts
- Email notifications to employees and HR
- Web dashboard for monitoring activity and employee records
- Camera preview page for live monitoring

## 🧠 What This Project Does

This project monitors employees in a workplace environment using a webcam feed. It combines:

- Mask detection to classify each face as masked or unmasked
- Face recognition to identify the person
- Attendance tracking for recognized employees
- Automated violation logging when a person is detected without a mask
- Email alerts for warning escalation

The system produces a practical workplace safety solution for offices, factories, and smart security environments.

## 🏗️ Project Structure

```text
Face_Mask_Detection_Project/
├── app.py                  # Flask frontend entry point
├── main.py                 # Camera + detection + recognition pipeline
├── config.py               # Core app configuration
├── database.py             # SQLite database and monitoring logic
├── detector.py             # Mask detection model wrapper
├── recognizer.py           # Face recognition logic
├── tracker.py              # Warning and tracking logic
├── mail.py                 # Email sending functions
├── employee_data.py        # Employee records / HR config
├── capture_faces.py        # Face capture utility
├── register_faces.py       # Registration helper
├── train.py                # Training logic
├── screenshot.py           # Screenshot saving utility
├── static/                 # CSS and frontend assets
├── templates/              # HTML pages
├── models/                 # Trained model files
├── embeddings/             # Saved face embeddings
├── database/               # SQLite database files
├── screenshots/            # Captured violation screenshots
├── modules/                # Dataset and project utilities
├── test_*.py               # Test files for different components
├── yolov8n.pt              # YOLO model checkpoint
├── README.md               # Project documentation
└── .venv/                  # Virtual environment
```

## 🚀 Features Overview

### 1. Mask Detection
The system uses a model to identify whether a detected face is covered by a mask or not.

### 2. Face Recognition
Recognized faces are matched against stored employee data and mapped to known identities.

### 3. Attendance Tracking
When the same employee is detected reliably, the system records attendance automatically.

### 4. Violation Monitoring
Repeated non-mask detections produce warning counts and are stored in the database.

### 5. Email Alerts
The system can notify employees when violations occur and escalate to HR after repeated warnings.

### 6. Dashboard Interface
A simple Flask web UI displays:
- dashboard
- employee records
- attendance logs
- violations
- email history
- live camera page

### 7. Guest Recognition and Employee Enrollment

Every detected face is classified as a known employee or `Guest`. Guests are visible in the camera result but never receive attendance, violation warnings, or employee emails. From **Add Employee**, capture several browser camera photos during registration. The photos are stored under the employee dataset and converted into face embeddings automatically, so no separate manual photo-copy or registration command is required.

## 🛠️ Setup

1. Open the project folder.
2. Activate your virtual environment.
3. Install dependencies if they are available in your environment.

Example:

```bash
cd Face_Mask_Detection_Project
.venv\Scripts\activate
pip install opencv-python flask ultralytics Pillow
```

If your environment already has the required packages installed, you can skip the install step.

## ▶️ Run the Application

### Frontend UI

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

### Deploy as one web application

The dashboard, employee records, attendance, violations, email logs, and camera page are served from the same Flask URL. For Render, connect this repository and use the included `render.yaml`; it installs `requirements-ai.txt`, starts `wsgi:app`, and exposes the health check at `/health`. Other full-AI hosts can use the same commands:

```bash
pip install -r requirements-ai.txt
gunicorn --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT wsgi:app
```

Vercel uses the lightweight `requirements.txt` and `.vercelignore` so the dashboard can deploy within its 500 MB function limit. Vercel cannot bundle this project's full computer-vision stack and model files; deploy the AI-enabled service with Render or another host that supports larger persistent services.

Set these environment variables in the hosting provider when email alerts are required:

```text
MAIL_USERNAME=your-sending-gmail-address
MAIL_APP_PASSWORD=your-gmail-app-password
```

For local testing, copy `.env.example` to `.env` and fill in the values. Use a Gmail App Password, not your normal Gmail password, and rotate any credential that was previously exposed in source code.

Use a persistent disk or a hosted database for production data. The default SQLite database is suitable for a single-instance demo and is created automatically at startup. The browser camera sends a compressed frame to `/process_frame` approximately every 1.5 seconds. The service runs face recognition and mask detection, marks attendance for known employees, and reports processing time on the camera page. Server-side OpenCV monitoring through `main.py` remains a separate local-camera mode controlled by `ENABLE_LOCAL_MONITORING=true`.

### Camera / Detection System

```bash
python main.py
```

This starts the webcam monitoring pipeline and AI detection loop.

## 📌 Notes

- The project uses a local SQLite database for attendance, violations, and email logs.
- The system relies on trained model files in the `models` directory.
- Webcam access is required for live detection.
- If the camera is unavailable, the app may not display the live video feed.

## ⚠️ Typical Use Cases

- Office security monitoring
- Workplace health compliance checks
- Smart factory safety audits
- Attendance + safety enforcement systems

## 🤝 Contribution

You are welcome to improve the project by:

- improving the front-end design
- enhancing detection accuracy
- adding better reporting
- adding login and admin panels
- improving database reporting

## 📃 License

This project is intended for educational and practical use. Please check your organization’s policy before deploying it in production environments.

---

Made with Python, OpenCV, Flask, and AI-powered detection for smarter workplace safety.
