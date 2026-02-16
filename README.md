# Smart Attendance System – Raspberry Pi 4

Offline, portable face-recognition-based attendance system.

Students press a button, blink, and get marked present.  
No internet connection required.

---

## Project Roadmap

### Current (Almost Done)

- Face recognition using InsightFace (`buffalo_sc`)
- PostgreSQL database integration with attendance engine
- Blink detection (liveness verification)

---

### After Blink Detection

- Combine face recognition, blink detection, and attendance logic into a single unified pipeline
- Perform full end-to-end testing and stabilization

---

### FastAPI Backend (Next Phase)

- Teacher authentication
- Start and stop attendance sessions via web interface
- Live attendance count
- View present students
- Download CSV reports
- Student enrollment through web interface

FastAPI integration begins immediately after the core recognition pipeline is stable.

---

### Raspberry Pi Deployment Phase

- GPIO button handling
- LCD display integration
- LED status indicators
- Camera performance optimization
- Auto-start on boot using systemd
- Watchdog-based auto-restart mechanism

---

## Core Architecture

```
Camera → Face Detection → Embedding Extraction → Cosine Matching
                              ↓
                        Blink Liveness Check
                              ↓
                       Attendance Engine
                              ↓
                         PostgreSQL
                              ↓
                        FastAPI Backend
```

---

## Technology Stack

- Python 3.10
- InsightFace (`buffalo_sc`)
- ONNX Runtime (CPU)
- OpenCV
- NumPy
- PostgreSQL
- FastAPI (Next Phase)

---

## Target Performance

- 2–3 seconds per student
- 80 students processed in under 13 minutes
- Fully offline operation
- Designed for Raspberry Pi 4 (CPU-only execution)

---

## Current Focus

Complete blink detection, integrate it into the core attendance pipeline, stabilize the system, and then proceed to backend development.
