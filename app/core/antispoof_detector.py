import sys, os
import numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'antispoofing'))

from app.antispoofing.anti_spoof_predict import AntiSpoofPredict
from app.antispoofing.generate_patches import CropImage
import cv2
from dotenv import load_dotenv
load_dotenv()

class AntiSpoofDetector:
    def __init__(self):
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_dir = os.path.join(base, "models", "antispoofing", "anti_spoof_models")
        detection_dir = os.path.join(base, "models", "antispoofing", "detection_model")
        os.chdir(base)  # Change to project root
        
        # Create symlink or copy detection_model to resources/
        resources_dir = os.path.join(base, "resources")
        os.makedirs(resources_dir, exist_ok=True)
        
        # Copy detection model to where it expects
        import shutil
        dest = os.path.join(resources_dir, "detection_model")
        if not os.path.exists(dest):
            shutil.copytree(detection_dir, dest)

        self.model = AntiSpoofPredict(0)
        self.model_dir = model_dir
        self.threshold = float(os.getenv("ANTISPOOF_THRESHOLD", "0.7"))
    
    def check(self, frame, bbox):
        # Convert dlib bbox [left, top, right, bottom] to expected format
        # MiniVision expects [x, y, w, h] format
        x1, y1, x2, y2 = bbox
        bbox_formatted = [x1, y1, x2 - x1, y2 - y1]  # Convert to [x, y, width, height]

        prediction = np.zeros((1,3))
        image_cropper = CropImage()

        for model_name in os.listdir(self.model_dir):
            model_path = os.path.join(self.model_dir, model_name)

            if not model_path.endswith(".pth"):
                continue

            from app.antispoofing.utility import parse_model_name
            h_input, w_input, _, _ = parse_model_name(model_name)

            param = {
                "org_img": frame,
                "bbox": bbox_formatted,
                "scale": w_input / 80.0,   # MiniVision's default scale factor
                "out_w": w_input,
                "out_h": h_input,
                "crop": True,
            }
            img_cropped = image_cropper.crop(**param)



            pred = self.model.predict(img_cropped, model_path)
            prediction += pred

        label = np.argmax(prediction)
        score = prediction[0][label]
        
        return {"is_real": label == 1 and score >= self.threshold, "score": float(score)}