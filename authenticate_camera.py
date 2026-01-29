import cv2
import os
import numpy as np
from deepface import DeepFace
from gpu_config import setup_gpu
from db import get_connection, init_db
from datetime import datetime
import time
from liveness import detect_blink




setup_gpu()
init_db()

MODEL = "Facenet"
EMB_DIR = "data/embeddings"
THRESHOLD = 1.1

# control speed
PROCESS_EVERY_N_FRAMES = 10
frame_count = 0
last_result = None
last_time = 0

def mark_attendance(reg_no, name):
    conn = get_connection()
    cur = conn.cursor()

    today = datetime.now().date().isoformat()
    cur.execute(
        "SELECT 1 FROM attendance WHERE reg_no=? AND date=?",
        (reg_no, today)
    )

    if cur.fetchone() is None:
        cur.execute("""
            INSERT INTO attendance (reg_no, name, date, time, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            reg_no,
            name,
            today,
            datetime.now().strftime("%H:%M:%S"),
            "Present"
        ))
        conn.commit()

    conn.close()

def authenticate_once(frame):
    rep = DeepFace.represent(
        img_path=frame,
        model_name=MODEL,
        detector_backend="opencv",
        enforce_detection=False   # IMPORTANT
    )

    live_emb = np.array(rep[0]["embedding"])

    best_dist = float("inf")
    best_reg = None

    for file in os.listdir(EMB_DIR):
        stored_emb = np.load(os.path.join(EMB_DIR, file))
        dist = np.linalg.norm(live_emb - stored_emb)

        if dist < best_dist:
            best_dist = dist
            best_reg = file.replace(".npy", "")

    if best_dist < THRESHOLD:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM students WHERE reg_no=?", (best_reg,))
        row = cur.fetchone()
        conn.close()

        if row:
            return row[0], best_reg, best_dist

    return None, None, best_dist


cap = cv2.VideoCapture(0)
print("Authentication running...")

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (640, 480))
    frame_count += 1
    # liveness check
    if not detect_blink(frame):
        cv2.putText(frame, "NO LIVENESS DETECTED",
                (30, 40), cv2.FONT_HERSHEY_SIMPLEX,
                0.9, (0, 0, 255), 2)
        continue
    # skip frames
    if frame_count % PROCESS_EVERY_N_FRAMES == 0:
        try:
            last_result = authenticate_once(frame)
            last_time = time.time()
        except:
            last_result = (None, None, None)

    # reuse last result (smooth UI)
    if last_result and last_result[0]:
        name, reg, dist = last_result
        mark_attendance(reg, name)

        cv2.putText(frame, "AUTHORIZED", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.putText(frame, f"Name: {name}", (30, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
        cv2.putText(frame, f"RegNo: {reg}", (30, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
        cv2.putText(frame, f"Dist: {dist:.2f}", (30, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    else:
        cv2.putText(frame, "ACCESS DENIED", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    cv2.imshow("Face Authentication", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
