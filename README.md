# Smart Attendance (Pi-based)

An IoT-based attendance system that tries to remove the need for manual marking or QR scanning.

Instead of asking students to actively mark attendance, the system passively verifies presence using proximity and device-based identification.

> This project is currently under development.

---

##  What this does

- Automatically detects student presence  
- Removes need for QR codes / manual input  
- Uses Raspberry Pi as a central node  
- Combines proximity + device identity for verification  

---

##  Idea

Most attendance systems:
- rely on QR codes  
- or require manual interaction  
- or are easy to fake  

This project tries a different approach:

> "Attendance should happen automatically if you're actually there."

The system uses:
- BLE / WiFi signals  
- device-based identification  
- time + proximity validation  

to decide whether a student is present or not.

---

##  How it works (high-level)

1. Raspberry Pi acts as a beacon / monitor  
2. Student devices broadcast or respond with identifiers  
3. System checks:
   - proximity (RSSI / signal strength)
   - timing consistency
   - device validity  
4. Attendance is marked only if conditions match  

---

##  Tech Stack

- Raspberry Pi  
- Node.js / Python (depending on implementation)  
- BLE (Bluetooth Low Energy)  
- WiFi-based detection  
- Backend logic for validation  

*(still evolving as system design improves)*

---

##  Running (WIP)

Setup instructions will be added once the system stabilizes.

---

##  Current Status

Work in progress.

Things being built / improved:
- BLE token system  
- device registration flow  
- validation logic (false positives handling)  
- backend structure  
- basic UI (teacher side)  

---

##  Future Plans

- Teacher dashboard (start/stop sessions)  
- Better anti-proxy detection  
- Logging + analytics  
- Multi-class support  
- Mobile-side integration  

---

##  Challenges

- Handling false positives  
- Signal fluctuations (RSSI instability)  
- Preventing proxy attendance  
- Battery / performance constraints  

---

##  Contributing

Still early stage, but ideas and discussions are welcome.

---
