import cv2
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==============================
# Screenshot Folder
# ==============================

SCREENSHOT_FOLDER = os.path.join(BASE_DIR, "screenshots")

os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)


# ==============================
# Save Screenshot
# ==============================

def save_screenshot(frame, employee_name):

    # Current Date & Time
    now = datetime.now()

    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

    # File Name
    filename = f"{employee_name}_{timestamp}.jpg"

    # Complete Path
    filepath = os.path.join(
        SCREENSHOT_FOLDER,
        filename
    )

    # Save Image
    cv2.imwrite(
        filepath,
        frame
    )

    print(f"📸 Screenshot Saved : {filepath}")

    return filepath