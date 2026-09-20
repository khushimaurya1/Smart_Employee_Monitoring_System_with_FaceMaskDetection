from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = str(BASE_DIR / "models" / "best.pt")

CAMERA_ID = 0

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Face Recognition har 15 frames me chalega
RECOGNITION_INTERVAL = 15

# Recognition Threshold
# Increase slightly to avoid rejecting valid faces from webcam frames that are
# slightly different from the stored training images.
FACE_DISTANCE_THRESHOLD = 35

# No Mask Duration (seconds)
WARNING_TIME =5