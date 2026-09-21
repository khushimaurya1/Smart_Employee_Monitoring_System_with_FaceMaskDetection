# Smart Employee Monitoring System

Flask dashboard for workplace mask monitoring, employee face recognition, attendance, guest detection, violation tracking, screenshots, and email alerts.

## Features

- YOLO mask/no-mask detection
- Face recognition for registered employees
- Multiple people per camera frame
- Unknown people classified as `Guest`
- Guests never receive attendance or employee warnings
- Attendance marked once per employee per day
- No-mask warning tracking and screenshots
- Employee and HR email notifications
- Responsive dashboard for desktop, tablet, and mobile
- Browser camera capture for hosted deployments
- Employee photo capture during registration, with automatic embeddings
- Email, attendance, and violation logs

## Architecture

The application has two deployment modes:

1. **Full-AI service:** Runs Flask, OpenCV, YOLO, InsightFace, SQLite, email alerts, and `/process_frame`. Use Render or another service with enough memory and disk for the models.
2. **Vercel dashboard:** Serves the lightweight responsive web interface. It forwards camera frames to the full-AI service through `AI_SERVICE_URL`.

Vercel cannot bundle the computer-vision dependencies and model files because its function limit is 500 MB. The split deployment is required for hosted live recognition.

## Project Structure

```text
Face_Mask_Detection_Project/
├── app.py                  # Flask routes and frame processing
├── api/index.py            # Vercel Flask entrypoint
├── wsgi.py                 # WSGI entrypoint for full-AI hosts
├── detector.py             # YOLO wrapper
├── recognizer.py           # InsightFace recognition
├── database.py             # SQLite records and logs
├── register_faces.py       # Photo-to-embedding registration
├── requirements.txt        # Lightweight Vercel dependencies
├── requirements-ai.txt     # Full recognition service dependencies
├── render.yaml             # Render full-AI service configuration
├── vercel.json             # Vercel routing configuration
├── .vercelignore           # Excludes large AI assets from Vercel
├── templates/              # Dashboard pages
├── static/                 # Responsive CSS and assets
├── models/                 # YOLO model files
├── embeddings/             # Employee face embeddings
└── modules/dataset/        # Registered employee photos
```

## Local Setup

```bash
cd Face_Mask_Detection_Project
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements-ai.txt
```

Run the full application:

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

For the desktop OpenCV camera loop instead of the browser camera:

```bash
python main.py
```

## Employee Enrollment

Open **Add Employee**, enter the employee details, allow camera access, capture several clear photos, and submit the form. Photos are saved automatically and converted into embeddings. No manual photo copying or separate registration command is needed.

## Deployment

### Full-AI service

Connect the repository to Render. The included `render.yaml` installs `requirements-ai.txt`, starts `wsgi:app`, binds to `$PORT`, and uses `/health` as its health check.

Equivalent commands:

```bash
pip install -r requirements-ai.txt
gunicorn --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT wsgi:app
```

### Vercel dashboard

Connect the repository to Vercel with the project root as the Root Directory. Vercel uses `requirements.txt`, `vercel.json`, and `.vercelignore`. Set `AI_SERVICE_URL` to the deployed full-AI service URL so `/process_frame` is forwarded there.

## Environment Variables

Set these on the full-AI service:

```text
MAIL_USERNAME=your-sending-gmail-address
MAIL_APP_PASSWORD=your-gmail-app-password
```

Set this on Vercel:

```text
AI_SERVICE_URL=https://your-full-ai-service.example.com
```

For local email testing, copy `.env.example` to `.env`. Use a Gmail App Password, never your regular Gmail password. Never commit `.env`.

Use a persistent disk or external database for production. SQLite, embeddings, employee photos, and screenshots are local files; Vercel's filesystem is temporary.

## Camera Processing

The browser captures a compressed frame about every 1.5 seconds. The full-AI service recognizes all visible faces, labels unknown people as `Guest`, marks attendance only for registered employees, and returns processing time to the camera page. No-mask warnings are tracked for employees and can create screenshots, violation records, and emails.

## Validation

```bash
python -m py_compile app.py database.py mail.py recognizer.py register_faces.py
```

## License

This project is intended for educational and practical use. Please check your organization’s policy before deploying it in production environments.
