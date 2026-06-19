import cv2
import requests
import time
import os

# --- KONFIGURACJA ---
TOPIC = "motion_detector"  # Zmień na własną, unikalną nazwę
IMAGE_PATH = "alarm_snapshot.jpg"
COOLDOWN_SECONDS = 5  # Czas w sekundach między powiadomieniami

def send_alert(message, image_path=None):
    """Wysyła powiadomienie tekstowe i opcjonalnie zdjęcie przez ntfy.sh"""
    headers = {"Priority": "urgent"}

    if image_path and os.path.exists(image_path):
        # Wysyłanie zdjęcia
        with open(image_path, "rb") as f:
            requests.post(
                f"https://ntfy.sh/{TOPIC}",
                data=f,
                headers={
                    "Title": "ALARM RUCHU!",
                    "Filename": "kamera.jpg",
                    "Priority": "urgent"
                }
            )
    else:
        # Wysyłanie samego tekstu
        requests.post(f"https://ntfy.sh/{TOPIC}", data=message.encode('utf-8'), headers=headers)

# --- INICJALIZACJA ---
cap = cv2.VideoCapture(0)
_, frame1 = cap.read()
_, frame2 = cap.read()
last_alert_time = 0

print("System uruchomiony. Monitoruję ruch...")

while cap.isOpened():
    # Obliczanie różnicy między klatkami
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)

    # Jeśli suma białych pikseli jest duża -> ruch
    if thresh.sum() > 1000000:
        current_time = time.time()
        if current_time - last_alert_time > COOLDOWN_SECONDS:
            print("Wykryto ruch! Wysyłam powiadomienie...")

            # Zapisz zdjęcie klatki z ruchem
            cv2.imwrite(IMAGE_PATH, frame2)

            # Wyślij powiadomienie
            send_alert("Wykryto ruch w monitorowanym obszarze!", IMAGE_PATH)

            last_alert_time = current_time

    # Podgląd (opcjonalny)
    cv2.imshow('System Detekcji', frame2)

    # Aktualizacja klatek
    frame1 = frame2
    _, frame2 = cap.read()

    # Wyjście klawiszem ESC
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()