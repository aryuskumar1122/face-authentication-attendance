import cv2
import os
import numpy as np
from deepface import DeepFace
from gpu_config import setup_gpu
from db import init_db, get_connection

setup_gpu()
init_db()

MODEL = "Facenet"
SAVE_DIR = "data/embeddings"
CAPTURE_FRAMES = 30
MIN_VALID_FRAMES = 15

os.makedirs(SAVE_DIR, exist_ok=True)

reg_no = input("Enter Registration Number: ")
name = input("Enter Name: ")

cap = cv2.VideoCapture(0)
embeddings = []

print("Enrollment started. Look straight at the camera.")
print("Do NOT wear mask or sunglasses.")

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (640, 480))
    cv2.imshow("Enrollment", frame)

    try:
        rep = DeepFace.represent(
            img_path=frame,
            model_name=MODEL,
            detector_backend="opencv",  # more stable for webcam
            enforce_detection=True
        )

        emb = rep[0]["embedding"]
        if emb is not None:
            embeddings.append(emb)
            print(f"Captured valid face: {len(embeddings)}")

    except:
        pass

    if len(embeddings) >= CAPTURE_FRAMES:
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# 🔒 SAFETY CHECK
if len(embeddings) < MIN_VALID_FRAMES:
    print("❌ Enrollment failed: insufficient valid face frames")
    exit()

# ✅ SAVE EMBEDDING (ATOMIC)
mean_emb = np.mean(np.array(embeddings), axis=0)

tmp_path = f"{SAVE_DIR}/{reg_no}.tmp.npy"
final_path = f"{SAVE_DIR}/{reg_no}.npy"

np.save(tmp_path, mean_emb)
os.replace(tmp_path, final_path)

# ✅ SAVE METADATA
conn = get_connection()
cur = conn.cursor()
cur.execute(
    "INSERT OR REPLACE INTO students (reg_no, name) VALUES (?, ?)",
    (reg_no, name)
)
conn.commit()
conn.close()

print("✅ Enrollment completed successfully")
print("Saved embedding shape:", mean_emb.shape)
