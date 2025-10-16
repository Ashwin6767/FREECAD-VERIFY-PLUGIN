# Image processing core for VerifyImagePlugin

import os
import tempfile
from typing import Optional, Tuple

import numpy as np
import cv2

try:
    import FreeCADGui
except Exception:
    FreeCADGui = None  # Allows limited testing outside FreeCAD

class ImageProcessor:
    def _largest_contour(self, contours):
        if not contours:
            return None
        return max(contours, key=cv2.contourArea)

    def generate_cad_silhouette(self):
        """Capture the current FreeCAD 3D view as a black silhouette on white and return the largest contour.
        Returns None if FreeCAD GUI is not available.
        """
        if FreeCADGui is None or getattr(FreeCADGui, 'ActiveDocument', None) is None:
            return None

        view = FreeCADGui.ActiveDocument.ActiveView

        # Save a snapshot to a temp file
        tmpdir = tempfile.mkdtemp(prefix="verify_cad_")
        out_path = os.path.join(tmpdir, "temp_cad.png")
        orig_bg = None
        restore_colors = []
        try:
            # Attempt to set a clean background if available
            try:
                orig_bg = view.getBackgroundColor()
                view.setBackgroundColor((1.0, 1.0, 1.0))  # white
            except Exception:
                orig_bg = None

            # Set all visible objects to black if possible
            try:
                doc = FreeCADGui.ActiveDocument
                for vobj in doc.listObjects():
                    try:
                        # Try to save and set shape color
                        old_color = getattr(vobj, 'ShapeColor', None)
                        if old_color is not None:
                            restore_colors.append((vobj, old_color))
                            vobj.ShapeColor = (0.0, 0.0, 0.0)
                    except Exception:
                        continue
            except Exception:
                restore_colors = []

            view.saveImage(out_path, 1920, 1080, 'White')
        finally:
            # restore colors
            try:
                for vobj, color in restore_colors:
                    try:
                        vobj.ShapeColor = color
                    except Exception:
                        pass
            except Exception:
                pass
            # restore background
            try:
                if orig_bg is not None:
                    view.setBackgroundColor(orig_bg)
            except Exception:
                pass

        img = cv2.imread(out_path)
        if img is None:
            return None
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # binary inverse: black shapes on white -> contours are white after inversion
        _, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return self._largest_contour(contours)

    def process_physical_image(self, image_path: str) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Load and process the physical photo; return (largest_contour, original_color_image)."""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
        original = img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        largest = self._largest_contour(contours)
        return largest, original

    def compare_silhouettes(self, cad_contour, physical_contour) -> float:
        if cad_contour is None or physical_contour is None:
            raise ValueError("Contours must not be None")
        score = cv2.matchShapes(cad_contour, physical_contour, cv2.CONTOURS_MATCH_I1, 0.0)
        return float(score)

    def create_overlay_image(self, original_photo: np.ndarray, cad_contour, physical_contour) -> Optional[np.ndarray]:
        if original_photo is None or cad_contour is None or physical_contour is None:
            return None

        # Compute bounding boxes
        x_p, y_p, w_p, h_p = cv2.boundingRect(physical_contour)
        x_c, y_c, w_c, h_c = cv2.boundingRect(cad_contour)
        if w_p == 0 or h_p == 0 or w_c == 0 or h_c == 0:
            return original_photo

        # Normalize cad contour to physical bbox size
        scale_x = w_p / w_c
        scale_y = h_p / h_c

        cad_contour_scaled = cad_contour.astype(np.float32)
        cad_contour_scaled[:, 0, 0] = (cad_contour_scaled[:, 0, 0] - x_c) * scale_x + x_p
        cad_contour_scaled[:, 0, 1] = (cad_contour_scaled[:, 0, 1] - y_c) * scale_y + y_p
        cad_contour_scaled = cad_contour_scaled.astype(np.int32)

        overlay = original_photo.copy()
        cv2.drawContours(overlay, [physical_contour], -1, (0, 0, 255), 2)  # red
        cv2.drawContours(overlay, [cad_contour_scaled], -1, (0, 255, 0), 2)  # green
        return overlay
