# Smart Attendance System – Raspberry Pi 4

Offline, portable face-recognition-based attendance system.

Students press a button, blink, and get marked present.  
No internet connection required.

---

## What Makes This Different

Most attendance systems require:
- Active student participation (QR scanning, manual marking)
- Internet connectivity
- Expensive hardware
- IT support for deployment

**This system:**
- Passively verifies presence through face recognition + liveness detection
- Works completely offline (local database, no cloud)
- Costs less (Raspberry Pi 4 + webcam + components)
- Student-operated (press button → blink → done)
- Teacher controls remotely via web dashboard

---

## How It Works

### Student Flow (5–7 seconds)
1. Press button on device
2. Look at camera
3. Blink when prompted (liveness check)
4. LCD shows: "John Doe - Marked Present!"
5. Pass device to next student

### Teacher Flow
- Start session from web dashboard (laptop/phone)
- Students mark themselves using the device
- View live attendance count
- End session and download CSV report

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

**Core Recognition:**
- InsightFace (`buffalo_sc` model) – CPU-optimized face recognition
- ONNX Runtime (CPU execution)
- dlib – Blink detection via Eye Aspect Ratio (EAR)
- OpenCV – Frame processing

**Backend:**
- FastAPI – REST API + teacher dashboard
- PostgreSQL – Student data, attendance records, sessions
- SQLAlchemy ORM

**Hardware (Raspberry Pi):**
- GPIO – Button input, LED status indicators
- I2C LCD (16×2) – Student feedback messages
- USB Webcam (720p minimum)

**Development:**
- Python 3.10
- Tested on Windows (development), deployed on Raspberry Pi OS

---

## Target Performance

- 5-7 seconds per student
- 80 students processed in under 15 minutes
- Fully offline operation
- Designed for Raspberry Pi 4 (CPU-only execution)

---

### In Progress
- Anti-spoofing enhancement (currently: blink + face verification)
- Email/SMS notifications
- Hardware integration (GPIO, LCD, LEDs)


## Anti-Spoofing Strategy

**Current Implementation:**
1. **Blink detection** – Defeats printed photos
2. **Face verification during blink** – Prevents swap attacks (showing photo → person blinks)

**Known Limitations:**
- Pre-recorded videos with blinks may pass (low probability in practice)
- Live video calls on screens are not fully prevented

**Exploring:**
- Challenge-response system (random actions: smile, turn head)
- Deep learning models (deferred due to Raspberry Pi constraints)

--- 

## Contributing

Currently under active development. Suggestions and feedback are welcome, especially on:
- Anti-spoofing techniques suitable for Raspberry Pi
- UI/UX improvements for teacher dashboard