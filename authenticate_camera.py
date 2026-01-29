import cv2
import os
import numpy as np
from deepface import DeepFace
from datetime import datetime
from db import get_connection, init_db

# ---------------- CONFIG ----------------
MODEL = "Facenet"
EMB_DIR = "data/embeddings"
THRESHOLD = 5
PROCESS_EVERY_N_FRAMES = 10
MOTION_THRESHOLD = 6
# ----------------------------------------

init_db()
frame_count = 0
prev_gray = None


# ---------- MOTION-BASED LIVENESS ----------
def motion_liveness(frame):
    global prev_gray
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if prev_gray is None:
        prev_gray = gray
        return False

    diff = cv2.absdiff(prev_gray, gray)
    score = diff.mean()
    prev_gray = gray

    return score > MOTION_THRESHOLD


# ---------- ATTENDANCE (IN / OUT) ----------
def mark_attendance(reg_no, name):
    conn = get_connection()
    cur = conn.cursor()

    today = datetime.now().date().isoformat()
    now_time = datetime.now().strftime("%H:%M:%S")

    cur.execute("""
        SELECT in_time, out_time FROM attendance
        WHERE reg_no=? AND date=?
    """, (reg_no, today))

    row = cur.fetchone()

    # FIRST AUTH → IN
    if row is None:
        cur.execute("""
            INSERT INTO attendance (reg_no, name, date, in_time, out_time)
            VALUES (?, ?, ?, ?, ?)
        """, (reg_no, name, today, now_time, None))
        conn.commit()
        conn.close()
        return "IN", now_time

    in_time, out_time = row

    # SECOND AUTH → OUT
    if out_time is None:
        cur.execute("""
            UPDATE attendance
            SET out_time=?
            WHERE reg_no=? AND date=?
        """, (now_time, reg_no, today))
        conn.commit()
        conn.close()
        return "OUT", now_time

    conn.close()
    return "ALREADY_MARKED", None


# ---------- AUTHENTICATION ----------
def authenticate_once(frame):
    rep = DeepFace.represent(
        img_path=frame,
        model_name=MODEL,
        detector_backend="opencv",
        enforce_detection=False
    )

    live_emb = np.array(rep[0]["embedding"]) # type: ignore
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


# ---------- MAIN (ONE-SHOT SESSION) ----------
def main():
    global frame_count

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        print("Camera not opened")
        return

    print(" Camera started — waiting for live face")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.resize(frame, (640, 480))
        frame_count += 1

        try:
            # Process only every N frames
            if frame_count % PROCESS_EVERY_N_FRAMES == 0:

                # LIVENESS CHECK
                if not motion_liveness(frame):
                    cv2.putText(frame, "NO LIVENESS DETECTED",
                                (40, 60), cv2.FONT_HERSHEY_SIMPLEX,
                                0.9, (0, 0, 255), 2)
                    cv2.imshow("Face Authentication", frame)
                    continue

                name, reg, dist = authenticate_once(frame)

                if name:
                    status, time_val = mark_attendance(reg, name)

                    print(f"AUTHENTICATED: {name} ({reg})")
                    print(f"{status} TIME: {time_val}")

                    cv2.putText(frame, "AUTHENTICATED",
                                (50, 80), cv2.FONT_HERSHEY_SIMPLEX,
                                1.2, (0, 255, 0), 3)
                    cv2.putText(frame, f"{status} TIME: {time_val}",
                                (50, 130), cv2.FONT_HERSHEY_SIMPLEX,
                                0.9, (0, 255, 0), 2)

                    cv2.imshow("Face Authentication", frame)
                    cv2.waitKey(1500)

                    break   # EXIT IMMEDIATELY AFTER AUTH

        except Exception as e:
            print("AUTH ERROR:", e)

        cv2.imshow("Face Authentication", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Cancelled by user")
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Session ended")


if __name__ == "__main__":
    main()
