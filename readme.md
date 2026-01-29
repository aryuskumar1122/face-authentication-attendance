# Face Authentication Attendance System

A real-time **face authentication–based attendance system** built using **DeepFace (FaceNet)**, **OpenCV**, **TensorFlow**, and **SQLite**. The system performs automatic enrollment via camera, authenticates users using face embeddings, logs attendance securely, and includes a lightweight spoof-prevention mechanism.

---

## 🚀 Key Features

- 📷 **Camera-based Enrollment** (no image upload)
- 🧠 **DeepFace FaceNet embeddings** (128-D)
- 🗄️ **SQLite database** for student data & attendance
- ⚡ **GPU-accelerated inference** (TensorFlow)
- 🔐 **Privacy-preserving** (stores embeddings, not images)
- 🚫 **Spoof prevention** using motion-based liveness detection
- ❌ Automatic rejection for masks, sunglasses, or unclear faces
- 🧾 Duplicate attendance prevention (per day)

---

## 🧩 System Architecture

```
Camera
  ↓
Face Detection
  ↓
Face Embedding (FaceNet)
  ↓
Distance Matching (L2)
  ↓
Liveness Check (Motion)
  ↓
Authentication Decision
  ↓
Attendance Logging (SQLite)
```

---

## 📁 Project Structure

```
faceAuthAttain/
│
├── data/
│   ├── embeddings/          # Stored face embeddings (.npy)
│   └── attendance.db        # SQLite database
│
├── gpu_config.py            # GPU configuration
├── db.py                    # SQLite DB schema & helpers
├── enroll_camera.py         # Automatic enrollment via camera
├── authenticate_camera.py   # Authentication + attendance
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Create Virtual Environment (Recommended)

```bash
python -m venv env
env\Scripts\activate
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ MediaPipe is intentionally **not used** due to protobuf conflicts with TensorFlow.

---

## 📝 Enrollment (One-Time)

### 📸 Enrollment Demo

![Enrollment Process](attachment:fd509fb6-bdf5-48ea-b114-0a62fa34c527.png)

During enrollment, the camera automatically captures multiple valid face frames. These frames are processed using DeepFace to generate embeddings, which are averaged to create a robust facial representation for the user.

### ▶️ Running Enrollment

```bash
python enroll_camera.py
```

- Enter **Registration Number** and **Name**
- Camera captures multiple frames automatically
- Mean face embedding is generated and stored
- Student metadata saved in SQLite

📌 **Important:** Do not wear mask or sunglasses during enrollment.

---

## 🔍 Authentication & Attendance

### 📸 Authentication Demo

**Successful Authentication**

![Authorized Authentication](attachment:98bec146-ccf8-4920-a92f-d3992b03cd99.png)

**Access Denied (No Face / Invalid Match)**

![Access Denied Authentication](attachment:552713e7-a141-4af9-ae9d-80d0e6f79b45.png)

The system performs real-time face authentication using DeepFace embeddings. When a registered user is correctly identified, the system displays the user’s **Name**, **Registration Number**, and **matching distance** on the screen. If no valid face is detected or the embedding distance exceeds the threshold, access is denied.

---

### ▶️ Running Authentication

```bash
python authenticate_camera.py
```

- Live camera feed
- Face embedding extracted in real-time
- Compared with stored embeddings using L2 distance
- Motion-based liveness check prevents spoofing
- On success:
  - Name & Reg No displayed
  - Attendance marked (once per day)

---

## 🔐 Spoof Prevention Strategy

Instead of MediaPipe blink detection, a **motion-based liveness check** is used:

- Detects frame-to-frame facial motion
- Rejects static photos or screen replays
- Lightweight, dependency-free, and stable

This approach avoids protobuf conflicts while providing basic spoof protection.

---

## 📊 Embedding Details

- Model: **FaceNet (via DeepFace)**
- Vector size: **128-D float32**
- Stored as: `RegNo.npy`
- No images are stored

---

## 🛡️ Privacy & Security

- No raw images saved
- Only numerical embeddings stored
- Cannot reconstruct face from embeddings
- Separation of biometric data and metadata

---

## 🧪 Known Limitations

- Performance may degrade under extreme occlusions
- Motion-based liveness is basic (advanced spoofing is future work)
- Single-camera setup

---

## 🔮 Future Enhancements

- Advanced anti-spoofing models
- Multi-face detection & rejection
- Confidence score visualization
- Web dashboard (Streamlit)
- Role-based access control

---

## 🧠 Tech Stack

- Python 3.11
- OpenCV
- DeepFace
- TensorFlow 2.20
- NumPy
- SQLite

---

## 📌 Author

**Aryus Kumar**  
AI / ML Developer  
Lovely Professional University

---

## ✅ Conclusion

This project demonstrates a complete, real-world face authentication pipeline with strong emphasis on **system design**, **ML robustness**, and **privacy-aware implementation**, suitable for academic evaluation and technical interviews.

