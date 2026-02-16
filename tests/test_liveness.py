import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from app.core.liveness_detection import LivenessDetector

detector = LivenessDetector()
cap = cv2.VideoCapture(0)

print("Blink detection test - press Q to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    result = detector.process_frame(frame)

    cv2.putText(frame, f"EAR: {result['ear']:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame, f"Blinks: {result['blink_count']}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame, "CLOSED" if result['eye_closed'] else "OPEN", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255) if result['eye_closed'] else (0, 255, 0), 2)

    cv2.imshow('Liveness Test', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()