from __future__ import annotations
import math
from pathlib import Path
import cv2
import numpy as np

try:
    import mediapipe as mp
    _MP_AVAILABLE = True
except Exception:
    mp = None
    _MP_AVAILABLE = False

# MediaPipe Face Mesh indices. Measurements are normalized by inter-ocular distance.
P = {
    "forehead": 10, "chin": 152, "left_cheek": 234, "right_cheek": 454,
    "left_eye_outer": 33, "left_eye_inner": 133, "right_eye_inner": 362, "right_eye_outer": 263,
    "left_eye_top": 159, "left_eye_bottom": 145, "right_eye_top": 386, "right_eye_bottom": 374,
    "nose_tip": 1, "nose_left": 98, "nose_right": 327, "nose_bridge_top": 168,
    "nose_base": 2, "mouth_left": 61, "mouth_right": 291, "upper_lip": 13, "lower_lip": 14,
    "left_brow": 70, "right_brow": 300, "left_jaw": 172, "right_jaw": 397,
    "left_midface": 123, "right_midface": 352
}

def _dist(a, b):
    return float(np.linalg.norm(np.asarray(a) - np.asarray(b)))

class FaceEngine:
    def __init__(self):
        self.mesh = None
        if _MP_AVAILABLE:
            try:
                self.mesh = mp.solutions.face_mesh.FaceMesh(
                    static_image_mode=True, max_num_faces=2, refine_landmarks=True,
                    min_detection_confidence=0.55
                )
            except Exception:
                self.mesh = None

    @property
    def ready(self):
        return self.mesh is not None

    def analyze(self, image_bytes: bytes):
        arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("The uploaded file is not a readable image.")
        h, w = image.shape[:2]
        if min(w, h) < 240:
            raise ValueError("Image is too small. Upload an image at least 240 pixels on its shortest side.")
        if self.mesh is None:
            raise RuntimeError("Face landmark model is unavailable. Install backend dependencies and restart.")
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = self.mesh.process(rgb)
        faces = result.multi_face_landmarks or []
        if len(faces) == 0:
            raise ValueError("No face detected. Upload a clear, front-facing photo.")
        if len(faces) > 1:
            raise ValueError("More than one face detected. Upload a photo containing one person.")
        pts = np.array([[lm.x * w, lm.y * h, lm.z * w] for lm in faces[0].landmark], dtype=np.float32)
        # normalize x/y using inter-eye distance; keep z relative to image width
        eye_span = _dist(pts[P["left_eye_outer"], :2], pts[P["right_eye_outer"], :2])
        if eye_span < 5:
            raise ValueError("Face landmarks are unreliable. Try a clearer, more frontal photo.")
        center = (pts[P["left_eye_outer"]] + pts[P["right_eye_outer"]]) / 2
        norm = pts.copy()
        norm[:, :2] = (pts[:, :2] - center[:2]) / eye_span
        norm[:, 2] = (pts[:, 2] - center[2]) / eye_span
        brightness = float(np.mean(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)))
        blur = float(cv2.Laplacian(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var())
        pose_proxy = abs(float(norm[P["left_eye_outer"], 0] + norm[P["right_eye_outer"], 0]))
        quality = {
            "width": w, "height": h, "brightness": round(brightness, 1),
            "blur_variance": round(blur, 1),
            "warnings": []
        }
        if brightness < 45 or brightness > 220: quality["warnings"].append("Lighting may affect measurements.")
        if blur < 25: quality["warnings"].append("Image may be blurry.")
        if eye_span / w < 0.12: quality["warnings"].append("Face occupies a small part of the image.")
        features = self._features(norm)
        confidence = 0.85
        if blur < 25: confidence -= 0.2
        if brightness < 45 or brightness > 220: confidence -= 0.1
        return {"features": features, "confidence": max(0.15, confidence),
                "quality": quality, "landmarks": norm}

    def _features(self, q):
        def xy(k): return q[P[k], :2]
        def d(a,b): return _dist(xy(a),xy(b))
        def ratio(a,b): return d(*a) / max(d(*b), 1e-6)
        face_w = d("left_cheek","right_cheek")
        face_h = d("forehead","chin")
        eye_w_l = d("left_eye_outer","left_eye_inner")
        eye_w_r = d("right_eye_inner","right_eye_outer")
        eye_h_l = d("left_eye_top","left_eye_bottom")
        eye_h_r = d("right_eye_top","right_eye_bottom")
        nose_w = d("nose_left","nose_right")
        nose_len = d("nose_bridge_top","nose_base")
        mouth_w = d("mouth_left","mouth_right")
        lip_h = d("upper_lip","lower_lip")
        jaw_w = d("left_jaw","right_jaw")
        cheek_w = d("left_midface","right_midface")
        thirds = [
            d("forehead","left_brow"),
            d("left_brow","nose_base"),
            d("nose_base","chin")
        ]
        thirds = np.asarray(thirds, dtype=float)
        thirds = thirds / max(float(thirds.sum()), 1e-6)
        eye_tilt_l = math.degrees(math.atan2(xy("left_eye_inner")[1]-xy("left_eye_outer")[1], xy("left_eye_inner")[0]-xy("left_eye_outer")[0]))
        eye_tilt_r = math.degrees(math.atan2(xy("right_eye_outer")[1]-xy("right_eye_inner")[1], xy("right_eye_outer")[0]-xy("right_eye_inner")[0]))
        sym = []
        for a,b in [("left_eye_outer","right_eye_outer"),("left_eye_inner","right_eye_inner"),("left_cheek","right_cheek"),("left_jaw","right_jaw")]:
            sym.append(abs(float(xy(a)[1]-xy(b)[1])))
        return {
            "face_width": [face_w], "face_height": [face_h], "face_ratio": [face_w/max(face_h,1e-6)],
            "symmetry_profile": sym,
            "jaw_width": [jaw_w], "chin_width": [d("left_jaw","right_jaw")*0.45],
            "lower_face_height": [d("nose_base","chin")], "cheek_width": [cheek_w],
            "midface_height": [d("left_brow","nose_base")],
            "thirds": thirds.tolist(), "structure_vector": [face_w/max(face_h,1e-6), jaw_w/max(face_w,1e-6), nose_w/max(face_w,1e-6)],
            "eye_shape_left": [eye_w_l/max(eye_h_l,1e-6)], "eye_shape_right": [eye_w_r/max(eye_h_r,1e-6)],
            "eye_spacing": [d("left_eye_inner","right_eye_inner")/max((eye_w_l+eye_w_r)/2,1e-6)],
            "eye_size": [eye_w_l/max(face_w,1e-6), eye_w_r/max(face_w,1e-6), eye_h_l/max(face_h,1e-6), eye_h_r/max(face_h,1e-6)],
            "eye_tilt": [eye_tilt_l, eye_tilt_r],
            "eye_symmetry": [abs(eye_w_l-eye_w_r)/max((eye_w_l+eye_w_r)/2,1e-6), abs(eye_h_l-eye_h_r)/max((eye_h_l+eye_h_r)/2,1e-6)],
            "brow_eye_gap": [d("left_brow","left_eye_top")/max(face_h,1e-6), d("right_brow","right_eye_top")/max(face_h,1e-6)],
            "nose_length": [nose_len/max(face_h,1e-6)], "nose_width": [nose_w/max(face_w,1e-6)],
            "nose_bridge": [d("nose_bridge_top","nose_tip"), nose_w/max(face_w,1e-6)],
            "nose_tip": [d("nose_tip","nose_base"), nose_w/max(face_w,1e-6)],
            "mouth_width": [mouth_w/max(face_w,1e-6)],
            "lip_proportions": [mouth_w/max(face_w,1e-6), lip_h/max(mouth_w,1e-6)],
            "lip_ratio": [max(d("upper_lip","nose_base"),1e-6)/max(d("lower_lip","chin"),1e-6)],
            "mouth_symmetry": [abs(float(xy("mouth_left")[1]-xy("mouth_right")[1]))/max(face_h,1e-6)],
            "forehead_height": [d("forehead","left_brow")/max(face_h,1e-6)],
            "brow_shape": [xy("left_brow")[1], xy("right_brow")[1]],
            "alignment": [abs(float(xy("nose_tip")[0])), abs(float((xy("mouth_left")[0]+xy("mouth_right")[0])/2))],
            "balance": [eye_w_l/max(face_w,1e-6), nose_w/max(face_w,1e-6), mouth_w/max(face_w,1e-6)]
        }
