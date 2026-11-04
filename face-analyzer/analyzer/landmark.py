import mediapipe as mp
import cv2
import numpy as np
import os
from typing import Optional


class FaceLandmarkDetector:
    """Detects 478 3D facial landmarks using MediaPipe FaceLandmarker (Tasks API)."""

    # Key landmark indices for facial analysis
    LANDMARKS = {
        # Forehead / hairline
        "forehead_top": 10,
        "forehead_left": 107,
        "forehead_right": 336,

        # Eyebrows
        "brow_left_outer": 70,
        "brow_left_mid": 63,
        "brow_left_inner": 105,
        "brow_right_inner": 334,
        "brow_right_mid": 296,
        "brow_right_outer": 300,

        # Eyes
        "eye_left_outer": 33,
        "eye_left_top": 159,
        "eye_left_inner": 133,
        "eye_left_bottom": 145,
        "eye_right_outer": 263,
        "eye_right_top": 386,
        "eye_right_inner": 362,
        "eye_right_bottom": 374,

        # Nose
        "nose_bridge_top": 6,
        "nose_bridge_mid": 168,
        "nose_tip": 1,
        "nose_bottom": 2,
        "nose_left": 48,
        "nose_right": 278,
        "nose_nostril_left": 44,
        "nose_nostril_right": 274,

        # Mouth
        "mouth_left": 61,
        "mouth_right": 291,
        "mouth_top": 13,
        "mouth_bottom": 14,
        "lip_upper_top": 13,
        "lip_upper_mid": 0,
        "lip_lower_bottom": 14,
        "lip_lower_mid": 17,

        # Cheeks
        "cheek_left": 123,
        "cheek_right": 352,

        # Jaw / Chin
        "chin_tip": 152,
        "chin_left": 149,
        "chin_right": 378,
        "jaw_left_top": 234,
        "jaw_right_top": 454,
        "jaw_left_mid": 127,
        "jaw_right_mid": 356,
        "jaw_left_bottom": 162,
        "jaw_right_bottom": 389,

        # Face outline
        "face_left": 234,
        "face_right": 454,
        "face_top": 10,
        "face_bottom": 152,

        # Ear area (approximation)
        "ear_left": 127,
        "ear_right": 356,
    }

    def __init__(self):
        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions

        # Download model if not present
        model_path = os.path.join(os.path.dirname(__file__), "face_landmarker.task")
        if not os.path.exists(model_path):
            import urllib.request
            url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
            urllib.request.urlretrieve(url, model_path)

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.landmarker = FaceLandmarker.create_from_options(options)

    def detect(self, image_path: str) -> Optional[dict]:
        """
        Detect face landmarks from an image file.
        Returns dict with 'landmarks' (dict of named points), 'raw_landmarks' (array),
        'image_size' (h, w), or None if no face detected.
        """
        img = cv2.imread(image_path)
        if img is None:
            return None

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w = img.shape[:2]

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        result = self.landmarker.detect(mp_image)

        if not result.face_landmarks:
            return None

        face_landmarks = result.face_landmarks[0]

        # Extract all landmark positions
        raw = np.array(
            [(lm.x * w, lm.y * h, lm.z * w) for lm in face_landmarks],
            dtype=np.float64,
        )

        # Build named landmark dict
        named = {}
        for name, idx in self.LANDMARKS.items():
            if idx < len(raw):
                named[name] = raw[idx]

        return {
            "landmarks": named,
            "raw_landmarks": raw,
            "image_size": (h, w),
        }

    def distance(self, p1: np.ndarray, p2: np.ndarray) -> float:
        """Euclidean distance between two points."""
        return float(np.linalg.norm(p1[:2] - p2[:2]))

    def midpoint(self, p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
        """Midpoint between two points."""
        return (p1 + p2) / 2

    def angle_between(self, p1: np.ndarray, vertex: np.ndarray, p2: np.ndarray) -> float:
        """Angle in degrees at vertex between p1-vertex-p2."""
        v1 = p1[:2] - vertex[:2]
        v2 = p2[:2] - vertex[:2]
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        return float(np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0))))
