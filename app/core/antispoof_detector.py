import sys, os
import numpy as np
import cv2
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'antispoofing'))

from app.antispoofing.anti_spoof_predict import AntiSpoofPredict
from app.antispoofing.generate_patches import CropImage
from app.antispoofing.utility import parse_model_name


def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


class AntiSpoofDetector:
    def __init__(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.model_dir = os.path.join(base, "models", "antispoofing", "anti_spoof_models")
        detection_dir = os.path.join(base, "models", "antispoofing", "detection_model")

        os.chdir(base)

        # Copy detection model to resources/ if needed
        import shutil
        resources_dir = os.path.join(base, "resources")
        os.makedirs(resources_dir, exist_ok=True)
        dest = os.path.join(resources_dir, "detection_model")
        if not os.path.exists(dest):
            shutil.copytree(detection_dir, dest)

        self.model = AntiSpoofPredict(0)
        self.image_cropper = CropImage()

        # Threshold on averaged real-class probability (0.0 to 1.0)
        # 0.6 is safer than 0.7 — reduces false positives on Pi camera
        self.threshold = float(os.getenv("ANTISPOOF_THRESHOLD", "0.60"))

        # Collect valid model paths once at init
        self.model_paths = [
            os.path.join(self.model_dir, f)
            for f in os.listdir(self.model_dir)
            if f.endswith(".pth")
        ]
        if not self.model_paths:
            raise RuntimeError(f"No .pth models found in {self.model_dir}")

    def check(self, frame, bbox) -> dict:
        """
        frame: BGR numpy array (full frame)
        bbox: (x1, y1, x2, y2) — same format InsightFace gives you

        Returns:
            {
                "is_real": bool,
                "real_prob": float,   # averaged real-class probability [0..1]
                "scores_per_model": list  # for debugging
            }
        """
        x1, y1, x2, y2 = bbox
        bbox_xywh = [x1, y1, x2 - x1, y2 - y1]

        per_model_real_probs = []

        for model_path in self.model_paths:
            model_name = os.path.basename(model_path)

            try:
                h_input, w_input, model_type, scale = parse_model_name(model_name)
            except Exception as e:
                print(f"[AntiSpoof] Could not parse model name {model_name}: {e}")
                continue

            # scale comes directly from the filename (e.g. 2.7 or 4.0)
            # This is the key fix — don't recompute it
            param = {
                "org_img": frame,
                "bbox": bbox_xywh,
                "scale": scale,
                "out_w": w_input,
                "out_h": h_input,
                "crop": True,
            }

            try:
                img_cropped = self.image_cropper.crop(**param)
                raw_pred = self.model.predict(img_cropped, model_path)  # shape (1, 3)
                probs = softmax(raw_pred[0])  # convert to probabilities
                real_prob = float(probs[1])   # index 1 = real class
                per_model_real_probs.append(real_prob)
            except Exception as e:
                print(f"[AntiSpoof] Model {model_name} failed: {e}")
                continue

        if not per_model_real_probs:
            # No model ran successfully — fail open or closed based on your preference
            # Failing CLOSED (assume spoof) is safer for attendance
            print("[AntiSpoof] WARNING: No models produced output. Treating as spoof.")
            return {"is_real": False, "real_prob": 0.0, "scores_per_model": []}

        avg_real_prob = float(np.mean(per_model_real_probs))
        is_real = avg_real_prob >= self.threshold

        return {
            "is_real": is_real,
            "real_prob": round(avg_real_prob, 4),
            "scores_per_model": [round(p, 4) for p in per_model_real_probs]
        }