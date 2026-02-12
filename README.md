# Smart Attendance System – Raspberry Pi 4

Portable, offline face-recognition-based attendance unit designed for classroom use.

Students press a button → blink → get marked present.  
No internet required.

---

## Project Objective

Build a standalone, student-operated attendance device that:

- Works fully offline
- Uses face recognition (InsightFace)
- Performs liveness detection (blink)
- Stores attendance locally
- Provides teacher/admin web interface
- Runs on Raspberry Pi 4
- Operates using a power bank (portable)

---

## Core Attendance Flow

Target time: **2–3 seconds per student**

1. Student presses button  
2. LCD shows: "Look at camera"  
3. Blink detection (liveness check)  
4. Face recognition  
5. Attendance saved  
6. Green LED + confirmation  
7. Auto-reset  

---

## System Architecture

```
Camera → Face Detection → Embedding Extraction → Cosine Matching
                              ↓
                        Liveness Check
                              ↓
                       Attendance Engine
                              ↓
                        PostgreSQL Database
                              ↓
                      FastAPI Web Interface
```

---

## ⚙️ Hardware (Production Target)

- Raspberry Pi 4 (4GB)
- USB Webcam (720p)
- 16x2 LCD (I2C)
- Push Button (GPIO)
- 4 LEDs (Power / Processing / Success / Error)
- Optional Buzzer
- 10,000mAh Power Bank

---

## 💻 Software Stack

- Python 3.10
- InsightFace (`buffalo_sc` model)
- ONNX Runtime (CPU)
- OpenCV
- NumPy
- PostgreSQL
- FastAPI
- Uvicorn

---

## Current Development Status

### Completed
- Face recognition engine
- Embedding extraction (512-dimensional)
- Cosine similarity matching
- Webcam capture testing
- Student enrollment (live + folder-based)
- Temporary pickle-based embedding storage

### In Progress
- PostgreSQL integration
- Embedding normalization
- Recognition optimization
- Attendance session logic

### Planned
- Blink detection (EAR-based)
- State machine implementation
- Teacher/admin web interface
- Raspberry Pi hardware integration
- Systemd auto-start service
- Battery monitoring & graceful shutdown

---

## Current Data Structure (Temporary – Pickle Based)

```python
{
    "0901EO231039": {
        "name": "Omika",
        "embeddings": [embedding1, embedding2, ...]
    }
}
```

Planned migration → PostgreSQL (JSONB storage).

---

## Development Setup (Windows)

### Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install insightface onnxruntime opencv-python numpy psycopg2-binary fastapi uvicorn
```

---

## Face Recognition Model

Model used: `buffalo_sc`

- 512-dimensional embeddings
- CPU-compatible
- Suitable for Raspberry Pi 4
- Cosine similarity threshold: 0.35 – 0.40

---

## Target Performance

| Metric | Target |
|--------|--------|
| Recognition Accuracy | 99%+ |
| Liveness Accuracy | 95%+ |
| Per Student Processing Time | 2–3 seconds |
| 80 Students Total | < 13 minutes |
| Battery Runtime | 2–3 hours |

---

## Design Principles

- Offline-first architecture
- Hardware abstraction
- Clean state machine design
- No infinite loops or hangs
- Automatic reset on failure
- Duplicate prevention per session
- Production-grade error handling

---

## Future Improvements

- Embedding normalization optimization
- Optional vector search acceleration (FAISS)
- Structured logging system
- Confidence score reporting
- Web-based student enrollment dashboard

---

## License

Academic project – internal use.
