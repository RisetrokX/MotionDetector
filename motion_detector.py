import cv2
import requests
import time
import os

# --- CONFIGURATION ---
TOPIC = "motion_detector"  # Change to your own, unique name
IMAGE_PATH = "alarm_snapshot.jpg"
COOLDOWN_SECONDS = 5  # Time in seconds between notifications

def send_alert(message, image_path=None):
    """Sends a text notification and optionally an image via ntfy.sh"""
    headers = {"Priority": "urgent"}

    if image_path and os.path.exists(image_path):
        # Send image
        with open(image_path, "rb") as f:
            requests.post(
                f"https://ntfy.sh/{TOPIC}",
                data=f,
                headers={
                    "Title": "MOTION DETECTED!",
                    "Filename": "camera.jpg",
                    "Priority": "urgent"
                }
            )
    else:
        # Send text only
        requests.post(f"https://ntfy.sh/{TOPIC}", data=message.encode('utf-8'), headers=headers)

# --- INITIALIZATION ---
cap = cv2.VideoCapture(0)
_, frame1 = cap.read()
_, frame2 = cap.read()
last_alert_time = 0

print("System started. Monitoring for motion...")

while cap.isOpened():
    # Calculate difference between frames
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)

    # If the sum of white pixels is high -> motion detected
    if thresh.sum() > 1000000:
        current_time = time.time()
        if current_time - last_alert_time > COOLDOWN_SECONDS:
            print("Motion detected! Sending alert...")

            # Save snapshot of the frame with motion
            cv2.imwrite(IMAGE_PATH, frame2)

            # Send alert
            send_alert("Motion detected in the monitored area!", IMAGE_PATH)

            last_alert_time = current_time

    # Preview (optional)
    cv2.imshow('Detection System', frame2)

    # Update frames
    frame1 = frame2
    _, frame2 = cap.read()

    # Exit on ESC key
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()