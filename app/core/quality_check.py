import cv2
import numpy as np

class QualityChecker:
  def __init__(self):
    self.blur_threshold = 50.0
    self.brightness_max = 200
    self.brightness_min = 50

  def check_blur(self, image: np.ndarray) -> dict:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = laplacian.var()

    is_sharp = variance > self.blur_threshold

    return {
      "passed": is_sharp,
      "score": variance,
      "reason": None if is_sharp else "Image too blurry"
    }
  

  def check_brightness(self, image: np.ndarray) -> dict:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray)
        
        too_dark = avg_brightness < self.brightness_min
        too_bright = avg_brightness > self.brightness_max
        
        passed = not (too_dark or too_bright)
        
        reason = None
        if too_dark:
            reason = "Too dark"
        elif too_bright:
            reason = "Too bright"
        
        return {
            "passed": passed,
            "score": avg_brightness,
            "reason": reason
        }

  def check_all(self, image: np.ndarray) -> dict:
        results = {
            "blur": self.check_blur(image),
            "brightness": self.check_brightness(image)
        }
        
        all_passed = all(check["passed"] for check in results.values())
        failures = [check["reason"] for check in results.values() if not check["passed"]]
        
        return {
            "passed": all_passed,
            "checks": results,
            "failures": failures
        }